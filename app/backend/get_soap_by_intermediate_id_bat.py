#############################################
# SOAPの内容を参照するバッチファイル
#############################################
########
# 使い方
# app\backend に移動し、以下のコマンドを実行します
# py .\get_soap_by_intermediate_id_bat.py '{your .env file path} {参照したい中間データテーブルのid}'
# ex)
# HL-MedicalGPTDemo\app\backend> py .\get_soap_by_intermediate_id_bat.py 'C:\HL-MedicalGPTDemo\.azure\HealthcareGPTdemo-dev-GPT35\.env'
########


import os
import sys
from dotenv import load_dotenv
from lib.sqlconnector import SQLConnector
from azure.identity import DefaultAzureCredential


NOT_HIT_ORIGINAL_DOC_NO = 'NOT_HIT_ORIGINAL_DOC_NO'

# 第一パラメーター：.envファイルのパスを指定します
# パラメーター取得
args = sys.argv

print(args)
print("第1引数：" + args[1])
print("第2引数：" + args[2])
id = args[2]

# ファイルパスを指定して、.envファイルの内容を読み込みます
load_dotenv(dotenv_path=args[1])
azure_credential = DefaultAzureCredential()
sql_connector = SQLConnector(azure_credential)

# SQL Server に接続する
with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
        sql = """SELECT IntermediateData
            FROM [dbo].[IntermediateSOAP]
            WHERE Id = ?"""

        cursor.execute(sql, id)
        rows = cursor.fetchall()
        if len(rows) == 0:
            print("Not found")
            exit()
        for row in rows:
            print(row[0])
