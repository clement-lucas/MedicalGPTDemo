from lib.sqlconnector import SQLConnector
from parser.doctorsnoteparser import DoctorsNoteParser as DNP
from lib.soapsummarizer import SOAPSummarizer
from lib.tokencounter import TokenCounter
from lib.gptconfigmanager import GPTConfigManager
from lib.laptimer import LapTimer
import math
class SOAPManager:
    _soap_by_date_list = []
    _soap_prefix = "\n以下は医師の書いた SOAP です。\n\n"

    @staticmethod
    def _get_records_of_the_day(target, soap_record):
        record_of_the_day = ""
        if target.find('S') >= 0:
            if soap_record.S != "":
                record_of_the_day = ''.join([record_of_the_day, "S：", soap_record.S, "\n\n"])
        if target.find('O') >= 0:
            if soap_record.O != "":
                record_of_the_day = ''.join([record_of_the_day, "O：", soap_record.O, "\n\n"])
        if target.find('A') >= 0:
            if soap_record.A != "":
                record_of_the_day = ''.join([record_of_the_day, "A：", soap_record.A, "\n\n"])
        if target.find('P') >= 0:
            if soap_record.P != "":
                record_of_the_day = ''.join([record_of_the_day, "P：", soap_record.P, "\n\n"])
        if target.find('B') >= 0:
            if soap_record.B != "":
                record_of_the_day = ''.join([record_of_the_day, "＃：", soap_record.B, "\n\n"])
        # print(record_of_the_day)
        return record_of_the_day
    
    def SOAP(self, 
             target: str, 
             get_original: bool = False):
        # print("SOAP の件数：" + str(len(self._soap_by_date_list)))
        # target には、S, O, A, P, B(PLOBLEM) のいずれかを指定する。
        # 指定された target に対応する SOAP+B を返却する。
        # SOAP+B が存在しない場合は、空文字を返却する。
        target = target.upper()
        records = ""

        timer = LapTimer()
        timer.start("SOAP 連結処理")
        for soap_by_date in self._soap_by_date_list:
            record_of_the_day = SOAPManager._get_records_of_the_day(target, soap_by_date[1])
            if record_of_the_day == "":
                continue
            records = ''.join([records, "記入日：", soap_by_date[0], "\n\n", record_of_the_day, "\n"])
        timer.stop()

        if get_original:
            return ''.join([SOAPManager._soap_prefix, records]), 0, 0, 0, ""

        timer.start("TokenCount 処理")
        max_tokens_for_soap_contents = max_tokens_for_soap - self._prefix_tokens
        # print("max_tokens_for_soap_contents:" + str(max_tokens_for_soap_contents))
        summarizer = SOAPSummarizer(self._gptconfigmanager, self._engine)
        contents_token = TokenCounter.count(records, self._model_name_for_tiktoken)
        print("contents_token:" + str(contents_token))
        timer.stop()

        # Ptn1: 作成された SOAP が SOAP Token 上限に収まる場合
        #       そのまま返却する。
        if contents_token <= max_tokens_for_soap_contents:
            # print("Ptn1: SOAP Token 上限に収まる場合")
            return ''.join([SOAPManager._soap_prefix, records]), 0, 0, 0, ""
        
        # Ptn2: 作成された SOAP が SOAP Token 上限を超え、且つ、一回の要約で収まる場合
        #       要約して返却する。
        # print("max_tokens_for_soap_contents" + str(max_tokens_for_soap_contents))
        # print("contents_token" + str(contents_token))
        # print("summarizer.capacity_for_befor_and_after_summarize_text" + str(summarizer.capacity_for_befor_and_after_summarize_text))
        # print("max_tokens_for_soap" + str(max_tokens_for_soap))

        timer.start("要約処理")

        if max_tokens_for_soap_contents < contents_token  and \
            contents_token <= summarizer.capacity_for_befor_and_after_summarize_text - max_tokens_for_soap:
            # print("Ptn2: SOAP Token 上限を超え、且つ、一回の要約で収まる場合")
            # 退院時サマリ作成に使用するモデルよりもはるかに大きい Token 上限を持つ要約用モデルを使用するなどしない限り、
            # ここに入ることはない。
            # なぜならば、退院時サマリ作成のために GPT に送信する時点で Token 超を over するならば、
            # 要約用モデルに送信してもやはり Token 超するからである。
            # 要約時の GPT 応答用の領域は、退院時サマリ作成時よりも大きく確保することが一般的に考えられ、
            # そうすると、同じトークン上限を持つモデルを使っている場合、
            # 要約前の文書として渡せるトークン数が、退院時サマリ作成時に渡せる SOAP のトークン数よりも大きくなることは考えられない。
            summary = summarizer.summarize(records, max_tokens_for_soap_contents)
            return ''.join([SOAPManager._soap_prefix, summary[0]]), summary[1].completion_tokens, summary[1].prompt_tokens, summary[1].total_tokens, summary[2]

        timer.stop()        

        timer.start("Ptn3")
        # Ptn3: 作成された SOAP が SOAP Token 上限を超え、且つ、一回の要約では収まらない場合
        #       段階的に要約して返却する。
        # print("Ptn3: SOAP Token 上限を超え、且つ、一回の要約では収まらない場合")
        summary = self._summarize(summarizer, target, max_tokens_for_soap_contents)
        timer.stop()

        return summary[0], summary[1], summary[2], summary[3], summary[4]

    # 段階的に要約する。
    def _summarize(self, summarizer:SOAPSummarizer, target:str, max_tokens_for_soap_contents:int):
        
        # 要約前のテキストとして渡せる最大トークン数を計算する。
        capacity_for_befor_text = summarizer.capacity_for_befor_and_after_summarize_text / (1 + self._compressibility_for_summary)
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

        # 段階的要約の開始
        for soap_by_date in self._soap_by_date_list:
            record_of_the_day = SOAPManager._get_records_of_the_day(target, soap_by_date[1])
            if record_of_the_day == "":
                continue
            record_of_the_day = ''.join(["記入日：", soap_by_date[0], "\n\n", record_of_the_day, "\n"])

            # 今見ているレコードを足してなお、要約バッファに入りきるか調べる。
            if TokenCounter.count(''.join([summarize_buffer, record_of_the_day]), 
                    self._model_name_for_tiktoken) > capacity_for_befor_text:
                # print("要約バッファに入りきらないので、要約して確保する。")
                # これ以上要約バッファに入りきらないので、要約して確保する。
                summarize_token = expected_summarized_token_num
                record_of_the_day_token = TokenCounter.count(record_of_the_day, self._model_name_for_tiktoken)
                if summarize_token > capacity_for_befor_text - record_of_the_day_token:
                    summarize_token = capacity_for_befor_text - record_of_the_day_token
                summary = summarizer.summarize(summarize_buffer, summarize_token)
                summarize_buffer = ''.join([summary[0], "\n\n"])
                # print("summarize_buffer1:" + summarize_buffer)
                completion_tokens += summary[1].completion_tokens
                prompt_tokens += summary[1].prompt_tokens
                total_tokens += summary[1].total_tokens
                summarize_log = ''.join([summarize_log, summary[2]])

            # 今見ているレコードを要約バッファに追加する。
            summarize_buffer = ''.join([summarize_buffer, record_of_the_day])
            # print("summarize_buffer2:" + summarize_buffer)

        # 最後まで見終わったので、SOAP Token 上限に収まるか調べて、収まる場合はそのまま返す。
        contents_token = TokenCounter.count(summarize_buffer, self._model_name_for_tiktoken)
        # print("contents_token:" + str(contents_token))
        if contents_token <= max_tokens_for_soap_contents:
            # print("最後まで見終わり。SOAP Token 上限に収まるので、そのまま返す。"+str(contents_token)+":"+str(max_tokens_for_soap_contents))
            return ''.join([SOAPManager._soap_prefix, summarize_buffer]), completion_tokens, prompt_tokens, total_tokens, summarize_log

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
        summarize_log = ''.join([summarize_log, summary[2]])
        return ''.join([SOAPManager._soap_prefix, summary[0]]), completion_tokens, prompt_tokens, total_tokens, summarize_log

    def __init__(self, 
                gptconfigmanager:GPTConfigManager, 
                patient_code: str, 
                engine: str,
                max_tokens_for_soap: int):
        timer = LapTimer()
        timer.start("SQL SELECT 処理")
        
        self._gptconfigmanager = gptconfigmanager
        self._model_name_for_tiktoken = gptconfigmanager.get_value("MODEL_NAME_FOR_TIKTOKEN")
        self._engine = engine
        self._prefix_tokens = TokenCounter.count(SOAPManager._soap_prefix, self._model_name_for_tiktoken)
        self._compressibility_for_summary = float(gptconfigmanager.get_value("COMPRESSIBILITY_FOR_SUMMARY"))

        # SQL Server に接続する
        cnxn = SQLConnector.get_conn()
        cursor = cnxn.cursor()

        # TODO 日付等の各種取得条件は適宜実装のこと
        select_datax_sql = """SELECT EXTBDH1.DOCDATE, EXTBDC1.DOC_DATAX FROM EXTBDC1 
            INNER JOIN EXTBDH1 
            ON EXTBDC1.DOC_NO = EXTBDH1.DOC_NO
            AND EXTBDH1.DOC_K = ? 
            AND EXTBDH1.ACTIVE_FLG = 1 
            AND EXTBDC1.ACTIVE_FLG = 1 
            AND EXTBDH1.PID = ?
            ORDER BY EXTBDH1.DOCDATE DESC"""

        # 医師記録の取得
        cursor.execute(select_datax_sql,'MD01', patient_code)
        rows = cursor.fetchall() 
        
        self._soap_by_date_list = []
        # print("SOAP の取得件数：" + str(len(rows)))
        for i in range(200):
            for row in rows:
                datetime = SOAPManager.get_datetime(row[0])
                # XML のまま GPT に投げても解釈してくれないこともないが、
                # XML のままだとトークン数をとても消費してしまうので、
                # XML を解釈して、平文に変換する。
                soap = DNP(row[1])
                self._soap_by_date_list.append((datetime, soap))
        
        timer.stop()

        records = self.SOAP("SOAP", False)
        contents_token = TokenCounter.count(records, self._model_name_for_tiktoken)
        max_tokens_for_soap_contents = max_tokens_for_soap - self._prefix_tokens
        print("contents_token:" + str(contents_token))
        # 作成された SOAP が SOAP Token 上限に収まる場合、要約を行わない。
        if contents_token <= max_tokens_for_soap_contents:
            return
        
        # 収まらない場合は、要約を行う。
        # まずは、各セクションごとの比率を計算する。
        # 比率の計算は概算で良いので、"S:"というセクション名や日付を除いた文字列の長さで計算する。
        # （処理時間をなるべく削減するため）
        for soap_by_date in self._soap_by_date_list:
            if (soap_by_date[1].S != ""):
                s = ''.join([s, "記入日：", soap_by_date[0], "\n\n", soap_by_date[1].S, "\n\n"])
            if (soap_by_date[1].O != ""):
                o = ''.join([o, "記入日：", soap_by_date[0], "\n\n", soap_by_date[1].O, "\n\n"])
            if (soap_by_date[1].A != ""):
                a = ''.join([a, "記入日：", soap_by_date[0], "\n\n", soap_by_date[1].A, "\n\n"])
            if (soap_by_date[1].P != ""):
                p = ''.join([p, "記入日：", soap_by_date[0], "\n\n", soap_by_date[1].P, "\n\n"])
            if (soap_by_date[1].B != ""):
                b = ''.join([b, "記入日：", soap_by_date[0], "\n\n", soap_by_date[1].B, "\n\n"])
            
        s_tokens = TokenCounter.count(s, self._model_name_for_tiktoken)
        o_tokens = TokenCounter.count(o, self._model_name_for_tiktoken)
        a_tokens = TokenCounter.count(a, self._model_name_for_tiktoken)
        p_tokens = TokenCounter.count(p, self._model_name_for_tiktoken)
        b_tokens = TokenCounter.count(b, self._model_name_for_tiktoken)
        total_tokens = s_tokens + o_tokens + a_tokens + p_tokens + b_tokens
        s_ratio = s_tokens / total_tokens
        o_ratio = o_tokens / total_tokens
        a_ratio = a_tokens / total_tokens
        p_ratio = p_tokens / total_tokens
        b_ratio = b_tokens / total_tokens

        # 各セクションに割り当てられる max token 数を計算する。
        max_tokens_for_soap_contents_s = math.floor(max_tokens_for_soap_contents * s_ratio)
        max_tokens_for_soap_contents_o = math.floor(max_tokens_for_soap_contents * o_ratio)
        max_tokens_for_soap_contents_a = math.floor(max_tokens_for_soap_contents * a_ratio)
        max_tokens_for_soap_contents_p = math.floor(max_tokens_for_soap_contents * p_ratio)
        max_tokens_for_soap_contents_b = math.floor(max_tokens_for_soap_contents * b_ratio)

        # 要約はキャッシュしておく
        # 最終カルテ記載日を記録しておく



        
    # yyyyMMddHHMISS -> yyyy/MM/dd HH:MI:SS に変換する関数
    # 例）20140224095813 -> 2014/02/24 09:58:13
    @staticmethod
    def get_datetime(org: str):
        strdate = str(org)
        if len(strdate) != 14:
            return strdate
        year = strdate[0:4]
        month = strdate[4:6]
        day = strdate[6:8]
        hour = strdate[8:10]
        minute = strdate[10:12]
        second = strdate[12:14]
        return ''.join([year, "/", month, "/", day, " ", hour, ":", minute, ":", second])
    
