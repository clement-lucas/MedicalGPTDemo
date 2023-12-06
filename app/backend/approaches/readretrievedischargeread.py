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
                        row, 
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
        # use_discharge_medicine_records:row[10]
        # "start_day_to_use_soap_range_after_hospitalization":row[11],
        # "use_soap_range_days_after_hospitalization":row[12],
        # "start_day_to_use_soap_range_before_discharge":row[13],
        # "use_soap_range_days_before_discharge":row[14]

        kind = row[1]
        categoryName = row[2]
        temperature = row[4]
        question = row[5]

        response_max_tokens = row[7]
        targetSoapRecords = row[8]

        # 以下は今は見ていない
        useAllergyRecords = row[9]
        useDischargeMedicineRecords = row[10]
        print(categoryName + "の処理開始")

        if kind == DOCUMENT_FORMAT_KIND_SOAP:
            # SOAP からの情報取得である

            soap = SOAPManager.get_values(
                self.sql_connector,
                pid,
                # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★
                self._department_code,
                targetSoapRecords,
                row[11],
                row[12],
                row[13],
                row[14])
            # print(soap)
            summarized_soap = soap

            # print("★★★★"+categoryName+"★★★★")
            # print(summarized_soap)
            # print("★★★★★★★★")

            answer = self.get_answer(
                categoryName, temperature, question, 
                summarized_soap,
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
                medicine

    def run(self, pid:str, document_format_index_id:int, user_id:str, overrides: dict) -> any:
        timer_total = LapTimer()
        timer_total.start("退院時サマリ作成処理全体")

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

        timer = LapTimer()
        timer.start("SOAP の読込と必要に応じた要約処理")
        # 医師記録の取得
        # SOAP に割り当て可能なトークン数を計算する
        num_tokens_for_soap = self.get_max_tokens_for_soap()
        timer.stop()

        ret = ""

        # token の集計
        sum_of_completion_tokens: int = 0
        sum_of_prompt_tokens: int = 0
        sum_of_total_tokens: int = 0

        # 要約した SOAP を履歴として確保する（廃盤）
        summarized_soap_history = ''

        # 作成されたプロンプトの回収（返却とログ用）
        prompts = ""

        allergy = ""
        medicine = ""

        timer.start("退院時サマリ作成処理")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            features = [executor.submit(self.get_all_answers,
                        row, 
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
                # [0]:ret, \
                # [1]:completion_tokens, \
                # [2]:prompt_tokens, \
                # [3]:total_tokens, \
                # [4]:prompt, \
                # [5]:summarized_soap_history
                # [6]:allergy
                # [7]:medicine

                ret = ''.join([ret, future_ret[0]])
                sum_of_completion_tokens += future_ret[1]
                sum_of_prompt_tokens += future_ret[2]
                sum_of_total_tokens += future_ret[3]
                prompts = ''.join([prompts, future_ret[4], "\n"])
                allergy = ''.join([allergy, future_ret[5]])
                medicine = ''.join([medicine, future_ret[6]])

        # print(ret)
        # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
        records_soap = soap_manager.SOAP("soapb", True)
        # print("\n\n\nカルテデータ：\n" + records_soap + allergy + medicine)
        timer.stop()

        # History テーブルに追加する
        # TODO 今はログインの仕組みがないので、 UserId は '000001' 固定値とする
        # TODO 日本時間との時差調整の値を設定可能にする
        insert_history_sql = """INSERT INTO [dbo].[History]
           ([UserId]
           ,[PID]
           ,[DocumentName]
           ,[Prompt]
           ,[MedicalRecord]
           ,[SummarizedMedicalRecord]
           ,[Response]
           ,[CompletionTokens]
           ,[PromptTokens]
           ,[TotalTokens]
           ,[CreatedDateTime]
           ,[UpdatedDateTime]
           ,[IsDeleted])
        VALUES
           ('000001'
           ,?
           ,N'退院時サマリ'
           ,?
           ,?
           ,?
           ,?
           ,?
           ,?
           ,?
           ,dateadd(hour, 9, GETDATE())
           ,dateadd(hour, 9, GETDATE())
           ,0)"""
        
        # SQL Server に接続する
        with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
            cursor.execute(insert_history_sql, pid, 
                        prompts, ''.join([records_soap, allergy, medicine]),
                        summarized_soap_history,
                        ret,
                        sum_of_completion_tokens,   
                        sum_of_prompt_tokens,   
                        sum_of_total_tokens
                        )
            cursor.commit()

        timer_total.stop()

        return {"data_points": "test results", 
                "answer": ''.join([ret, "\n\n\nカルテデータ：\n", records_soap, allergy, medicine]), 
                "thoughts": prompts, 
                "completion_tokens": sum_of_completion_tokens,   
                "prompt_tokens": sum_of_prompt_tokens,   
                "total_tokens": sum_of_total_tokens}

