from lib.sqlconnector import SQLConnector
from parser.doctorsnoteparser import DoctorsNoteParser as DNP
from lib.soapsummarizer import SOAPSummarizer
from lib.tokencounter import TokenCounter
from lib.gptconfigmanager import GPTConfigManager
from lib.laptimer import LapTimer
from lib.soapcachemanager import SOAPCacheManager
import math
class SOAPManager:
    _soap_by_date_list = []
    _soap_prefix = "\n以下は医師の書いた SOAP です。\n\n"

    @staticmethod
    def _get_records_of_the_day(target, soap_record, add_caption: bool = True):
        target = target.upper()
        record_of_the_day = ""
        if target.find('S') >= 0:
            if soap_record.S != "":
                record_of_the_day = ''.join([record_of_the_day, "S：" if add_caption else '', soap_record.S, "\n\n"])
        if target.find('O') >= 0:
            if soap_record.O != "":
                record_of_the_day = ''.join([record_of_the_day, "O：" if add_caption else '', soap_record.O, "\n\n"])
        if target.find('A') >= 0:
            if soap_record.A != "":
                record_of_the_day = ''.join([record_of_the_day, "A：" if add_caption else '', soap_record.A, "\n\n"])
        if target.find('P') >= 0:
            if soap_record.P != "":
                record_of_the_day = ''.join([record_of_the_day, "P：" if add_caption else '', soap_record.P, "\n\n"])
        if target.find('B') >= 0:
            if soap_record.B != "":
                record_of_the_day = ''.join([record_of_the_day, "＃：" if add_caption else '', soap_record.B, "\n\n"])
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
        if get_original or self._is_summarized == False:
            timer.start("SOAP 連結処理")
            for soap_by_date in self._soap_by_date_list:
                record_of_the_day = SOAPManager._get_records_of_the_day(target, soap_by_date[1])
                if record_of_the_day == "":
                    continue
                records = ''.join([records, "記入日：", soap_by_date[0], "\n\n", record_of_the_day, "\n"])
            timer.stop()
            return ''.join([SOAPManager._soap_prefix, records])

        records = ""

        timer.start("要約 SOAP 連結処理")
        if target.find('S') >= 0 and self._summarized_s != "":
            records = ''.join([records, self._summarized_s])
        if target.find('O') >= 0 and self._summarized_o != "":
            records = ''.join([records, self._summarized_o])
        if target.find('A') >= 0 and self._summarized_a != "":
            records = ''.join([records, self._summarized_a])
        if target.find('P') >= 0 and self._summarized_p != "":
            records = ''.join([records, self._summarized_p])
        if target.find('B') >= 0 and self._summarized_b != "":
            records = ''.join([records, self._summarized_b])
        timer.stop()

        return ''.join([SOAPManager._soap_prefix, records])

    # 段階的に要約する。
    def _summarize(self, summarizer:SOAPSummarizer, target:str, max_tokens_for_soap_contents:int, add_caption:bool = True):
        
        # print("_summarize")
        # print("target:" + target)
        # print("max_tokens_for_soap_contents:" + str(max_tokens_for_soap_contents))


        # 要約前のテキストとして渡せる最大トークン数を計算する。
        capacity_for_befor_text = summarizer.capacity_for_befor_and_after_summarize_text / (1 + self._compressibility_for_summary)
        capacity_for_befor_text = math.floor(capacity_for_befor_text)
        # print("capacity_for_befor_text:" + str(capacity_for_befor_text))

        # 要約後のテキストとして受け取る事のできる最大トークン数を計算する。
        expected_summarized_token_num = summarizer.capacity_for_befor_and_after_summarize_text - capacity_for_befor_text
        # print("expected_summarized_token_num:" + str(expected_summarized_token_num))

        # 要約の結果を格納する変数
        completion_tokens = 0
        prompt_tokens = 0
        total_tokens = 0
        summarize_log = ""

        # 要約バッファ（要約前のテキスト）
        summarize_buffer = ""

        # 段階的要約の開始
        for soap_by_date in self._soap_by_date_list:
            # print("soap_by_date:" + soap_by_date[0])
            record_of_the_day = SOAPManager._get_records_of_the_day(target, soap_by_date[1], add_caption)
            # print("record_of_the_day:" + record_of_the_day)
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
                print("summarize_log:" + summarize_log)

            # 今見ているレコードを要約バッファに追加する。
            summarize_buffer = ''.join([summarize_buffer, record_of_the_day])
            # print("summarize_buffer2:" + summarize_buffer)

        # 最後まで見終わったので、SOAP Token 上限に収まるか調べて、収まる場合はそのまま返す。
        contents_token = TokenCounter.count(summarize_buffer, self._model_name_for_tiktoken)
        # print("contents_token:" + str(contents_token))
        if contents_token <= max_tokens_for_soap_contents:
            print("最後まで見終わり。SOAP Token 上限に収まるので、そのまま返す。"+str(contents_token)+":"+str(max_tokens_for_soap_contents))
            return summarize_buffer, completion_tokens, prompt_tokens, total_tokens, summarize_log

        # 超過する場合は、最後の要約を行って返す。
        print("最後まで見終わり。SOAP Token 上を超えるので、最後の要約を行って返す。")
        # SOAPコンテンツ長と、要約後のコンテンツ長のうち、低い方を要約後のコンテンツ長とする。
        summarize_token = max_tokens_for_soap_contents
        if max_tokens_for_soap_contents > expected_summarized_token_num: 
            summarize_token = expected_summarized_token_num

        summary = summarizer.summarize(summarize_buffer, summarize_token)
        completion_tokens += summary[1].completion_tokens
        prompt_tokens += summary[1].prompt_tokens
        total_tokens += summary[1].total_tokens
        summarize_log = ''.join([summarize_log, summary[2]])
        print("summarize_log:" + summarize_log)
        return summary[0], completion_tokens, prompt_tokens, total_tokens, summarize_log

    def __init__(self, 
                sql_connector:SQLConnector,
                user_id: str,
                gptconfigmanager:GPTConfigManager, 
                patient_code: str, 
                engine: str,
                max_tokens_for_soap: int, force_original: bool = False):
        self._sql_connector = sql_connector
        self._is_summarized = False
        self._summarized_completion_tokens = 0
        self._summarized_prompt_tokens = 0
        self._summarized_total_tokens = 0
        self._summarized_log = ""
        self._summarized_s = ""
        self._summarized_o = ""
        self._summarized_a = ""
        self._summarized_p = ""
        self._summarized_b = ""

        timer = LapTimer()
        timer.start("SQL SELECT 処理")
        
        self._gptconfigmanager = gptconfigmanager
        self._model_name_for_tiktoken = gptconfigmanager.get_value("MODEL_NAME_FOR_TIKTOKEN")
        self._engine = engine
        self._prefix_tokens = TokenCounter.count(SOAPManager._soap_prefix, self._model_name_for_tiktoken)
        self._compressibility_for_summary = float(gptconfigmanager.get_value("COMPRESSIBILITY_FOR_SUMMARY"))
        self._max_tokens_for_soap = max_tokens_for_soap

        # SQL Server に接続する
        cache = SOAPCacheManager(user_id, patient_code)

        with self._sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
            # 要約されたキャッシュがあるかチェック
            cached_doc_date:int = cache.GetLastDocDate(cursor)

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
            new_doc_date:int = -1
            use_cache = False
            
            self._soap_by_date_list = []
            # print("SOAP の取得件数：" + str(len(rows)))
            for row in rows:
                if new_doc_date == -1:
                    new_doc_date = int(row[0]) if row[0] != None else 0
                    # print("new_doc_date:" + str(new_doc_date))
                    # print("cached_doc_date:" + str(cached_doc_date))
                    if cached_doc_date >= new_doc_date:
                        # キャッシュがあるので、SOAP を要約しない。
                        print("キャッシュがあるので、キャッシュを使用する。")
                        use_cache = True

                        # なぜここで break しないかというと、
                        # self._soap_by_date_list を後で要約前データ返却用に使用するため。
                        # break
                datetime = SOAPManager.get_datetime(row[0])
                # XML のまま GPT に投げても解釈してくれないこともないが、
                # XML のままだとトークン数をとても消費してしまうので、
                # XML を解釈して、平文に変換する。
                soap = DNP(row[1])
                self._soap_by_date_list.append((datetime, soap))

            if use_cache == True:
                cache.GetSummarizedSOAP(cursor)
                self._is_summarized = True
                self._summarized_s = cache.SummarizedS
                self._summarized_o = cache.SummarizedO
                self._summarized_a = cache.SummarizedA
                self._summarized_p = cache.SummarizedP
                self._summarized_b = cache.SummarizedB
                return
        timer.stop()

        records = self.SOAP("soapb", True)
        # print("records:" + records)

        contents_token = TokenCounter.count(records, self._model_name_for_tiktoken)
        max_tokens_for_soap_contents = max_tokens_for_soap - self._prefix_tokens
        # print("contents_token:" + str(contents_token))
        # 作成された SOAP が SOAP Token 上限に収まる場合、要約を行わない。
        self._is_summarized = False

        # print("contents_token" + str(contents_token))
        # print("max_tokens_for_soap_contents" + str(max_tokens_for_soap_contents))

        if force_original or contents_token <= max_tokens_for_soap_contents:
            print("SOAP Token 上限に収まるので、要約を行わない。contents_token: " + str(contents_token))
            return
        print("SOAP Token 上限に収まらないので、要約を行う。contents_token: " + str(contents_token))
        self._is_summarized = True

        s = ""
        o = ""
        a = ""
        p = ""
        b = ""
        
        # 収まらない場合は、要約を行う。
        # まずは、各セクションごとの比率を計算する。
        # 比率の計算は概算で良いので、"S:"というセクション名や日付を除いた文字列の長さで計算する。
        # （処理時間をなるべく削減するため）
        for soap_by_date in self._soap_by_date_list:
            if (soap_by_date[1].S != "" and soap_by_date[1].S != None):
                s = ''.join([s, "記入日：", soap_by_date[0], "\n\n", soap_by_date[1].S, "\n\n"])
            if (soap_by_date[1].O != "" and soap_by_date[1].O != None):
                o = ''.join([o, "記入日：", soap_by_date[0], "\n\n", soap_by_date[1].O, "\n\n"])
            if (soap_by_date[1].A != "" and soap_by_date[1].A != None):
                a = ''.join([a, "記入日：", soap_by_date[0], "\n\n", soap_by_date[1].A, "\n\n"])
            if (soap_by_date[1].P != "" and soap_by_date[1].P != None):
                p = ''.join([p, "記入日：", soap_by_date[0], "\n\n", soap_by_date[1].P, "\n\n"])
            if (soap_by_date[1].B != "" and soap_by_date[1].B != None):
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

        summarizer = SOAPSummarizer(self._gptconfigmanager, self._engine)
        if a != "":
            print("max_tokens_for_soap_contents_s: " + str(max_tokens_for_soap_contents_s))
            temp = self._summarize(summarizer, 's', max_tokens_for_soap_contents_s, False)
            cnt = TokenCounter.count(temp[0], self._model_name_for_tiktoken)
            print("cnt: " + str(cnt))
            self._summarized_s = ''.join(["S：\n\n", temp[0], "\n\n\n"])
            self._summarized_completion_tokens += temp[1]
            self._summarized_prompt_tokens += temp[2]
            self._summarized_total_tokens += temp[3]
            self._summarized_log = ''.join([self._summarized_log, temp[4]])
            cache.AddRowToCache('s', new_doc_date, self._summarized_s, temp[1], temp[2], temp[3], temp[4])

        if o != "":
            print("max_tokens_for_soap_contents_o: " + str(max_tokens_for_soap_contents_o))
            temp = self._summarize(summarizer, 'o', max_tokens_for_soap_contents_o, False)
            cnt = TokenCounter.count(temp[0], self._model_name_for_tiktoken)
            print("cnt: " + str(cnt))
            self._summarized_o = ''.join(["O：\n\n", temp[0], "\n\n\n"])
            self._summarized_completion_tokens += temp[1]
            self._summarized_prompt_tokens += temp[2]
            self._summarized_total_tokens += temp[3]
            self._summarized_log = ''.join([self._summarized_log, temp[4]])
            cache.AddRowToCache('o', new_doc_date, self._summarized_o, temp[1], temp[2], temp[3], temp[4])

        if a != "":
            print("max_tokens_for_soap_contents_a: " + str(max_tokens_for_soap_contents_a))
            temp = self._summarize(summarizer, 'a', max_tokens_for_soap_contents_a, False)
            cnt = TokenCounter.count(temp[0], self._model_name_for_tiktoken)
            print("cnt: " + str(cnt))
            self._summarized_a = ''.join(["A：\n\n", temp[0], "\n\n\n"])
            self._summarized_completion_tokens += temp[1]
            self._summarized_prompt_tokens += temp[2]
            self._summarized_total_tokens += temp[3]
            self._summarized_log = ''.join([self._summarized_log, temp[4]])
            cache.AddRowToCache('a', new_doc_date, self._summarized_a, temp[1], temp[2], temp[3], temp[4])

        if p != "":
            print("max_tokens_for_soap_contents_p: " + str(max_tokens_for_soap_contents_p))
            temp = self._summarize(summarizer, 'p', max_tokens_for_soap_contents_p, False)
            cnt = TokenCounter.count(temp[0], self._model_name_for_tiktoken)
            print("cnt: " + str(cnt))
            self._summarized_p = ''.join(["P：\n\n", temp[0], "\n\n\n"])
            self._summarized_completion_tokens += temp[1]
            self._summarized_prompt_tokens += temp[2]
            self._summarized_total_tokens += temp[3]
            self._summarized_log = ''.join([self._summarized_log, temp[4]])
            cache.AddRowToCache('p', new_doc_date, self._summarized_p, temp[1], temp[2], temp[3], temp[4])

        if b != "":
            print("max_tokens_for_soap_contents_b: " + str(max_tokens_for_soap_contents_b))
            temp = self._summarize(summarizer, 'b', max_tokens_for_soap_contents_b, False)
            cnt = TokenCounter.count(temp[0], self._model_name_for_tiktoken)
            print("cnt: " + str(cnt))
            self._summarized_b = ''.join(["＃：\n\n", temp[0], "\n\n\n"])
            self._summarized_completion_tokens += temp[1]
            self._summarized_prompt_tokens += temp[2]
            self._summarized_total_tokens += temp[3]
            self._summarized_log = ''.join([self._summarized_log, temp[4]])
            cache.AddRowToCache('b', new_doc_date, self._summarized_b, temp[1], temp[2], temp[3], temp[4])
   
        # print("_summarized_s : " + self._summarized_s)
        # print("_summarized_o : " + self._summarized_o)
        # print("_summarized_a : " + self._summarized_a)
        # print("_summarized_p : " + self._summarized_p)
        # print("_summarized_b : " + self._summarized_b)

        # SQL Server に接続する
        with self._sql_connector.get_conn() as cnxn:
            cnxn.autocommit = False
            with cnxn.cursor() as cursor:
                cache.SaveCache(cnxn, cursor)

        return

    @property
    def IsSumarized(self):
        return self._is_summarized
    
    @property
    def SummarizedCompletionTokens(self):
        return self._summarized_completion_tokens
    
    @property
    def SummarizedPromptTokens(self):
        return self._summarized_prompt_tokens
    
    @property
    def SummarizedTotalTokens(self):
        return self._summarized_total_tokens
    
    @property
    def SummarizedLog(self):
        return self._summarized_log
        
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
    
