from lib.sqlconnector import SQLConnector
from approaches.approach import Approach
from lib.datetimeconverter import DateTimeConverter

class GetPatientApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, pid:str, department_code:str) -> any:

        # print("run")
        # print(pid)

        if pid is None or pid == "":
            return {"name":""}

        # SQL Server に接続する
        with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:

            # SQL Server から患者情報を取得する
            cursor.execute("""SELECT TOP 1 PID_NAME
                FROM [dbo].[EXTBDH1] WHERE ACTIVE_FLG = 1 AND PID = ?""", pid)
            row = cursor.fetchone() 
            if row is None:
                return {"name":"患者情報が見つかりませんでした。",
                        "hospitalization_date":"-",
                        "discharge_date":"-"}

            pid_name = row[0]

            if department_code is None or department_code == "":
                return {"name":pid_name,
                        "hospitalization_date":"-",
                        "discharge_date":"-"}

            # サマリ管理テーブルから、入院日と退院日を取得する。
            select_hospitalization_sql = """
                SELECT TOP 1 NOW_DATE, TAIIN_DATE
                FROM ECSCSM_ECTBSM
                WHERE PID = ?
                AND SUM_SYUBETU = '01'
                AND NOW_KA = ?
                AND SUM_SEQ = (
                SELECT MAX(SUM_SEQ)
                FROM ECSCSM_ECTBSM
                WHERE PID = ?
                AND SUM_SYUBETU = '01'
                AND NOW_KA = ?
                );
                """
            cursor.execute(select_hospitalization_sql, 
                           pid, department_code, 
                           pid, department_code)
            rows = cursor.fetchone()
            if row is None:
                print("サマリ管理テーブルから入院日と退院日を取得できませんでした。pid:" + str(pid) + ", now_ka:" + department_code)
                return {"name":pid_name,
                        "hospitalization_date":"-",
                        "discharge_date":"-"}
            hospitalization_date = rows[0]
            discharge_date = rows[1]
            hospitalization_date_str = DateTimeConverter.int_2_str(hospitalization_date, True)
            discharge_date_str = DateTimeConverter.int_2_str(discharge_date, True)

            return {"name":pid_name,
                    "hospitalization_date":hospitalization_date_str,
                    "discharge_date":discharge_date_str}

            

