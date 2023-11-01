import os
from lib.sqlconnector import SQLConnector
from approaches.approach import Approach
DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT = 0

class DocumentFormat:
    kind: int
    category_name: str
    temperature: float
    question: str
    question_suffix: str
    response_max_tokens: int
    is_s: bool
    is_o: bool
    is_a: bool
    is_p: bool
    is_b: bool
    use_allergy_records: bool
    use_discharge_medicine_records: bool

class UpdateDocumentFormatApproach(Approach):
    def __init__(self, sourcepage_field: str, content_field: str):
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, document_name: str, department_code:str, 
            icd10_code:str, document_formats: [DocumentFormat]
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
                    UpdatedDateTime = GETDATE()
                WHERE IsMaster = 0
                AND DepartmentCode = ?
                AND Icd10Code = ?
                AND DocumentName = ?
                AND Kind <> ?
                AND GPTModelName = ?
                AND IsDeleted = 1"""
            cursor.execute(update_document_format_sql,
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
                    CreatedDateTime,
                    UpdatedDateTime,
                    IsDeleted
                )
                VALUES
                ( 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, GETDATE(), GETDATE(), 0)"""

            rows_to_insert = []
            order = 0
            for document_format in document_formats:
                target_soap = ""
                if document_format.is_s:
                    target_soap += "s"
                if document_format.is_o:
                    target_soap += "o"
                if document_format.is_a:
                    target_soap += "a"
                if document_format.is_p:
                    target_soap += "p"
                if document_format.is_b:
                    target_soap += "b"
                rows_to_insert.append((
                    department_code,
                    icd10_code,
                    document_name,
                    gpt_model_name,
                    document_format.kind,
                    order,
                    document_format.category_name,
                    document_format.temperature,
                    document_format.question,
                    document_format.question_suffix,
                    document_format.response_max_tokens,
                    target_soap
                ))
                order += 1
            cursor.execute(insert_document_format_sql, rows_to_insert);

            # トランザクションのコミット
            cnxn.commit()
        except:
            # トランザクションのロールバック
            cnxn.rollback()
        finally:
            # 接続の解除
            cursor.close()
            cnxn.close()

        return {"result": "OK"}
