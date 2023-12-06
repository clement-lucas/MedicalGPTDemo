from lib.sqlconnector import SQLConnector
from approaches.approach import Approach

# Attempt to answer questions by iteratively evaluating the question to see what information is missing, and once all information
# is present then formulate an answer. Each iteration consists of two parts: first use GPT to see if we need more information, 
# second if more data is needed use the requested "tool" to retrieve it. The last call to GPT answers the actual question.
# This is inspired by the MKRL paper[1] and applied here using the implementation in Langchain.
# [1] E. Karpas, et al. arXiv:2205.00445
class GetPatientApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, pid:str) -> any:

        # print("run")
        # print(pid)

        # SQL Server に接続する
        with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:

            # SQL Server から患者情報を取得する
            cursor.execute("""SELECT PID_NAME
                FROM [dbo].[EXTBDH1] WHERE ACTIVE_FLG = 1 AND PID = ?""", pid)
            rows = cursor.fetchall() 
        for row in rows:
            return {"name":row[0]}
        return {"name":"患者情報が見つかりませんでした。"}

