from lib.sqlconnector import SQLConnector
from approaches.approach import Approach

# Attempt to answer questions by iteratively evaluating the question to see what information is missing, and once all information
# is present then formulate an answer. Each iteration consists of two parts: first use GPT to see if we need more information, 
# second if more data is needed use the requested "tool" to retrieve it. The last call to GPT answers the actual question.
# This is inspired by the MKRL paper[1] and applied here using the implementation in Langchain.
# [1] E. Karpas, et al. arXiv:2205.00445

# このクラスは旧体系の患者情報取得クラスです。
class GetPatientOldApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, patient_code:str) -> any:

        # print("run")
        # print(patient_code)

        # SQL Server に接続する
        with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:

            # SQL Server から患者情報を取得する
            cursor.execute("""SELECT Name
                FROM [dbo].[Patient] WHERE IsDeleted = 0 AND PatientCode = ?""", patient_code)
            #cursor.execute('SELECT Name FROM Patient WHERE PatientCode = ?', patient_code)
            rows = cursor.fetchall() 
        for row in rows:
            return {"name":row[0]}
        return {"name":"患者情報が見つかりませんでした。"}


