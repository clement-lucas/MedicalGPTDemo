#############################################
# DOC_NO を指定して SOAP の内容を参照するバッチファイル
#############################################
########
# 使い方
# app\backend に移動し、以下のコマンドを実行します
# py .\get_soap_by_doc_no_bat.py '{your .env file path} {参照したいDOC_NO}'
# ex)
# HL-MedicalGPTDemo\app\backend> py .\get_soap_by_doc_no_bat.py 'C:\HL-MedicalGPTDemo\.azure\HealthcareGPTdemo-dev-GPT35\.env' '0A497E602D52782014030315222700'
########


import os
import sys
from dotenv import load_dotenv
from lib.sqlconnector import SQLConnector
from azure.identity import DefaultAzureCredential
from parser.doctorsnoteparser import DoctorsNoteParser


NOT_HIT_ORIGINAL_DOC_NO = 'NOT_HIT_ORIGINAL_DOC_NO'

# 第一パラメーター：.envファイルのパスを指定します
# パラメーター取得
args = sys.argv

print(args)
print("第1引数：" + args[1])
print("第2引数：" + args[2])
doc_no = args[2]

# ファイルパスを指定して、.envファイルの内容を読み込みます
load_dotenv(dotenv_path=args[1])
azure_credential = DefaultAzureCredential()
sql_connector = SQLConnector(azure_credential)

# SQL Server に接続する
with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
        sql = """SELECT EXTBDH1.DOCDATE, EXTBDC1.DOC_DATAX FROM EXTBDC1 
            INNER JOIN EXTBDH1 
            ON EXTBDC1.DOC_NO = EXTBDH1.DOC_NO
            AND EXTBDH1.DOC_NO = ?
            AND EXTBDH1.ACTIVE_FLG = 1 
            AND EXTBDC1.ACTIVE_FLG = 1 
            ORDER BY EXTBDH1.DOCDATE"""

        cursor.execute(sql, doc_no)
        rows = cursor.fetchall()
        if len(rows) == 0:
            print("Not found")
            exit()
        for row in rows:
            print(row[0])

            print("DOCDATE:" + str(row[0]))

            parser = DoctorsNoteParser(row[1])
            print("S:")
            print(parser.S)
            print("O:")
            print(parser.O)
            print("A:")
            print(parser.A)
            print("P:")
            print(parser.P)
            print("#:")
            print(parser.B)
