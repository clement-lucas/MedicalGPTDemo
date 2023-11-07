import os
from lib.sqlconnector import SQLConnector
from approaches.approach import Approach
DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT = 0

class UpdateDocumentFormatApproach(Approach):
    def __init__(self, sourcepage_field: str, content_field: str):
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, document_name: str, department_code:str, 
            icd10_code:str, user_id:str, document_formats: []
            ) -> any:

        gpt_model_name = os.getenv("AZURE_GPT_MODEL_NAME")
        # print(gpt_model_name)
        if gpt_model_name is None:
            gpt_model_name = "gpt-35-turbo"

        # トランザクションを開始する
        cnxn = SQLConnector.get_conn()
        cnxn.autocommit = False
        cursor = cnxn.cursor()

        try:
            # ドキュメントフォーマットの論理削除
            update_document_format_sql = """UPDATE DocumentFormat SET
                    IsDeleted = 1,
                    UpdatedBy = ?,
                    UpdatedDateTime = GETDATE()
                WHERE IsMaster = 0
                AND DepartmentCode = ?
                AND Icd10Code = ?
                AND DocumentName = ?
                AND Kind <> ?
                AND GPTModelName = ?
                AND IsDeleted = 0"""
            cursor.execute(update_document_format_sql,
                        user_id,
                        department_code, icd10_code,
                        document_name,
                        DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                        gpt_model_name)
            
            # ドキュメントフォーマットの登録
            insert_document_format_sql = """INSERT INTO DocumentFormat
                ( 
                    IsMaster,
                    DepartmentCode,
                    Icd10Code,
                    DocumentName,
                    GPTModelName,
                    Kind, 
                    OrderNo, 
                    CategoryName, 
                    Temperature,
                    Question, 
                    QuestionSuffix,
                    ResponseMaxTokens, 
                    TargetSoapRecords, 
                    UseAllergyRecords, 
                    UseDischargeMedicineRecords,
                    CreatedBy,
                    UpdatedBy,
                    CreatedDateTime,
                    UpdatedDateTime,
                    IsDeleted
                )
                VALUES
                ( 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, GETDATE(), GETDATE(), 0)"""

            rows_to_insert = []
            for document_format in document_formats:
                target_soap = ""
                if document_format['is_s']:
                    target_soap += "s"
                if document_format['is_o']:
                    target_soap += "o"
                if document_format['is_a']:
                    target_soap += "a"
                if document_format['is_p']:
                    target_soap += "p"
                if document_format['is_b']:
                    target_soap += "b"
                rows_to_insert.append((
                    department_code,
                    icd10_code,
                    document_name,
                    gpt_model_name,
                    document_format['kind'],
                    document_format['order_no'],
                    document_format['category_name'],
                    document_format['temperature'],
                    document_format['question'],
                    document_format['question_suffix'],
                    document_format['response_max_tokens'],
                    target_soap,
                    user_id,
                    user_id
                ))
            cursor.executemany(insert_document_format_sql, rows_to_insert)

            # トランザクションのコミット
            cnxn.commit()
        except:
            # トランザクションのロールバック
            cnxn.rollback()
            raise
        finally:
            # 接続の解除
            cursor.close()
            cnxn.close()

        return {"result": "OK"}
