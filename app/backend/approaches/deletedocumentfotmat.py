import os
from lib.sqlconnector import SQLConnector
from approaches.approach import Approach

class DeleteDocumentFormatApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, 
                 sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, document_format_index_id:int, 
            user_id:str
            ) -> any:
        print("UpdateDocumentFormatApproach.run")  
        print("document_format_index_id:" + str(document_format_index_id))
        print("user_id:" + user_id)

        gpt_model_name = os.getenv("AZURE_GPT_MODEL_NAME")
        # print(gpt_model_name)
        if gpt_model_name is None:
            gpt_model_name = "gpt-35-turbo"

        # トランザクションを開始する
        with self.sql_connector.get_conn() as cnxn:
            cnxn.autocommit = False
            with cnxn.cursor() as cursor:

                try:
                    # ドキュメントフォーマットの論理削除
                    update_document_format_sql = """UPDATE DocumentFormatData SET
                            IsDeleted = 1,
                            UpdatedBy = ?,
                            UpdatedDateTime = GETDATE()
                        WHERE IndexId = ?
                        AND IsDeleted = 0"""
                    cursor.execute(update_document_format_sql,
                                user_id,
                                document_format_index_id)
                    
                    update_document_format_sql = """UPDATE DocumentFormatIndex SET
                            IsDeleted = 1,
                            UpdatedBy = ?,
                            UpdatedDateTime = GETDATE()
                        WHERE IndexId = ?
                        AND IsDeleted = 0"""
                    cursor.execute(update_document_format_sql,
                                user_id,
                                document_format_index_id)
                    
                    # トランザクションのコミット
                    cnxn.commit()
                except:
                    # トランザクションのロールバック
                    cnxn.rollback()
                    raise

        return {"result": "OK"}
