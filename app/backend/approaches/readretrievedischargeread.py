######################
# 退院時サマリの作成 #
######################

import openai
import os
import concurrent.futures
from lib.sqlconnector import SQLConnector
from approaches.approach import Approach
from azure.search.documents import SearchClient
from lib.soapmanager import SOAPManager as SOAPManager
from lib.tokencounter import TokenCounter
from lib.gptconfigmanager import GPTConfigManager
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

    def __init__(self, search_client: SearchClient, chatgpt_deployment: str, gpt_deployment: str, sourcepage_field: str, content_field: str):
        self.search_client = search_client
        self.chatgpt_deployment = chatgpt_deployment
        self.gpt_deployment = gpt_deployment
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field

    # SOAP に割り当て可能なトークン数を計算する
    def get_max_tokens_for_soap(self, question, system_content, response_max_tokens):
        messages_without_soap = [{"role":"system","content":system_content},
                    {"role":"user","content":''.join([question, "\n\nmedical record:\n\n"])}]
        num_tokens_without_soap = TokenCounter.num_tokens_from_messages(messages_without_soap, self.gptconfigmanager.get_value("MODEL_NAME_FOR_TIKTOKEN"))
        num_tokens_for_soap = int(self.gptconfigmanager.get_value("MAX_TOTAL_TOKENS")) - num_tokens_without_soap - response_max_tokens
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

    def get_allergy(self, cursor, pi_item_id, jpn_item_name, patient_code):
        select_allergy_sql = """SELECT PI_ITEM_02, PI_ITEM_03
            FROM EATBPI
            WHERE PI_ACT_FLG = 1
            AND PI_ITEM_ID = ?
            AND PID = ?"""
        
        cursor.execute(select_allergy_sql, pi_item_id, patient_code)
        rows = cursor.fetchall() 
        records = ""
        for row in rows:
            records = ''.join([records, jpn_item_name, "アレルギー：", row[0], "による", row[1], "\n"])
        return records

    def get_all_answers(self, 
                        row, 
                        patient_code, 
                        system_content, 
                        soap_manager):

        ret = ""
        allergy = ""
        medicine = ""

        # token の集計
        completion_tokens: int = 0
        prompt_tokens: int = 0
        total_tokens: int = 0

        # 要約後の SOAP を格納する変数
        summarized_soap_history = ""
        prompt = ""

        kind = row[0]
        categoryName = row[1]
        temperature = row[2]
        question = row[3]
        response_max_tokens = row[4]
        targetSoapRecords = row[5]

        # 以下は今は見ていない
        useAllergyRecords = row[6]
        useDischargeMedicineRecords = row[7]
        print(categoryName + "の処理開始")

        if kind == DOCUMENT_FORMAT_KIND_SOAP:
            # SOAP からの情報取得である

            # SOAP に割り当て可能なトークン数を計算する
            num_tokens_for_soap = self.get_max_tokens_for_soap(
                question, system_content, response_max_tokens)

            soap = soap_manager.SOAP(
                    targetSoapRecords, num_tokens_for_soap)
            summarized_soap = soap[0]

            # print("★★★★"+categoryName+"★★★★")
            # print(summarized_soap)
            # print("★★★★★★★★")

            # 要約した SOAP を履歴として確保する
            summarized_soap_history = ''.join([summarized_soap_history,
                "<CATEGORY>", str(categoryName), "</CATEGORY><SOAP>",
                str(summarized_soap), "</SOAP><COMPLETION_TOKENS_FOR_SUMMARIZE>",
                str(soap[1]), "</COMPLETION_TOKENS_FOR_SUMMARIZE><PROMPT_TOKENS_FOR_SUMMARIZE>",
                str(soap[2]), "</PROMPT_TOKENS_FOR_SUMMARIZE><TOTAL_TOKENS_FOR_SUMMARIZE>",
                str(soap[3]), "</TOTAL_TOKENS_FOR_SUMMARIZE><SUMMARIZE_LOG>",
                str(soap[4]), "</SUMMARIZE_LOG>"])

            answer = self.get_answer(
                categoryName, temperature, question, 
                summarized_soap,
                system_content,
                response_max_tokens)
            ret = answer[0]
            completion_tokens = answer[1]
            prompt_tokens = answer[2]
            total_tokens = answer[3]
            prompts = ''.join([answer[4], "\n"])
            
        elif kind == DOCUMENT_FORMAT_KIND_ALLERGY:
            # 【アレルギー・不適応反応】​
            # ARG001（薬剤アレルギー）
            # ARG010（食物アレルギー）
            # ARG040（注意すべき食物）
            # ARGN10（その他アレルギー）

            # SQL Server に接続する
            cnxn = SQLConnector.get_conn()
            cursor = cnxn.cursor()

            allergy = ''.join([
                # 薬剤アレルギー情報の取得
                self.get_allergy(cursor, 'ARG001', '薬剤', patient_code),
                
                # 食物アレルギー情報の取得
                self.get_allergy(cursor, 'ARG010', '食物', patient_code),

                # 注意すべき食物情報の取得
                self.get_allergy(cursor, 'ARG040', '注意すべき食物', patient_code),

                # その他アレルギー情報の取得
                self.get_allergy(cursor, 'ARGN10', 'その他原因物質', patient_code)])
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
            cnxn = SQLConnector.get_conn()
            cursor = cnxn.cursor()
            cursor.execute(select_taiinji_shoho_sql, patient_code)
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
                summarized_soap_history, \
                allergy, \
                medicine

    def run(self, document_name: str, patient_code:str, department_code:str, icd10_code:str, overrides: dict) -> any:

        # print("run")
        # print(document_name)
        # print(patient_code)

        self.gptconfigmanager = GPTConfigManager()

        # SQL Server に接続する
        cnxn = SQLConnector.get_conn()
        cursor = cnxn.cursor()

        # SQL Server から患者情報を取得する
        cursor.execute("""SELECT PID_NAME
            FROM [dbo].[EXTBDH1] WHERE ACTIVE_FLG = 1 AND PID = ?""", patient_code)
        rows = cursor.fetchall() 
        # Hit しなかった場合は、患者情報が見つからなかったというメッセージを返す
        if len(rows) == 0:
            return {"data_points": "test results", "answer": "患者情報が見つかりませんでした。", "thoughts": ""}

        # QA No.11 対応により、看護記録は一旦削除する
        # # 看護記録の取得

        # TODO SV08, SV09 への対応

        # 紹介元履歴の取得
        # TODO 本項目は単純な転記であり、
        # GPT の介在を必要としないプログラムにより実現が可能な処理であるため、
        # ここでは SQL サンプルの記載のみにとどめ、取得しないこととする。
        select_shokaimoto_sql = """SELECT 
            PI_ITEM_17 AS SHOKAI_BI,
            PI_ITEM_02 AS TOIN_KA,
            PI_ITEM_04 AS BYOIN_MEI,
            '' AS FROM_KA,
            PI_ITEM_06 AS ISHI_MEI,
            PI_ITEM_13 AS ZIP_CODE,
            PI_ITEM_14 AS ADRESS
            FROM EATBPI
            WHERE PI_ACT_FLG = 1
            AND PI_ITEM_ID = 'BAS001'
            AND PID = ?
            ORDER BY PI_ITEM_17 DESC"""
        
        # cursor.execute(select_shokaimoto_sql, patient_code)
        # rows = cursor.fetchall() 
        # is_first = True
        # for row in rows:
        #     if is_first:
        #         records += "\n以下は患者の紹介元履歴に関する情報 です。\n\n"
        #     is_first = False
        #     print(row[0])
        #     print(row[1])
        #     records += "紹介日：" + row[0] + "\n"
        #     records += "当院診療科：" + row[1] + "\n"
        #     records += "照会元病院：" + row[2] + "\n"
        #     records += "照会元診療科：" + row[3] + "\n"
        #     records += "照会元医師：" + row[4] + "\n"
        #     records += "照会元郵便番号：" + row[5] + "\n"
        #     records += "照会元住所：" + row[6] + "\n\n"

        # 紹介先履歴の取得
        # TODO 本項目は単純な転記であり、
        # GPT の介在を必要としないプログラムにより実現が可能な処理であるため、
        # ここでは SQL サンプルの記載のみにとどめ、取得しないこととする。
        select_shokaisaki_sql = """SELECT 
            PI_ITEM_17 AS SHOKAI_BI,
            PI_ITEM_02 AS TOIN_KA,
            PI_ITEM_10 AS BYOIN_MEI,
            PI_ITEM_14 AS TO_KA,
            PI_ITEM_12 AS ISHI_MEI,
            PI_ITEM_15 AS ZIP_CODE,
            PI_ITEM_16 AS ADRESS
            FROM EATBPI
            WHERE PI_ACT_FLG = 1
            AND PI_ITEM_ID = 'BAS002'
            AND PID = ?
            ORDER BY PI_ITEM_17 DESC"""
        
        # cursor.execute(select_shokaisaki_sql, patient_code)
        # rows = cursor.fetchall() 
        # is_first = True
        # for row in rows:
        #     if is_first:
        #         records += "\n以下は患者の紹介先履歴に関する情報 です。\n\n"
        #     is_first = False
        #     print(row[0])
        #     print(row[1])
        #     records += "紹介日：" + row[0] + "\n"
        #     records += "当院診療科：" + row[1] + "\n"
        #     records += "照会先病院：" + row[2] + "\n"
        #     records += "照会先診療科：" + row[3] + "\n"
        #     records += "照会先医師：" + row[4] + "\n"
        #     records += "照会先郵便番号：" + row[5] + "\n"
        #     records += "照会先住所：" + row[6] + "\n\n"


        # 退院後予約情報の取得
        # TODO 本項目は単純な転記であり、
        # GPT の介在を必要としないプログラムにより実現が可能な処理であるため、
        # ここでは SQL サンプルの記載のみにとどめ、取得しないこととする。
        select_taiinji_yoyakujoho_sql = """
        SELECT EXTBOD1.IATTR, EXTBOD1.INAME FROM EXTBDH1 
            INNER JOIN EXTBOD1 
            ON EXTBOD1.DOC_NO = EXTBDH1.DOC_NO
            AND EXTBDH1.DOC_K = 'W000'
            AND EXTBDH1.ACTIVE_FLG = 1 
            AND EXTBOD1.ACTIVE_FLG = 1 
            AND EXTBDH1.PID = ?
			ORDER BY EXTBOD1.SEQ
            """
        # system content 部分の文言取得
        select_system_content_sql = """SELECT 
                Question
            FROM DocumentFormat 
            WHERE IsMaster = 1
            AND DocumentName = ?
            AND Kind = ?
            AND GPTModelName = ?
            AND IsDeleted = 0"""
        gpt_model_name = os.getenv("AZURE_GPT_MODEL_NAME")
        # print(gpt_model_name)
        if gpt_model_name is None:
            gpt_model_name = "gpt-35-turbo"
        cursor.execute(select_system_content_sql,
                       document_name,
                       DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                       gpt_model_name)
        rows = cursor.fetchall() 
        system_content = ""
        for row in rows:
            # print(row)
            system_content = row[0]

        # ドキュメントフォーマットの取得
        select_document_format_sql = """SELECT 
                Kind, 
                CategoryName, 
                Temperature,
                ISNULL(Question, '') + ISNULL(QuestionSuffix, '') AS Question,
                ResponseMaxTokens,
                TargetSoapRecords, 
                UseAllergyRecords, 
                UseDischargeMedicineRecords 
            FROM DocumentFormat 
            WHERE IsMaster = ?
            AND DepartmentCode = ?
            AND Icd10Code = ?
            AND DocumentName = ?
            AND Kind <> ?
            AND GPTModelName = ?
            AND IsDeleted = 0
            ORDER BY OrderNo"""
        cursor.execute(select_document_format_sql,
                       0, department_code, icd10_code,
                       document_name,
                       DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                       gpt_model_name)
        rows = cursor.fetchall() 

        # マスター以外が HIT しなかった場合は、マスターを取得する
        if len(rows) == 0:
            cursor.execute(select_document_format_sql,
                        1, department_code, icd10_code,
                        document_name,
                        DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                        gpt_model_name)
            rows = cursor.fetchall() 

        # 医師記録の取得
        soap_manager = SOAPManager(self.gptconfigmanager, patient_code, 
            self.gpt_deployment)

        ret = ""

        # token の集計
        sum_of_completion_tokens: int = 0
        sum_of_prompt_tokens: int = 0
        sum_of_total_tokens: int = 0

        # 要約後の SOAP を格納する変数
        summarized_soap_history = ""

        # 作成されたプロンプトの回収（返却とログ用）
        prompts = ""

        allergy = ""
        medicine = ""

        timer = LapTimer()
        timer.start("退院時サマリ作成処理")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            features = [executor.submit(self.get_all_answers,
                        row, 
                        patient_code, 
                        system_content, 
                        soap_manager) for row in rows]
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
                summarized_soap_history = ''.join([summarized_soap_history, future_ret[5]])
                allergy = ''.join([allergy, future_ret[6]])
                medicine = ''.join([medicine, future_ret[7]])

        # print(ret)
        records_soap = soap_manager.SOAP("soapb")[0]
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
        cursor.execute(insert_history_sql, patient_code, 
                       prompts, ''.join([records_soap, allergy, medicine]),
                       summarized_soap_history,
                       ret,
                       sum_of_completion_tokens,   
                       sum_of_prompt_tokens,   
                       sum_of_total_tokens
                       )
        cursor.commit()

        return {"data_points": "test results", 
                "answer": ''.join([ret, "\n\n\nカルテデータ：\n", records_soap, allergy, medicine]), 
                "thoughts": prompts, 
                "completion_tokens": sum_of_completion_tokens,   
                "prompt_tokens": sum_of_prompt_tokens,   
                "total_tokens": sum_of_total_tokens}

