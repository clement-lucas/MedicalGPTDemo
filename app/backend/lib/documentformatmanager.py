import os
from lib.sqlconnector import SQLConnector
DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT = 0

# DocumentFormat テーブルの内容を取得するクラス

class DocumentFormatManager:

    def __init__(self, sql_connector:SQLConnector, 
                 document_format_index_id:int
                ) -> None:
        self._sql_connector = sql_connector
        self._document_format_index_id = document_format_index_id

    def get_system_contents(self
            ) -> any:
        
        # SQL Server に接続する
        with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:

            rows = []
            # システムコンテンツの取得
            select_system_contents_sql = """SELECT 
                    ISNULL(Question, '') AS Question,
                    ISNULL(QuestionSuffix, '') AS QuestionSuffix
                FROM DocumentFormat 
                WHERE IndexId = ?
                AND Kind = ?
                AND IsDeleted = 0
                ORDER BY OrderNo"""
            cursor.execute(select_system_contents_sql,
                        self._document_format_index_id,
                        DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT)            
            rows = cursor.fetchall() 

            if len(rows) < 1:
                raise Exception("システムコンテンツが存在しません。IndexId:" + self._document_format_index_id) 

            system_contetns = rows[0][0]
            system_contetns_suffix = rows[0][1]
            return system_contetns, system_contetns_suffix

    def get_document_format(self
            ) -> any:
        
        # SQL Server に接続する
        with self._sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
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
                WHERE IndexId = ?
                AND Kind = ?
                AND IsDeleted = 0
                ORDER BY OrderNo"""
            cursor.execute(select_document_format_sql,
                        self._document_format_index_id,
                        DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT)            
            rows = cursor.fetchall() 

        return rows
                


        


