import os
from lib.sqlconnector import SQLConnector
from approaches.approach import Approach
DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT = 0

class GetDocumentFormatApproach(Approach):
    def __init__(self, sourcepage_field: str, content_field: str):
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        

    def run(self, document_name: str, department_code:str, 
            icd10_code:str, 
            user_id:str,
            force_master:bool   # マスターを強制的に取得するかどうか
            ) -> any:
        
        print(user_id)

        # SQL Server に接続する
        cnxn = SQLConnector.get_conn()
        cursor = cnxn.cursor()

        gpt_model_name = os.getenv("AZURE_GPT_MODEL_NAME")
        # print(gpt_model_name)
        if gpt_model_name is None:
            gpt_model_name = "gpt-35-turbo"

        # ドキュメントフォーマットの取得
        select_document_format_master_sql = """SELECT 
                Id, 
                Kind, 
                CategoryName, 
                OrderNo,
                Temperature,
                ISNULL(Question, '') AS Question,
                ISNULL(QuestionSuffix, '') AS QuestionSuffix,
                ResponseMaxTokens,
                TargetSoapRecords, 
                UseAllergyRecords, 
                UseDischargeMedicineRecords 
            FROM DocumentFormat 
            WHERE IsMaster = 1
            AND DepartmentCode = ?
            AND Icd10Code = ?
            AND DocumentName = ?
            AND Kind <> ?
            AND GPTModelName = ?
            AND IsDeleted = 0
            ORDER BY OrderNo"""
        if force_master:
            cursor.execute(select_document_format_master_sql,
                        department_code, icd10_code,
                        document_name,
                        DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                        gpt_model_name)
        else:
            select_document_format_sql = """SELECT 
                    Id, 
                    Kind, 
                    CategoryName, 
                    OrderNo,
                    Temperature,
                    ISNULL(Question, '') AS Question,
                    ISNULL(QuestionSuffix, '') AS QuestionSuffix,
                    ResponseMaxTokens,
                    TargetSoapRecords, 
                    UseAllergyRecords, 
                    UseDischargeMedicineRecords 
                FROM DocumentFormat 
                WHERE IsMaster = 0
                AND UserId = ?
                AND DepartmentCode = ?
                AND Icd10Code = ?
                AND DocumentName = ?
                AND Kind <> ?
                AND GPTModelName = ?
                AND IsDeleted = 0
                ORDER BY OrderNo"""
            cursor.execute(select_document_format_sql,
                        user_id,
                        department_code, icd10_code,
                        document_name,
                        DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                        gpt_model_name)            
        rows = cursor.fetchall() 

        # HIT しなかった場合は、マスターを取得する
        if len(rows) == 0:
            cursor.execute(select_document_format_master_sql,
                        department_code, icd10_code,
                        document_name,
                        DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                        gpt_model_name)
            rows = cursor.fetchall() 
        
        ret = []
        for row in rows:
            isS = False
            isO = False
            isA = False
            isP = False
            isB = False

            target = row[8].upper()
            if target.find('S') >= 0:
                isS = True
            if target.find('O') >= 0:
                isO = True
            if target.find('A') >= 0:
                isA = True
            if target.find('P') >= 0:
                isP = True
            if target.find('B') >= 0:
                isB = True

            ret.append({
                "id":row[0],
                "kind":row[1],
                "category_name":row[2],
                "order_no":row[3], 
                "temperature":row[4],
                "question":row[5],
                "question_suffix":row[6],
                "response_max_tokens":row[7],
                "is_s":isS,
                "is_o":isO,
                "is_a":isA,
                "is_p":isP,
                "is_b":isB,
                "use_allergy_records":row[9],
                "use_discharge_medicine_records":row[10]
            })
        return {"document_formats":ret}
