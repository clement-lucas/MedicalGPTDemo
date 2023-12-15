from lib.sqlconnector import SQLConnector
from approaches.approach import Approach

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


