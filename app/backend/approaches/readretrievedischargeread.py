######################
# 退院時サマリの作成 #
######################

import openai
import os
from lib.sqlconnector import SQLConnector
from approaches.approach import Approach
from azure.search.documents import SearchClient
from langchainadapters import HtmlCallbackHandler
from text import nonewlines
from lib.soapmanager import SOAPManager as SOAPManager

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

    # 質問文とカルテデータを受け取って GPT に投げる関数
    def get_answer(self, category_name, question, sources, system_content):
        messages = [{"role":"system","content":system_content},
                    {"role":"user","content":question + "\n\nmedical record:\n\n" + sources}]
        print(messages)

        completion = openai.ChatCompletion.create(
            engine=self.gpt_deployment,
            messages = messages,
            temperature=0.01,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)
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
        return "【" + category_name+ "】" + "\n" + answer + "\n\n", completion.usage.completion_tokens, completion.usage.prompt_tokens, completion.usage.total_tokens, prompt

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
            records += jpn_item_name + "アレルギー：" + row[0] + "による" + row[1] + "\n"
        return records

    def run(self, document_name: str, patient_code:str, overrides: dict) -> any:

        print("run")
        print(document_name)
        print(patient_code)

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
        # cursor.execute(select_datax_sql,'ON01', patient_code)
        # rows = cursor.fetchall() 
        # is_first = True
        # for row in rows:
        #     if is_first:
        #         records += "\n以下は看護師の書いた SOAP です。\n\n"
        #     is_first = False
        #     print("------1")
        #     print(row[0])
        #     print("------2")
        #     print(row[1])
        #     print("------3")
        #     datetime = self.get_datetime(row[0])
        #     # XML のまま GPT に投げても解釈してくれないこともないが、
        #     # XML のままだとトークン数をとても消費してしまうので、
        #     # XML を解釈して、平文に変換する。
        #     soap = NNP(row[1])
        #     records += "記入日：" + datetime + "\n\n"
        #     if soap.S != "":
        #         records += "S：" + soap.S + "\n\n"
        #     if soap.O != "":
        #         records += "O：" + soap.O + "\n\n"
        #     if soap.A != "":
        #         records += "A：" + soap.A + "\n\n"
        #     if soap.P != "":
        #         records += "P：" + soap.P + "\n\n"
        #     records += "\n\n"
        # print(records)

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
            WHERE DocumentName = ?
            AND Kind = ?
            AND GPTModelName = ?
            AND IsDeleted = 0"""
        gpt_model_name = os.getenv("AZURE_GPT_MODEL_NAME")
        print(gpt_model_name)
        if gpt_model_name is None:
            gpt_model_name = "gpt-35-turbo"
        cursor.execute(select_system_content_sql,
                       document_name,
                       DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                       gpt_model_name)
        rows = cursor.fetchall() 
        system_content = ""
        for row in rows:
            print(row)
            system_content = row[0]

        # ドキュメントフォーマットの取得
        select_document_format_sql = """SELECT 
                Kind, 
                CategoryName, 
                Question, 
                TargetSoapRecords, 
                UseAllergyRecords, 
                UseDischargeMedicineRecords 
            FROM DocumentFormat 
            WHERE DocumentName = ?
            AND Kind <> ?
            AND GPTModelName = ?
            AND IsDeleted = 0
            ORDER BY OrderNo"""
        cursor.execute(select_document_format_sql,
                       document_name,
                       DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                       gpt_model_name)
        rows = cursor.fetchall() 

        # 医師記録の取得
        soap_manager = SOAPManager(patient_code)

        ret = ""

        # token の集計
        sum_of_completion_tokens: int = 0
        sum_of_prompt_tokens: int = 0
        sum_of_total_tokens: int = 0

        # 作成されたプロンプトの回収（返却とログ用）
        prompts = ""
        for row in rows:
            print(row)
            kind = row[0]
            categoryName = row[1]
            question = row[2]
            targetSoapRecords = row[3]

            # 以下は今は見ていない
            useAllergyRecords = row[4]
            useDischargeMedicineRecords = row[5]

            if kind == DOCUMENT_FORMAT_KIND_SOAP:
                # SOAP からの情報取得
                answer = self.get_answer(
                    categoryName, question, 
                    soap_manager.SOAP(targetSoapRecords), 
                    system_content)
                ret += answer[0]
                sum_of_completion_tokens += answer[1]
                sum_of_prompt_tokens += answer[2]
                sum_of_total_tokens += answer[3]
                prompts += answer[4] + "\n"
            elif kind == DOCUMENT_FORMAT_KIND_ALLERGY:
                # 【アレルギー・不適応反応】​
                # ARG001（薬剤アレルギー）
                # ARG010（食物アレルギー）
                # ARG040（注意すべき食物）
                # ARGN10（その他アレルギー）

                allergy = ""
                # 薬剤アレルギー情報の取得
                allergy += self.get_allergy(cursor, 'ARG001', '薬剤', patient_code)
                
                # 食物アレルギー情報の取得
                allergy += self.get_allergy(cursor, 'ARG010', '食物', patient_code)

                # 注意すべき食物情報の取得
                allergy += self.get_allergy(cursor, 'ARG040', '注意すべき食物', patient_code)

                # その他アレルギー情報の取得
                allergy += self.get_allergy(cursor, 'ARGN10', 'その他原因物質', patient_code)
                if allergy != "":
                    allergy = "【アレルギー・不適応反応】\n" + allergy + "\n"
                else :
                    allergy = "【アレルギー・不適応反応】\n" + "なし\n\n"
                ret += allergy
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
                cursor.execute(select_taiinji_shoho_sql, patient_code)
                rows = cursor.fetchall() 
                medicine = ""
                for row in rows:
                    if row[0] == "HY1":
                        medicine += "　"
                    quantity = str(row[2])
                    # quantity の小数点以下の0を削除する
                    if quantity.find(".") != -1:
                        quantity = quantity.rstrip("0")
                        quantity = quantity.rstrip(".")
                    medicine += row[1] + "　" + quantity + row[3] + "\n"
                if medicine != "":
                    medicine = "【退院時使用薬剤】\n" + medicine + "\n"
                else:
                    medicine = "【退院時使用薬剤】\n" + "なし" + "\n\n"
                ret += medicine

        print(ret)
        records_soap = soap_manager.SOAP("soap")
        print("\n\n\nカルテデータ：\n" + records_soap + allergy + medicine)

        # History テーブルに追加する
        # TODO 今はログインの仕組みがないので、 UserId は '000001' 固定値とする
        # TODO 日本時間との時差調整の値を設定可能にする
        insert_history_sql = """INSERT INTO [dbo].[History]
           ([UserId]
           ,[PID]
           ,[DocumentName]
           ,[Prompt]
           ,[MedicalRecord]
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
           ,dateadd(hour, 9, GETDATE())
           ,dateadd(hour, 9, GETDATE())
           ,0)"""
        cursor.execute(insert_history_sql, patient_code, 
                       prompts, records_soap + allergy + medicine, 
                       ret,
                       sum_of_completion_tokens,   
                       sum_of_prompt_tokens,   
                       sum_of_total_tokens
                       )
        cursor.commit()

        return {"data_points": "test results", 
                "answer": ret + "\n\n\nカルテデータ：\n" + records_soap + allergy + medicine, 
                "thoughts": prompts, 
                "completion_tokens": sum_of_completion_tokens,   
                "prompt_tokens": sum_of_prompt_tokens,   
                "total_tokens": sum_of_total_tokens}

