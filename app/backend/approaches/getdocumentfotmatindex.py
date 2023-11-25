import os
from approaches.approach import Approach
from lib.sqlconnector import SQLConnector
from lib.documentformatmanager import DocumentFormatManager
DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT = 0

class GetDocumentFormatIndexApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, document_name: str, user_id:str, is_only_myself:bool, search_text:str
            ) -> any:
        print("GetDocumentFormatIndexApproach.run")  
        print("document_name:" + document_name)
        print("user_id:" + user_id)
        print("is_only_myself:" + str(is_only_myself))
        print("search_text:" + search_text)

        self._gpt_model_name = os.getenv("AZURE_GPT_MODEL_NAME")
        if self._gpt_model_name is None:
            self._gpt_model_name = "gpt-35-turbo"

        # search_text の全角スペースを半角スペースに変換する
        search_text = search_text.replace("　", " ")

        # search_text のカンマを半角スペースに変換する
        search_text = search_text.replace(",", " ")

        # search_text を半角スペースで分割する
        search_text_list = search_text.split(" ")

        # SQL Server に接続する
        with self._sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
            rows = []
            if is_only_myself and search_text != "":
                for search_text_item in search_text_list:
                    select_document_format_sql = """SELECT 
                            [IndexId]
                            ,[IsMaster]
                            ,[IndexName]
                            ,[Tags]
                            ,[UpdatedBy]
                            ,[UpdatedDateTime]
                        FROM [DocumentFormatFile]
                        WHERE DocumentName = ?
                        AND GPTModelName = ?
                        AND UpdatedBy = ?
                        AND IsDeleted = 0
                        AND (IndexName LIKE ?
                        OR Tags LIKE ?)
                        ORDER BY IndexId"""
                    cursor.execute(select_document_format_sql,
                                document_name,
                                self._gpt_model_name,
                                user_id, 
                                "%" + search_text_item + "%", 
                                "%" + search_text_item + "%")            
                    rows.append(cursor.fetchall() )
            elif is_only_myself == False and search_text != "":
                for search_text_item in search_text_list:
                    select_document_format_sql = """SELECT 
                            [IndexId]
                            ,[IsMaster]
                            ,[IndexName]
                            ,[Tags]
                            ,[UpdatedBy]
                            ,[UpdatedDateTime]
                        FROM [DocumentFormatFile]
                        WHERE DocumentName = ?
                        AND GPTModelName = ?
                        AND IsDeleted = 0
                        AND (IndexName LIKE ?
                        OR Tags LIKE ?)
                        ORDER BY IndexId"""
                    cursor.execute(select_document_format_sql,
                                document_name,
                                self._gpt_model_name,
                                "%" + search_text_item + "%", 
                                "%" + search_text_item + "%")            
                    rows.append(cursor.fetchall() )
            elif is_only_myself and search_text == "":
                select_document_format_sql = """SELECT 
                        [IndexId]
                        ,[IsMaster]
                        ,[IndexName]
                        ,[Tags]
                        ,[IndexName]
                        ,[UpdatedBy]
                        ,[UpdatedDateTime]
                    FROM [DocumentFormatFile]
                    WHERE DocumentName = ?
                    AND GPTModelName = ?
                    AND UpdatedBy = ?
                    AND IsDeleted = 0
                    ORDER BY IndexId"""
                cursor.execute(select_document_format_sql,
                            document_name,
                            self._gpt_model_name,
                            user_id)            
                rows = cursor.fetchall() 
            else:
                select_document_format_sql = """SELECT 
                        [IndexId]
                        ,[IsMaster]
                        ,[IndexName]
                        ,[Tags]
                        ,[UpdatedBy]
                        ,[UpdatedDateTime]
                    FROM [DocumentFormatFile]
                    WHERE DocumentName = ?
                    AND GPTModelName = ?
                    AND IsDeleted = 0
                    ORDER BY IndexId"""
                cursor.execute(select_document_format_sql,
                            document_name,
                            self._gpt_model_name,
                            DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT)            
                rows = cursor.fetchall() 

        ret = []        
        for row in rows:
            ret.append({
                "index_id":row[0],
                "is_master":row[1],
                "index_name":row[2],
                "tags":row[3],
                "updated_by":row[4],
                "updated_datetime":row[5].strftime('%Y-%m-%d %H:%M:%S')
            })
        return {
            "document_format_index_list":ret}
