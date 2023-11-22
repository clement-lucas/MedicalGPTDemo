# SQL Database への接続を行うクラス
import os
import pyodbc, struct
from azure.identity import DefaultAzureCredential

SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h

class SQLConnector:
    def __init__(self, azure_credential=None):
        if azure_credential is None:
            azure_credential = DefaultAzureCredential()

        self._azure_credential = azure_credential
        self._sql_connection_string = os.environ.get('SQL_CONNECTION_STRING')
        self._is_sql_authentication_is_aad = True

        if os.environ.get('SQL_AUTHENTICATION') is None:
            self._is_sql_authentication_is_aad = False
        elif os.environ.get('SQL_AUTHENTICATION') != 'ActiveDirectoryMsi':
            self._is_sql_authentication_is_aad = False
        
        if self._is_sql_authentication_is_aad:
            token_bytes = self._azure_credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
            self._token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)

    def get_conn(self):
        if self._is_sql_authentication_is_aad:
            return pyodbc.connect(self._sql_connection_string, 
                                  attrs_before={SQL_COPT_SS_ACCESS_TOKEN: self._token_struct})

        return pyodbc.connect(self._sql_connection_string)
