import os
from approaches.approach import Approach
from lib.sqlconnector import SQLConnector
from lib.documentformatmanager import DocumentFormatManager
DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT = 0

class GetDocumentFormatFileListApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, document_name: str, user_id:str, is_only_myself:bool
            ) -> any:
        print("GetDocumentFormatFileListApproach.run")  
        print("document_name:" + document_name)
        print("user_id:" + user_id)
        print("is_only_myself:" + str(is_only_myself))

        self._gpt_model_name = os.getenv("AZURE_GPT_MODEL_NAME")
        if self._gpt_model_name is None:
            self._gpt_model_name = "gpt-35-turbo"

        # SQL Server に接続する
        with self._sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
            if is_only_myself:
                select_document_format_sql = """SELECT 
                        [FileId]
                        ,[IsMaster]
                        ,[FileName]
                        ,[UpdatedBy]
                    FROM [DocumentFormatFile]
                    WHERE DocumentName = ?
                    AND GPTModelName = ?
                    AND UpdatedBy = ?
                    AND IsDeleted = 0
                    ORDER BY FileId"""
                cursor.execute(select_document_format_sql,
                            document_name,
                            self._gpt_model_name,
                            DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT, user_id)            
            else:
                select_document_format_sql = """SELECT 
                        [FileId]
                        ,[IsMaster]
                        ,[FileName]
                        ,[UpdatedBy]
                    FROM [DocumentFormatFile]
                    WHERE DocumentName = ?
                    AND GPTModelName = ?
                    AND IsDeleted = 0
                    ORDER BY FileId"""
                cursor.execute(select_document_format_sql,
                            document_name,
                            self._gpt_model_name,
                            DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT)            
            rows = cursor.fetchall() 

        ret = []        
        for row in rows:
            ret.append({
                "file_id":row[0],
                "is_master":row[1],
                "file_name":row[2],
                "updated_by":row[3]
            })
        return {
            "document_format_file_list":ret}
