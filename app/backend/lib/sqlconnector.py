# SQL Database への接続を行うクラス
import os
import time
import pyodbc, struct
from azure.identity import DefaultAzureCredential

SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h

class SQLConnector:
    def __init__(self, azure_credential=None):
        self._azure_credential = azure_credential
        self._sql_connection_string = os.environ.get('SQL_CONNECTION_STRING')
        self._is_sql_authentication_is_aad = True

        if os.environ.get('SQL_AUTHENTICATION') is None:
            self._is_sql_authentication_is_aad = False
        elif os.environ.get('SQL_AUTHENTICATION') != 'ActiveDirectoryMsi':
            self._is_sql_authentication_is_aad = False
        
        if self._is_sql_authentication_is_aad:
            self._connect_by_add()

    def _connect_by_add(self):
            if self._azure_credential is None:
                self._azure_credential = DefaultAzureCredential()
            token_bytes = self._azure_credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
            self._token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)

    def get_conn(self):
        if self._is_sql_authentication_is_aad:
            try:
                return pyodbc.connect(self._sql_connection_string, 
                                    attrs_before={SQL_COPT_SS_ACCESS_TOKEN: self._token_struct})
            except Exception as e:
                print(e)
                print('Retry connect to SQL Server')
                self._connect_by_add()
                return pyodbc.connect(self._sql_connection_string, 
                                    attrs_before={SQL_COPT_SS_ACCESS_TOKEN: self._token_struct})

        else:
            try:
                return pyodbc.connect(self._sql_connection_string)
            except Exception as e:
                print(e)
                print('Retry connect to SQL Server')
                time.sleep(5)
                return pyodbc.connect(self._sql_connection_string)
