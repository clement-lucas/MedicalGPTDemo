from approaches.approach import Approach
from lib.sqlconnector import SQLConnector

class GetIcd10MasterApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
    
    # codeLevel: 0:大項目, 1:中項目, 2:小項目
    # parentCode: 取得対象とする上位項目コード
    def run(self, codeLevel:int, parentCode:str) -> any:

        # SQL Server に接続する
        # 接続文字列を取得する
        with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:

            # SQL Server から履歴情報を取得する
            if parentCode == "":
                cursor.execute("""
                    SELECT Icd10Code
                        ,Caption
                        FROM Icd10Master
                        WHERE IsDeleted = 0
                        AND CodeLevel = ?
                        ORDER BY Icd10Code
                        """, codeLevel)
            else:
                cursor.execute("""
                    SELECT Icd10Code
                        ,Caption
                        FROM Icd10Master
                        WHERE IsDeleted = 0
                        AND CodeLevel = ?
                        AND ParentIcd10Code = ?
                        ORDER BY Icd10Code
                        """, codeLevel, parentCode)

            rows = cursor.fetchall()

            ret = []
            for row in rows:
                ret.append({"icd10_code":row[0], "caption":row[1]})

            if len(ret) == 0:
                raise Exception("Icd10Master not found. codeLevel:" + str(codeLevel) + ", parentCode:" + parentCode + ". ")
            return {"records":ret}
   
        

