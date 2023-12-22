# 削除予定

from lib.sqlconnector import SQLConnector
from lib.laptimer import LapTimer
from lib.datetimeconverter import DateTimeConverter
from lib.tokencounter import TokenCounter
from lib.gptconfigmanager import GPTConfigManager
from lib.soapsummarizer import SOAPSummarizer
from lib.soapexception import SoapException
import math

USE_RANGE_KIND_ALL = 0
USE_RANGE_KIND_HOSPITALIZATION = 1
USE_RANGE_KIND_DISCHARGE = 2
SOAP_PREFIX = "\n以下は医師の書いた SOAP です。\n\n"

class SOAPManager:

    def __init__(self, 
        sql_connector:SQLConnector,
        department_code: str,
        pid: str,
        gptconfigmanager: GPTConfigManager,
        gpt_deployment: str
                 ):
        self._sql_connector = sql_connector
        self._department_code = department_code
        self._pid = pid
        self._gptconfigmanager = gptconfigmanager
        model_name_for_tiktoken = self._gptconfigmanager.get_value("MODEL_NAME_FOR_TIKTOKEN")
        self._prefix_tokens = TokenCounter.count(SOAP_PREFIX, model_name_for_tiktoken)
        self._gpt_deployment = gpt_deployment
        with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
            # サマリ管理テーブルから、入院日と退院日を取得する。
            select_hospitalization_sql = """
                SELECT NOW_DATE, TAIIN_DATE
                FROM ECSCSM_ECTBSM
                WHERE PID = ?
                AND SUM_SYUBETU = '01'
                AND NOW_KA = ?
                AND SUM_SEQ = (
                SELECT MAX(SUM_SEQ)
                FROM ECSCSM_ECTBSM
                WHERE PID = ?
                AND SUM_SYUBETU = '01'
                AND NOW_KA = ?
                );
                """
            cursor.execute(select_hospitalization_sql, 
                           pid, department_code, 
                           pid, department_code)
            rows = cursor.fetchall() 
            if len(rows) < 1:
                err_msg = "サマリ管理テーブルから入院日と退院日を取得できませんでした。pid:" + str(pid) + ", now_ka:" + department_code
                print(err_msg) 
                raise Exception(err_msg)
            
            # 入院日と退院日の範囲を計算する。
            # hospitalization_date には、14桁の数値で日付時刻が格納されている。
            # 例）20140224095813

            self._hospitalization_date = rows[0][0]   # 入院日
            # print(self._hospitalization_date)
            self._hospitalization_date = DateTimeConverter.get_start_of_the_day(self._hospitalization_date)
            self._discharge_date = rows[0][1]         # 退院日
            # print(self._discharge_date)
            self._discharge_date = DateTimeConverter.get_start_of_the_day(self._discharge_date)
            self._hospitalization_date_str = DateTimeConverter.int_2_str(self._hospitalization_date, True)
            self._discharge_date_str = DateTimeConverter.int_2_str(self._discharge_date, True)

    @property
    def hospitalization_date_str(self):
        return self._hospitalization_date_str
    
    @property
    def discharge_date_str(self):
        return self._discharge_date_str

    def get_values(
        self,
        target_soap_kinds: str,
        use_range_kind: int,
        days_before_the_date_of_hospitalization_to_use: int,
        days_after_the_date_of_hospitalization_to_use: int,
        days_before_the_date_of_discharge_to_use: int,
        days_after_the_date_of_discharge_to_use: int) -> str:

        # 'SoP' -> 'sop'
        target_soap_kinds = target_soap_kinds.lower()

        # 'sop' -> ['s', 'o', 'p']
        target_soap_kinds_list = list(target_soap_kinds)

        # IN (?, ?, ?) にするために、カンマ区切りの文字列にする。
        placeholders = ', '.join('?' for _ in target_soap_kinds_list)

        timer = LapTimer()
        timer.start("SQL SELECT 処理")
        
        # 期間の計算
        absolute_range_start_date: int = 0
        absolute_range_end_date: int = 0
        if use_range_kind == USE_RANGE_KIND_ALL:
            absolute_range_start_date = self._hospitalization_date
            absolute_range_end_date = self._discharge_date
        elif use_range_kind == USE_RANGE_KIND_HOSPITALIZATION:
            absolute_range_start_date = DateTimeConverter.add_days(self._hospitalization_date, days_before_the_date_of_hospitalization_to_use * -1)
            absolute_range_end_date = DateTimeConverter.add_days(self._hospitalization_date, days_after_the_date_of_hospitalization_to_use)
        elif use_range_kind == USE_RANGE_KIND_DISCHARGE:
            absolute_range_start_date = DateTimeConverter.add_days(self._discharge_date, days_before_the_date_of_discharge_to_use * -1)
            absolute_range_end_date = DateTimeConverter.add_days(self._discharge_date, days_after_the_date_of_discharge_to_use)
        else:
            raise Exception("不正な値です。use_range_kind:" + str(use_range_kind))
        
        # 期間を0時0分0秒から23時59分59秒にする。
        absolute_range_start_date = DateTimeConverter.get_start_of_the_day(absolute_range_start_date)
        absolute_range_end_date = DateTimeConverter.get_end_of_the_day(absolute_range_end_date)

        range_str = "使用するカルテ期間：" + str(absolute_range_start_date) + "～" + str(absolute_range_end_date)
        #print(range_str)

        select_data_sql = f"""
            SELECT Id, OriginalDocNo, DocDate, SoapKind, DuplicateSourceDataId, IntermediateData
            FROM IntermediateSOAP
            WHERE (? <= DocDate AND DocDate <= ?)
                AND Pid = ? AND SoapKind IN ({placeholders}) AND IsDeleted = 0
            ORDER BY Id"""

        with self._sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
            # 中間データの取得
            cursor.execute(select_data_sql,
                           absolute_range_start_date, absolute_range_end_date, 
                           self._pid, *target_soap_kinds_list)
            rows = cursor.fetchall() 

            if len(rows) < 1:
                timer.stop()
                msg = f"中間データが取得できませんでした。pid:{self._pid}, now_ka:{self._department_code}, {range_str}, 対象 SOAP 種別:{target_soap_kinds}"
                raise SoapException(msg)

            id_list = []
            rows_include_duplicate = []  # 欠損していた重複データを補った行を格納する。
            # 芋づる式に重複データを取得する。
            for row in rows:
                # 日付が変わったら、日付を更新する。
                id = row[0]
                original_doc_no = row[1]
                doc_date = row[2]
                kind = row[3]
                duplicate_source_data_id = row[4]
                intermediateData = row[5]

                SOAPManager._get_duplicate_data_source(
                    cnxn, duplicate_source_data_id, id_list, rows_include_duplicate)

                id_list.append(id)
                rows_include_duplicate.append(row)

            now_date = -1
            original_doc_no_list = []
            not_sumarrized_soap = ""    # 要約前の SOAP
            for row in rows_include_duplicate:
                # 日付が変わったら、日付を更新する。
                id = row[0]
                original_doc_no = row[1]
                doc_date = row[2]
                kind = row[3]
                duplicate_source_data_id = row[4]
                intermediateData = row[5]

                if intermediateData is None or intermediateData == "":
                    # 重複削除した結果、中間データが空になったレコードについては、スキップする。
                    continue

                if now_date != doc_date:
                    now_date = doc_date
                    not_sumarrized_soap = ''.join([not_sumarrized_soap, "\n", DateTimeConverter.int_2_str(doc_date), "\n\n"])
                kind_upper = kind.upper()
                not_sumarrized_soap = ''.join([not_sumarrized_soap, "＃" if kind_upper == "B" else kind_upper, "：\n", intermediateData, "\n\n"])
                original_doc_no_list.append(original_doc_no)
        timer.stop()

        model_name_for_tiktoken = self._gptconfigmanager.get_value("MODEL_NAME_FOR_TIKTOKEN")
        contents_token = TokenCounter.count(not_sumarrized_soap, model_name_for_tiktoken)   # prefix を除くコンテンツ長
        max_tokens_for_soap = self.get_max_tokens_for_soap()                        # SOAP に割り当て可能なトークン数
        max_tokens_for_soap_contents = max_tokens_for_soap - self._prefix_tokens
        
        # Ptn1: 作成された SOAP が SOAP Token 上限に収まる場合
        #       そのまま返却する。
        if contents_token <= max_tokens_for_soap_contents:
            print("Ptn1: SOAP Token 上限に収まるので、要約を行わない。 Token 数: " + str(contents_token))
            not_sumarrized_soap = ''.join([SOAP_PREFIX, not_sumarrized_soap])
            return not_sumarrized_soap, id_list, \
                    original_doc_no_list, \
                    absolute_range_start_date, \
                    absolute_range_end_date, \
                    "", \
                    0, \
                    0, \
                    0, \
                    ""

        print("SOAP Token 上限に収まらないので、要約を行う。 Token 数: " + str(contents_token))            

        # Ptn2: 作成された SOAP が SOAP Token 上限を超え、且つ、一回の要約で収まる場合
        #       要約して返却する。
        # print("max_tokens_for_soap_contents" + str(max_tokens_for_soap_contents))
        # print("contents_token" + str(contents_token))
        # print("summarizer.capacity_for_befor_and_after_summarize_text" + str(summarizer.capacity_for_befor_and_after_summarize_text))
        # print("max_tokens_for_soap" + str(max_tokens_for_soap))

        timer = LapTimer()
        timer.start("要約処理")

        summarizer = SOAPSummarizer(self._gptconfigmanager, self._gpt_deployment)
        if max_tokens_for_soap_contents < contents_token  and \
            contents_token <= summarizer.capacity_for_befor_and_after_summarize_text - max_tokens_for_soap:
            print("Ptn2: SOAP Token 上限を超え、且つ、一回の要約で収まる場合")
            # 退院時サマリ作成に使用するモデルよりもはるかに大きい Token 上限を持つ要約用モデルを使用するなどしない限り、
            # ここに入ることはない。
            # なぜならば、退院時サマリ作成のために GPT に送信する時点で Token 超を over するならば、
            # 要約用モデルに送信してもやはり Token 超過するからである。
            # 要約時の GPT 応答用の領域は、退院時サマリ作成時よりも大きく確保することが一般的に考えられ、
            # そうすると、同じトークン上限を持つモデルを使っている場合、
            # 要約前の文書として渡せるトークン数が、退院時サマリ作成時に渡せる SOAP のトークン数よりも大きくなることは考えられない。
            summary = summarizer.summarize(not_sumarrized_soap, max_tokens_for_soap_contents)
            sumarrized_soap = ''.join([SOAP_PREFIX, summary[0]])
            timer.stop()
            return not_sumarrized_soap, id_list, \
                    original_doc_no_list, \
                    absolute_range_start_date, \
                    absolute_range_end_date, \
                    sumarrized_soap, \
                    summary[1].completion_tokens, \
                    summary[1].prompt_tokens, \
                    summary[1].total_tokens, \
                    summary[2]        
        # Ptn3: 作成された SOAP が SOAP Token 上限を超え、且つ、一回の要約では収まらない場合
        #       段階的に要約して返却する。
        print("Ptn3: SOAP Token 上限を超え、且つ、一回の要約では収まらない場合")
        summary = self._summarize(summarizer, rows_include_duplicate, max_tokens_for_soap_contents)
        sumarrized_soap = ''.join([SOAP_PREFIX, summary[0]])
        timer.stop()
        return not_sumarrized_soap, id_list, \
                original_doc_no_list, \
                absolute_range_start_date, \
                absolute_range_end_date, \
                sumarrized_soap, \
                summary[1], \
                summary[2], \
                summary[3], \
                summary[4]

    # 段階的に要約する。
    def _summarize(self, summarizer:SOAPSummarizer, rows_include_duplicate:[], max_tokens_for_soap_contents:int):
        
        # 要約前のテキストとして渡せる最大トークン数を計算する。
        compressibility_for_summary = float(self._gptconfigmanager.get_value("COMPRESSIBILITY_FOR_SUMMARY"))
        capacity_for_befor_text = summarizer.capacity_for_befor_and_after_summarize_text / (1 + compressibility_for_summary)
        capacity_for_befor_text = math.floor(capacity_for_befor_text)
        # print("capacity_for_befor_text:" + str(capacity_for_befor_text))

        # 要約後のテキストとして受け取る事のできる最大トークン数を計算する。
        expected_summarized_token_num = summarizer.capacity_for_befor_and_after_summarize_text - capacity_for_befor_text
        # print("expected_summarized_token_num:" + str(expected_summarized_token_num))

        completion_tokens = 0
        prompt_tokens = 0
        total_tokens = 0
        summarize_log = ""

        # 要約バッファ（要約前のテキスト）
        summarize_buffer = ""

        model_name_for_tiktoken = self._gptconfigmanager.get_value("MODEL_NAME_FOR_TIKTOKEN")

        # 段階的要約の開始
        now_date = -1
        for row in rows_include_duplicate:
            # 日付が変わったら、日付を更新する。
            doc_date = row[2]
            kind = row[3]
            intermediateData = row[5]

            if intermediateData is None or intermediateData == "":
                # 重複削除した結果、中間データが空になったレコードについては、スキップする。
                continue

            kind_upper = kind.upper()
            one_record = ''.join(["＃" if kind_upper == "B" else kind_upper, "：\n", intermediateData, "\n\n"])
            if now_date != doc_date:
                now_date = doc_date
                one_record = ''.join(["\n\n", DateTimeConverter.int_2_str(doc_date), "\n\n", one_record])

            # 今見ているレコードを足してなお、要約バッファに入りきるか調べる。
            if TokenCounter.count(summarize_buffer + one_record, 
                    model_name_for_tiktoken) > capacity_for_befor_text:
                # print("要約バッファに入りきらないので、要約して確保する。")
                # これ以上要約バッファに入りきらないので、要約して確保する。
                summarize_token = expected_summarized_token_num
                one_record_token = TokenCounter.count(one_record, model_name_for_tiktoken)
                if summarize_token > capacity_for_befor_text - one_record_token:
                    summarize_token = capacity_for_befor_text - one_record_token
                summary = summarizer.summarize(summarize_buffer, summarize_token)
                print("summarize_buffer:" + summarize_buffer)
                summarize_buffer = summary[0] + "\n\n"
                # print("summarize_buffer1:" + summarize_buffer)
                completion_tokens += summary[1].completion_tokens
                prompt_tokens += summary[1].prompt_tokens
                total_tokens += summary[1].total_tokens
                summarize_log += summary[2]
                now_date = -1

            # 今見ているレコードを要約バッファに追加する。
            summarize_buffer += one_record
            # print("summarize_buffer2:" + summarize_buffer)
        print("summarize_buffer:" + summarize_buffer)

        # 最後まで見終わったので、SOAP Token 上限に収まるか調べて、収まる場合はそのまま返す。
        contents_token = TokenCounter.count(summarize_buffer, model_name_for_tiktoken)
        # print("contents_token:" + str(contents_token))
        if contents_token <= max_tokens_for_soap_contents:
            print("最後まで見終わり。SOAP Token 上限に収まるので、そのまま返す。"+str(contents_token)+":"+str(max_tokens_for_soap_contents))
            return summarize_buffer, completion_tokens, prompt_tokens, total_tokens, summarize_log

        # 超過する場合は、最後の要約を行って返す。
        # print("最後まで見終わり。SOAP Token 上を超えるので、最後の要約を行って返す。")
        # SOAPコンテンツ長と、要約後のコンテンツ長のうち、低い方を要約後のコンテンツ長とする。
        summarize_token = max_tokens_for_soap_contents
        if max_tokens_for_soap_contents > expected_summarized_token_num: 
            summarize_token = expected_summarized_token_num

        summary = summarizer.summarize(summarize_buffer, summarize_token)
        completion_tokens += summary[1].completion_tokens
        prompt_tokens += summary[1].prompt_tokens
        total_tokens += summary[1].total_tokens
        summarize_log += summary[2]
        return summary[0], completion_tokens, prompt_tokens, total_tokens, summarize_log

    @staticmethod
    def _get_duplicate_data_source(cnxn, duplicate_source_data_id:int, id_list:[], rows_include_duplicate:[]):
        if duplicate_source_data_id is None or \
            duplicate_source_data_id < 0 or \
            duplicate_source_data_id in id_list:
            return

        # 芋づる式に重複データを取得する。
        source_data = SOAPManager._get_data_by_duplicate_source_data_id(
            cnxn, duplicate_source_data_id)
        if source_data is None:
            raise Exception("重複データが取得できませんでした。Id:" + str(duplicate_source_data_id))
        
        # 再帰的に重複データを取得する。
        id = source_data[0]
        source_duplicate_source_data_id = source_data[4]
        SOAPManager._get_duplicate_data_source(
            cnxn, source_duplicate_source_data_id, id_list, rows_include_duplicate)

        id_list.append(id)
        rows_include_duplicate.append(source_data)

    @staticmethod
    def _get_data_by_duplicate_source_data_id(cnxn, duplicate_source_data_id:int):
        with cnxn.cursor() as cursor:
            select_data_sql = """
                SELECT Id, OriginalDocNo, DocDate, SoapKind, DuplicateSourceDataId, IntermediateData
                FROM IntermediateSOAP
                WHERE Id = ? AND IsDeleted = 0
                """
            cursor.execute(select_data_sql, duplicate_source_data_id)
            rows = cursor.fetchall() 
            if len(rows) < 1:
                return None
            return rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5]

    # SOAP に割り当て可能なトークン数を計算する
    def get_max_tokens_for_soap(self):
        num_tokens_for_soap = int(self._gptconfigmanager.get_value("MAX_TOTAL_TOKENS")) - int(self._gptconfigmanager.get_value("TOKEN_NUM_FOR_QUESTION"))
        return num_tokens_for_soap

