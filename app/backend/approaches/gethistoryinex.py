import os
import pyodbc
from approaches.approach import Approach
from lib.sqlconnector import SQLConnector

class GetHistoryIndexApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
    
    # TODO ログインユーザーごとの絞り込みが必要であれば、引数にユーザーIDを追加する
    def run(self, document_name:str) -> any:

        # print("run")

        # SQL Server に接続する
        # 接続文字列を取得する
        with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:

            # SQL Server から履歴情報を取得する
            cursor.execute("""
                SELECT [History].[Id]
                    ,[History].[PID]
                    ,[EXTBDH1].[PID_NAME]
                    ,[History].[CreatedDateTime]
                    ,Format([History].[CreatedLocalDateTime],'yyyy/MM/dd') AS CreatedDate
                FROM [dbo].[History]
                INNER JOIN (SELECT DISTINCT PID, PID_NAME FROM EXTBDH1 WHERE ACTIVE_FLG = 1) AS EXTBDH1
                ON [History].[PID] = [EXTBDH1].[PID] AND [History].[IsDeleted] = 0
                AND [History].[DocumentName] = ?
                ORDER BY [History].[CreatedLocalDateTime] DESC
                """, document_name)
            rows = cursor.fetchall() 

        # print(rows)
  
        # SQL Server から取得した履歴情報を整形する
        history_date_list = []
        current_date = ""
        current_history_list = []
        for row in rows:
            id = row[0]
            pid = row[1]
            patient_name = row[2]
            created_date = row[4]
            if current_date == created_date:
                # 既存の日付に履歴情報を追加する
                current_history_list.append({"id":id , 
                                    "pid":pid ,
                                    "patient_name":patient_name,
                                    "document_name":document_name})
            else:
                # 新しい日付の履歴情報を追加する
                if current_history_list != []:
                    history_date_list.append({"created_date":current_date , "history_list":current_history_list})
                current_date = created_date
                current_history_list = []
                current_history_list.append({"id":id ,
                                    "pid":pid ,
                                    "patient_name":patient_name,
                                    "document_name":document_name})
        if current_history_list != []:
            history_date_list.append({"created_date":current_date , "history_list":current_history_list})
        
        return {"history_date_list":history_date_list}
        

