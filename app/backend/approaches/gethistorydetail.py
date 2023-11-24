import os
import pyodbc
from approaches.approach import Approach
from lib.sqlconnector import SQLConnector

class GetHistoryDetailApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, id:int) -> any:

        # print("run")
        # print(id)

        # SQL Server に接続する
        # 接続文字列を取得する
        with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:

            # SQL Server から履歴情報を取得する
            cursor.execute("""
                SELECT [History].[Id]
                    ,[History].[UserId]
                    ,[History].[PID]
                    ,[History].[Prompt]
                    ,[History].[MedicalRecord]
                    ,[History].[Response]
                    ,[History].[CompletionTokens]
                    ,[History].[PromptTokens]
                    ,[History].[TotalTokens]
                    ,[History].[CreatedDateTime]
                    ,[History].[UpdatedDateTime]
                    ,[EXTBDH1].[PID_NAME]
                FROM [dbo].[History]
                INNER JOIN (SELECT DISTINCT PID, PID_NAME FROM EXTBDH1 WHERE ACTIVE_FLG = 1) AS EXTBDH1
                ON [History].[PID] = [EXTBDH1].[PID] AND [History].[IsDeleted] = 0 AND [History].[Id] = ?
                """, id)
            rows = cursor.fetchall() 

        for row in rows:
            id = row[0]
            user_id = row[1]
            pid = row[2]
            prompt = row[3]
            medical_record = row[4]
            response = row[5]
            completion_tokens = row[6]
            prompt_tokens = row[7]
            total_tokens = row[8]
            created_date_time = row[9]
            updated_date_time = row[10]
            patient_name = row[11]


            return {"data_points": "test results", 
                    "pid": pid,
                    "patient_name": patient_name,
                    "answer": response + "\n\n\nカルテデータ：\n" + medical_record, 
                    "thoughts": prompt, 
                    "completion_tokens": completion_tokens,   
                    "prompt_tokens": prompt_tokens,   
                    "total_tokens": total_tokens}

        return {"name":"履歴情報が見つかりませんでした。"}
    

    


