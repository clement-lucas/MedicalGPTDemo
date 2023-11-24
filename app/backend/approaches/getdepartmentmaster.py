from approaches.approach import Approach
from lib.sqlconnector import SQLConnector

class GetDepartmentMasterApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
    
    def run(self) -> any:
        # SQL Server に接続する
        # 接続文字列を取得する
        with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:

            # SQL Server から情報を取得する
            cursor.execute("""
                SELECT DepartmentCode
                    ,DepartmentName
                    FROM DepartmentMaster
                    WHERE IsDeleted = 0
                    ORDER BY DepartmentCode
                    """)
            rows = cursor.fetchall()

            ret = []
            for row in rows:
                ret.append({"department_code":row[0], "department_name":row[1]})

            if len(ret) == 0:
                raise Exception("DepartmentMaster not found.")
            return {"records":ret}
   
        

