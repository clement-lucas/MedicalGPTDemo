from lib.sqlconnector import SQLConnector

# GPTConfig テーブルの内容を取得するクラス
class GPTConfigManager:
    def get_value(self, key: str):

        if key in self._config:
            return self._config[key]
        else:
            return None

    def __init__(self, sql_connector:SQLConnector) -> None:
        self._sql_connector = sql_connector
        # SQL Server に接続する
        with self._sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:

            select_data_sql = """SELECT ConfigKey, ConfigValue FROM GPTConfig 
                WHERE IsDeleted = 0"""

            cursor.execute(select_data_sql)
            rows = cursor.fetchall() 
        
        self._config = {}
        for row in rows:
            self._config[row[0]] = row[1]

