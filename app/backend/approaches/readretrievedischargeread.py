######################
# 退院時サマリの作成 #
######################

import openai
import os
import concurrent.futures
from lib.sqlconnector import SQLConnector
from approaches.approach import Approach
from azure.search.documents import SearchClient
from lib.soapmanager import SOAPManager
from lib.gptconfigmanager import GPTConfigManager
from lib.documentformatmanager import DocumentFormatManager
from lib.laptimer import LapTimer
from lib.datetimeconverter import DateTimeConverter
from lib.tokencounter import TokenCounter

DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT = 0
DOCUMENT_FORMAT_KIND_SOAP = 1
DOCUMENT_FORMAT_KIND_ALLERGY = 2
DOCUMENT_FORMAT_KIND_DISCHARGE_MEDICINE = 3

# Attempt to answer questions by iteratively evaluating the question to see what information is missing, and once all information
# is present then formulate an answer. Each iteration consists of two parts: first use GPT to see if we need more information, 
# second if more data is needed use the requested "tool" to retrieve it. The last call to GPT answers the actual question.
# This is inspired by the MKRL paper[1] and applied here using the implementation in Langchain.
# [1] E. Karpas, et al. arXiv:2205.00445
class ReadRetrieveDischargeReadApproach(Approach):

    def __init__(self, search_client: SearchClient, sql_connector:SQLConnector, 
                 chatgpt_deployment: str, gpt_deployment: str, sourcepage_field: str, content_field: str):
        self.search_client = search_client
        self.sql_connector = sql_connector
        self.chatgpt_deployment = chatgpt_deployment
        self.gpt_deployment = gpt_deployment
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        self.model_name_for_tiktoken = GPTConfigManager(self.sql_connector).get_value("MODEL_NAME_FOR_TIKTOKEN")

    # SOAP に割り当て可能なトークン数を計算する
    def get_max_tokens_for_soap(self):
        num_tokens_for_soap = int(self.gptconfigmanager.get_value("MAX_TOTAL_TOKENS")) - int(self.gptconfigmanager.get_value("TOKEN_NUM_FOR_QUESTION"))
        return num_tokens_for_soap

    # 質問文とカルテデータを受け取って GPT に投げる関数
    def get_answer(self, category_name, temperature, question, sources, system_content, response_max_tokens):

        messages = [{"role":"system","content":system_content},
                    {"role":"user","content":''.join([question, "\n\nmedical record:\n\n", sources])}]
        # print(messages)

        timer = LapTimer()
        timer.start("推定 Token 数取得 " + category_name)
        token_num = TokenCounter.num_tokens_from_messages(messages, self.model_name_for_tiktoken)
        print("category_name: " + category_name + "  推定 Token 数:" + str(token_num))
        timer.stop()

        timer = LapTimer()
        timer.start("GPTによる回答取得 " + category_name)
        completion = openai.ChatCompletion.create(
            engine=self.gpt_deployment,
            messages = messages,
            temperature=temperature,
            max_tokens=response_max_tokens,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)
        timer.stop()

        # completion.choices[0].message.content がとして存在するか調べる
        # 存在しない場合は、「なし」を返却する
        # print(completion)
        if hasattr(completion.choices[0].message, 'content') == False:
            return "【" + category_name+ "】" + "なし\n" + "\n\n", completion.usage.completion_tokens, completion.usage.prompt_tokens, completion.usage.total_tokens, ""
        answer = completion.choices[0].message.content
        answer = answer.lstrip("【" + category_name+ "】")
        answer = answer.lstrip(category_name)
        answer = answer.lstrip(" ")
        answer = answer.lstrip("：")
        answer = answer.lstrip(":")
        answer = answer.lstrip(" ")
        answer = answer.lstrip("　")
        answer = answer.lstrip("\n")

        prompt = ' '.join(map(str, messages))

        # どうしても「「なし」と出力します。」などと冗長に出力されてしまう場合は
        # 以下のように抑止することができる。
        # answer に「なし」という文字列が含まれていたら、空文字に置き換える
        # 例）「なし」と出力します。 -> なし
        # if answer.find("「なし」と出力します。") != -1 or answer.find("「なし」という文言を出力します。") != -1:
        #     answer = "なし"
        return ''.join(["【", category_name, "】\n", answer, "\n\n"]), completion.usage.completion_tokens, completion.usage.prompt_tokens, completion.usage.total_tokens, prompt

    def get_allergy(self, cursor, pi_item_id, jpn_item_name, pid):
        select_allergy_sql = """SELECT PI_ITEM_02, PI_ITEM_03
            FROM EATBPI
            WHERE PI_ACT_FLG = 1
            AND PI_ITEM_ID = ?
            AND PID = ?"""
        
        cursor.execute(select_allergy_sql, pi_item_id, pid)
        rows = cursor.fetchall() 
        records = ""
        for row in rows:
            records = ''.join([records, jpn_item_name, "アレルギー：", row[0], "による", row[1], "\n"])
        return records

    def get_all_answers(self, 
                        soap:SOAPManager,
                        row, 
                        department_code,
                        pid, 
                        system_content):

        ret = ""
        allergy = ""
        medicine = ""

        # token の集計
        completion_tokens: int = 0
        prompt_tokens: int = 0
        total_tokens: int = 0

        prompt = ""

        # id:row[0],
        # kind:row[1],
        # category_name:row[2],
        # order_no:row[3], 
        # temperature:row[4],
        # temperature_str:str(row[4]),
        # question:row[5],
        # question_suffix:row[6],
        # response_max_tokens:row[7],
        # target_soap:row[8],
        # use_allergy_records:row[9],
        # "use_discharge_medicine_records":row[10],
        # "use_range_kind":row[11],
        # "days_before_the_date_of_hospitalization_to_use":row[12],
        # "days_after_the_date_of_hospitalization_to_use":row[13],
        # "days_before_the_date_of_discharge_to_use":row[14],
        # "days_after_the_date_of_discharge_to_use":row[15],

        kind = row[1]
        categoryName = row[2]
        temperature = row[4]
        question = row[5]

        response_max_tokens = row[7]
        target_soap_records = row[8]

        # 以下は今は見ていない
        use_allergy_records = row[9]
        use_discharge_medicine_records = row[10]

        use_range_kind = row[11]
        days_before_the_date_of_hospitalization_to_use = row[12]
        days_after_the_date_of_hospitalization_to_use = row[13]
        days_before_the_date_of_discharge_to_use = row[14]
        days_after_the_date_of_discharge_to_use = row[15]

        print(categoryName + "の処理開始")

        id_list = []
        original_data_no_list = []
        soap_text = ""
        absolute_range_start_date = -1
        absolute_range_end_date = -1
        summarized_soap_history = ""
        if kind == DOCUMENT_FORMAT_KIND_SOAP:
            # SOAP からの情報取得である

            soap_ret = soap.get_values(
                target_soap_records,
                use_range_kind,
                days_before_the_date_of_hospitalization_to_use,
                days_after_the_date_of_hospitalization_to_use,
                days_before_the_date_of_discharge_to_use,
                days_after_the_date_of_discharge_to_use)
            # print(soap_ret)
            soap_text = soap_ret[0]
            id_list = soap_ret[1]
            original_data_no_list = soap_ret[2]
            absolute_range_start_date = soap_ret[3]
            absolute_range_end_date = soap_ret[4]

            # 要約が発生した場合は履歴を確保する
            summarized_log = soap_ret[8]
            if summarized_log != "":
                summarized_soap_history = "<CATEGORY>" + str(categoryName) + "</CATEGORY><SOAP>" + \
                    soap_text + "</SOAP><COMPLETION_TOKENS_FOR_SUMMARIZE>" + \
                    str(soap[5]) + "</COMPLETION_TOKENS_FOR_SUMMARIZE><PROMPT_TOKENS_FOR_SUMMARIZE>" + \
                    str(soap[6]) + "</PROMPT_TOKENS_FOR_SUMMARIZE><TOTAL_TOKENS_FOR_SUMMARIZE>" + \
                    str(soap[7]) + "</TOTAL_TOKENS_FOR_SUMMARIZE><SUMMARIZE_LOG>" + \
                    summarized_log + "</SUMMARIZE_LOG>"
            
            # print("★★★★"+categoryName+"★★★★")
            # print(summarized_soap)
            # print("★★★★★★★★")

            answer = self.get_answer(
                categoryName, temperature, question, 
                soap_text,
                system_content,
                response_max_tokens)
            ret = answer[0]
            completion_tokens = answer[1]
            prompt_tokens = answer[2]
            total_tokens = answer[3]
            prompt = ''.join([answer[4], "\n"])
            
        elif kind == DOCUMENT_FORMAT_KIND_ALLERGY:
            # 【アレルギー・不適応反応】​
            # ARG001（薬剤アレルギー）
            # ARG010（食物アレルギー）
            # ARG040（注意すべき食物）
            # ARGN10（その他アレルギー）

            # SQL Server に接続する
            with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
                allergy = ''.join([
                    # 薬剤アレルギー情報の取得
                    self.get_allergy(cursor, 'ARG001', '薬剤', pid),
                    
                    # 食物アレルギー情報の取得
                    self.get_allergy(cursor, 'ARG010', '食物', pid),

                    # 注意すべき食物情報の取得
                    self.get_allergy(cursor, 'ARG040', '注意すべき食物', pid),

                    # その他アレルギー情報の取得
                    self.get_allergy(cursor, 'ARGN10', 'その他原因物質', pid)])
            if allergy != "":
                allergy = ''.join(["【", categoryName, "】\n", allergy, "\n"])
            else :
                allergy = "【" + categoryName + "】\nなし\n\n"
            ret = allergy
        elif kind == DOCUMENT_FORMAT_KIND_DISCHARGE_MEDICINE:
            # 【退院時使用薬剤】​
            select_taiinji_shoho_sql = """
            SELECT EXTBOD1.IATTR, EXTBOD1.INAME, EXTBOD1.NUM, EXTBOD1.UNAME FROM EXTBDH1 
                INNER JOIN EXTBOD1 
                ON EXTBOD1.DOC_NO = EXTBDH1.DOC_NO
                AND EXTBDH1.DOC_K = 'H004'
                AND EXTBOD1.IATTR in ('HD1','HY1')
                AND EXTBDH1.ACTIVE_FLG = 1 
                AND EXTBOD1.ACTIVE_FLG = 1 
                AND EXTBDH1.PID = ?
                ORDER BY EXTBOD1.SEQ"""
            # SQL Server に接続する
            with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
                cursor.execute(select_taiinji_shoho_sql, pid)
                rows = cursor.fetchall() 
            medicine = ""
            for row in rows:
                if row[0] == "HY1":
                    medicine = ''.join([medicine, "　"])
                quantity = str(row[2])
                # quantity の小数点以下の0を削除する
                if quantity.find(".") != -1:
                    quantity = quantity.rstrip("0")
                    quantity = quantity.rstrip(".")
                medicine = ''.join([medicine, row[1], "　", quantity, row[3], "\n"])
            if medicine != "":
                medicine = ''.join(["【", categoryName, "】\n", medicine, "\n"])
            else:
                medicine = "【" + categoryName + "】\nなし\n\n"
            ret = medicine

        print(categoryName + "の処理終了")
        return ret, \
                completion_tokens, \
                prompt_tokens, \
                total_tokens, \
                prompt, \
                allergy, \
                medicine, \
                id_list, \
                original_data_no_list, \
                soap_text, \
                categoryName, \
                absolute_range_start_date, \
                absolute_range_end_date, \
                target_soap_records, \
                summarized_soap_history

    # 退院時サマリの作成
    # department_code: 診療科コード これは、ECSCSM.ECTBSM.NOW_KA に格納されている値
    def run(self, department_code:str, pid:str, document_format_index_id:int, user_id:str) -> any:
        timer_total = LapTimer()
        timer_total.start("退院時サマリ作成処理全体")

        print("department_code:" + department_code)
        print("pid:" + pid)
        print("document_format_index_id:" + str(document_format_index_id))
        print("user_id:" + user_id)
                
        self.gptconfigmanager = GPTConfigManager(self.sql_connector)

        # SQL Server に接続する
        with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:

            # SQL Server から患者情報を取得する
            cursor.execute("""SELECT PID_NAME
                FROM [dbo].[EXTBDH1] WHERE ACTIVE_FLG = 1 AND PID = ?""", pid)
            rows = cursor.fetchall() 
            # Hit しなかった場合は、患者情報が見つからなかったというメッセージを返す
            if len(rows) == 0:
                return {"data_points": "test results", "answer": "患者情報が見つかりませんでした。", "thoughts": ""}

            # # QA No.11 対応により、看護記録は一旦削除する
            # # # 看護記録の取得

            # # TODO SV08, SV09 への対応

            # # 紹介元履歴の取得
            # # TODO 本項目は単純な転記であり、
            # # GPT の介在を必要としないプログラムにより実現が可能な処理であるため、
            # # ここでは SQL サンプルの記載のみにとどめ、取得しないこととする。
            # select_shokaimoto_sql = """SELECT 
            #     PI_ITEM_17 AS SHOKAI_BI,
            #     PI_ITEM_02 AS TOIN_KA,
            #     PI_ITEM_04 AS BYOIN_MEI,
            #     '' AS FROM_KA,
            #     PI_ITEM_06 AS ISHI_MEI,
            #     PI_ITEM_13 AS ZIP_CODE,
            #     PI_ITEM_14 AS ADRESS
            #     FROM EATBPI
            #     WHERE PI_ACT_FLG = 1
            #     AND PI_ITEM_ID = 'BAS001'
            #     AND PID = ?
            #     ORDER BY PI_ITEM_17 DESC"""
            
            # # cursor.execute(select_shokaimoto_sql, pid)
            # # rows = cursor.fetchall() 
            # # is_first = True
            # # for row in rows:
            # #     if is_first:
            # #         records += "\n以下は患者の紹介元履歴に関する情報 です。\n\n"
            # #     is_first = False
            # #     print(row[0])
            # #     print(row[1])
            # #     records += "紹介日：" + row[0] + "\n"
            # #     records += "当院診療科：" + row[1] + "\n"
            # #     records += "照会元病院：" + row[2] + "\n"
            # #     records += "照会元診療科：" + row[3] + "\n"
            # #     records += "照会元医師：" + row[4] + "\n"
            # #     records += "照会元郵便番号：" + row[5] + "\n"
            # #     records += "照会元住所：" + row[6] + "\n\n"

            # # 紹介先履歴の取得
            # # TODO 本項目は単純な転記であり、
            # # GPT の介在を必要としないプログラムにより実現が可能な処理であるため、
            # # ここでは SQL サンプルの記載のみにとどめ、取得しないこととする。
            # select_shokaisaki_sql = """SELECT 
            #     PI_ITEM_17 AS SHOKAI_BI,
            #     PI_ITEM_02 AS TOIN_KA,
            #     PI_ITEM_10 AS BYOIN_MEI,
            #     PI_ITEM_14 AS TO_KA,
            #     PI_ITEM_12 AS ISHI_MEI,
            #     PI_ITEM_15 AS ZIP_CODE,
            #     PI_ITEM_16 AS ADRESS
            #     FROM EATBPI
            #     WHERE PI_ACT_FLG = 1
            #     AND PI_ITEM_ID = 'BAS002'
            #     AND PID = ?
            #     ORDER BY PI_ITEM_17 DESC"""
            
            # # cursor.execute(select_shokaisaki_sql, pid)
            # # rows = cursor.fetchall() 
            # # is_first = True
            # # for row in rows:
            # #     if is_first:
            # #         records += "\n以下は患者の紹介先履歴に関する情報 です。\n\n"
            # #     is_first = False
            # #     print(row[0])
            # #     print(row[1])
            # #     records += "紹介日：" + row[0] + "\n"
            # #     records += "当院診療科：" + row[1] + "\n"
            # #     records += "照会先病院：" + row[2] + "\n"
            # #     records += "照会先診療科：" + row[3] + "\n"
            # #     records += "照会先医師：" + row[4] + "\n"
            # #     records += "照会先郵便番号：" + row[5] + "\n"
            # #     records += "照会先住所：" + row[6] + "\n\n"


            # # 退院後予約情報の取得
            # # TODO 本項目は単純な転記であり、
            # # GPT の介在を必要としないプログラムにより実現が可能な処理であるため、
            # # ここでは SQL サンプルの記載のみにとどめ、取得しないこととする。
            # select_taiinji_yoyakujoho_sql = """
            # SELECT EXTBOD1.IATTR, EXTBOD1.INAME FROM EXTBDH1 
            #     INNER JOIN EXTBOD1 
            #     ON EXTBOD1.DOC_NO = EXTBDH1.DOC_NO
            #     AND EXTBDH1.DOC_K = 'W000'
            #     AND EXTBDH1.ACTIVE_FLG = 1 
            #     AND EXTBOD1.ACTIVE_FLG = 1 
            #     AND EXTBDH1.PID = ?
            #     ORDER BY EXTBOD1.SEQ
            #     """

        # system content 部分の文言取得
        document_manager = DocumentFormatManager(
            self.sql_connector,
            document_format_index_id)
        ret_system_contetns = document_manager.get_system_contents()
        system_content = ret_system_contetns[0] + ret_system_contetns[1]
        if system_content == "":
            raise Exception("システムコンテンツが取得できませんでした。")

        # ドキュメントフォーマットの取得
        rows = document_manager.get_document_format()

        ret = ""

        # token の集計
        sum_of_completion_tokens: int = 0
        sum_of_prompt_tokens: int = 0
        sum_of_total_tokens: int = 0

        # SOAP を履歴として確保する
        soap_text_history = ''

        # 使用したデータ期間
        use_date_range_list = ""

        # 作成されたプロンプトの回収（返却とログ用）
        prompts = ""

        allergy = ""
        medicine = ""

        # 要約ログ
        summarized_soap_history = ""

        timer = LapTimer()
        timer.start("退院時サマリ作成処理")
        id_list = []
        original_data_no_list = []
        soap = SOAPManager(
            self.sql_connector,
            department_code,
            pid,
            self.gptconfigmanager,
            self.gpt_deployment)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            features = [executor.submit(self.get_all_answers,
                                        soap,
                                        row, 
                                        department_code,
                                        pid, 
                                        system_content) for row in rows]
            for feature in features:
                try:
                    exception = feature.exception() # 例外が発生しなかった場合はNoneを返す
                    if exception is not None:
                        raise exception
                except Exception as e:
                    # print(e)
                    raise e
                future_ret = feature.result()

                ret = ''.join([ret, future_ret[0]])
                sum_of_completion_tokens += future_ret[1]
                sum_of_prompt_tokens += future_ret[2]
                sum_of_total_tokens += future_ret[3]
                prompts = ''.join([prompts, future_ret[4], "\n"])
                allergy = ''.join([allergy, future_ret[5]])
                medicine = ''.join([medicine, future_ret[6]])
                id_list.extend(future_ret[7])
                original_data_no_list.extend(future_ret[8])
                soap_text = future_ret[9]
                categoryName = future_ret[10]
                absolute_range_start_date = future_ret[11]
                absolute_range_end_date = future_ret[12]
                target_soap_records = future_ret[13]
                summarized_soap_history = ''.join([summarized_soap_history, future_ret[14]])
                if soap_text != "":
                    soap_text_history = ''.join([soap_text_history, "【", categoryName, " 使用データ】\n", soap_text, "\n\n"])
                if absolute_range_start_date != -1 and absolute_range_end_date != -1:
                    absolute_range_start_date_str = DateTimeConverter.int_2_str(absolute_range_start_date)
                    absolute_range_end_date_str = DateTimeConverter.int_2_str(absolute_range_end_date)
                    use_date_range_list = ''.join([use_date_range_list, "【", categoryName, " データ使用期間】\n", absolute_range_start_date_str, " ～ ", absolute_range_end_date_str, "\n", target_soap_records, "\n\n"])


        # print(ret)
        # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
        # records_soap = soap_manager.SOAP("soapb", True)
        # print("\n\n\nカルテデータ：\n" + records_soap + allergy + medicine)
        timer.stop()

        # 重複を削除する
        id_list = list(set(id_list))
        original_data_no_list = list(set(original_data_no_list))

        # をカンマ区切りの文字列に変換する
        id_list = ','.join(map(str, id_list))
        original_data_no_list = ','.join(map(str, original_data_no_list))

        # History テーブルに追加する
        # TODO 日本時間との時差調整の値を設定可能にする
        insert_history_sql = """INSERT INTO [dbo].[History]
           ([PID]
           ,[DocumentName]
           ,[Prompt]
           ,[HospitalizationDate]
           ,[DischargeDate]
           ,[DocumentFormatIndexId]
           ,[OriginalDocNoList]
           ,[IntermediateDataIds]
           ,[UseDateRangeList]
           ,[SoapForCategories]
           ,[SummarizedMedicalRecord]
           ,[Response]
           ,[CompletionTokens]
           ,[PromptTokens]
           ,[TotalTokens]
           ,[CreatedLocalDateTime]
           ,[UpdatedLocalDateTime]
           ,[CreatedBy]
           ,[UpdatedBy]
           ,[CreatedDateTime]
           ,[UpdatedDateTime]
           ,[IsDeleted])
        VALUES
           (?
           ,N'退院時サマリ'
           ,?
           ,?
           ,?
           ,?
           ,?
           ,?
           ,?
           ,?
           ,?
           ,?
           ,?
           ,?
           ,?
           ,dateadd(hour, 9, GETDATE())
           ,dateadd(hour, 9, GETDATE())
           ,?
           ,?
           ,GETDATE()
           ,GETDATE()
           ,0)"""

        # SQL Server に接続する
        with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
            cursor.execute(insert_history_sql, pid, 
                        prompts, 
                        soap.hospitalization_date_str,
                        soap.discharge_date_str,
                        document_format_index_id,
                        original_data_no_list,
                        id_list,
                        use_date_range_list,
                        soap_text_history,
                        summarized_soap_history,
                        ret,
                        sum_of_completion_tokens,   
                        sum_of_prompt_tokens,   
                        sum_of_total_tokens, user_id, user_id
                        )
            cursor.commit()

        timer_total.stop()

        return {"data_points": "test results", 
                "answer": ''.join([ret, "\n\nカルテデータ: \n\n", soap_text_history]), 
                "thoughts": prompts, 
                "completion_tokens": sum_of_completion_tokens,   
                "prompt_tokens": sum_of_prompt_tokens,   
                "total_tokens": sum_of_total_tokens}

