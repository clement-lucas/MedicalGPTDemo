#############################################
# 中間データを作成するバッチファイル
#############################################
########
# 使い方
# app\backend に移動し、以下のコマンドを実行します
# py .\createintermediatesoap_bat.py '{your .env file path}'
# ex)
# HL-MedicalGPTDemo\app\backend> py .\createintermediatesoap_bat.py 'C:\HL-MedicalGPTDemo\.azure\HealthcareGPTdemo-dev-GPT35\.env'
########


import os
import sys
import openai
import time
from dotenv import load_dotenv
from lib.gptconfigmanager import GPTConfigManager
from lib.sqlconnector import SQLConnector
from azure.identity import DefaultAzureCredential
from parser.doctorsnoteparser import DoctorsNoteParser
from lib.deduplicator import Deduplicator
from lib.datetimeconverter import DateTimeConverter

NOT_HIT_ORIGINAL_DOC_NO = 'NOT_HIT_ORIGINAL_DOC_NO'

# 第一パラメーター：.envファイルのパスを指定します
# パラメーター取得
args = sys.argv

print(args)
print("第1引数：" + args[1])

# ファイルパスを指定して、.envファイルの内容を読み込みます
load_dotenv(dotenv_path=args[1])

AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE") or "myopenai"
AZURE_OPENAI_AUTHENTICATION=os.environ.get("AZURE_OPENAI_AUTHENTICATION") or "ActiveDirectory"
is_openal_ad_auth = False if AZURE_OPENAI_AUTHENTICATION == "ApiKey" else True
AZURE_OPENAI_KEY=os.environ.get("AZURE_OPENAI_KEY") or ""
if (not is_openal_ad_auth and not AZURE_OPENAI_KEY):
    raise Exception("AZURE_OPENAI_KEY is required")
azure_credential = DefaultAzureCredential()
sql_connector = SQLConnector(azure_credential)

gptconfigmanager = GPTConfigManager(sql_connector)
def ensure_openai_token():
    if not is_openal_ad_auth:
        return
    global openai_token
    if openai_token.expires_on < int(time.time()) - 60:
        openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
        openai.api_key = openai_token.token

openai.api_base = f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com"
openai.api_version = "2023-05-15"

if is_openal_ad_auth:
    print("Using Azure AD authentication for OpenAI")
    openai.api_type = "azure_ad"
    openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
    openai.api_key = openai_token.token
else:
    print("Using API key authentication for OpenAI")
    openai.api_type = "azure"
    openai.api_key = AZURE_OPENAI_KEY

gpt_deployment = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT")

def insert_intermediate_soap(cnxn, data_list:[]) -> None:
    # SQL Server に接続する
    with cnxn.cursor() as cursor:
        # レコードを挿入する
        insert_sql = """INSERT INTO IntermediateSOAP (
                OriginalDocNo, DuplicateSourceDataId, Pid, DocDate, SoapKind, IntermediateData, 
                CreatedBy, UpdatedBy, CreatedDateTime, UpdatedDateTime, IsDeleted)  
            VALUES (
                ?, 
                COALESCE((SELECT TOP 1 Id FROM IntermediateSOAP
                    WHERE IsDeleted = 0
                    AND SoapKind = ?
                    AND OriginalDocNo = ?
                    ORDER BY Id DESC), NULL), 
                ?, ?, ?, ?, 
                'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0)
            """

        cnxn.autocommit = False
        try:
            cursor.executemany(insert_sql, data_list)
        except Exception as e:
            print(e)
            cnxn.rollback()
            raise
        cnxn.commit()

# 3. 中間データを作成する。
def create_intermediate_soap_row(pid:str,
                                 kind:str, 
                                 current_doc_no:str, 
                                 current_soap:DoctorsNoteParser, 
                                 current_doc_date:int,
                                 last_doc_no:str, 
                                 last_soap:DoctorsNoteParser):
    last_text_soap = ""
    if last_soap is None:
        last_text_soap = None
    else:
        last_text_soap = last_soap.get(kind)
    current_text_soap = current_soap.get(kind)
    if current_text_soap is None or current_text_soap == "":
        return None
    # 相対→絶対日時変換
    # last = DateTimeConverter.relative_datetime_2_absolute_datetime(last, last_doc_date)
    # current = DateTimeConverter.relative_datetime_2_absolute_datetime(current, doc_date)
    # 重複記述削除
    original_doc_no = NOT_HIT_ORIGINAL_DOC_NO
    if last_text_soap is not None:
        deduplicated = Deduplicator.deduplicate(current_text_soap, last_text_soap)
        found = deduplicated[0]
        if found:
            print("重複記述あり。doc_no:" + current_doc_no)
            current_text_soap = deduplicated[1]
            original_doc_no = last_doc_no
    data = (current_doc_no, kind, original_doc_no, 
            pid, current_doc_date, kind, current_text_soap)
    #data = (current_doc_no, kind, original_doc_no, pid, current_doc_date, kind, current_text_soap)
    return data

# 中間データ作成
def create_intermediate_soap(cnxn,
                             pid:str,
                             last_doc_no:str,
                             last_doc_date:int,
                             last_original_doc_datax:str) -> None:
    # 2. 患者ごとの未作成の中間データのリストを取得する。
    with cnxn.cursor() as cursor:
        select_datax_sql = """SELECT EXTBDH1.DOCDATE, EXTBDH1.DOC_NO, EXTBDC1.DOC_DATAX FROM EXTBDC1 
            INNER JOIN EXTBDH1 
            ON EXTBDC1.DOC_NO = EXTBDH1.DOC_NO
            AND EXTBDH1.DOC_K = ? 
            AND EXTBDH1.ACTIVE_FLG = 1 
            AND EXTBDC1.ACTIVE_FLG = 1 
            AND EXTBDH1.PID = ?
            AND EXTBDH1.DOCDATE > ?
            ORDER BY EXTBDH1.DOCDATE"""
        cursor.execute(select_datax_sql,'MD01', pid, last_doc_date)

        # レコードを取得する
        rows = cursor.fetchall()
    if len(rows) < 1:
        print("中間データを作成する対象のレコードがありません。")
        return

    if last_original_doc_datax is None or last_original_doc_datax == "":
        last_soap = None
    else:
        last_soap = DoctorsNoteParser(last_original_doc_datax)
    for row in rows:
        current_doc_date = row[0]
        current_doc_no = row[1]
        current_doc_datax = row[2]
        # 3. 中間データを作成する。
        print("中間データを作成します。doc_no:" + current_doc_no)
        rows_to_insert = []
        current_soap = DoctorsNoteParser(current_doc_datax)
        data = create_intermediate_soap_row(pid, "s", 
            current_doc_no, current_soap, current_doc_date,
            last_doc_no, last_soap)
        if data is not None:
            rows_to_insert.append(data)
        data = create_intermediate_soap_row(pid, "o",
            current_doc_no, current_soap, current_doc_date,
            last_doc_no, last_soap)
        if data is not None:
            rows_to_insert.append(data)
        data = create_intermediate_soap_row(pid, "a",
            current_doc_no, current_soap, current_doc_date,
            last_doc_no, last_soap)
        if data is not None:
            rows_to_insert.append(data)
        data = create_intermediate_soap_row(pid, "p",
            current_doc_no, current_soap, current_doc_date,
            last_doc_no, last_soap)
        if data is not None:
            rows_to_insert.append(data)
        data = create_intermediate_soap_row(pid, "b",
            current_doc_no, current_soap, current_doc_date,
            last_doc_no, last_soap)
        if data is not None:
            rows_to_insert.append(data)

        if len(rows_to_insert) > 0:
            # 4.中間データファイルから、重複比較元の DOC_NOと対応するIDを取得し、新しいレコード追加する。
            insert_intermediate_soap(cnxn, rows_to_insert)

        last_soap = current_soap
        last_doc_no = current_doc_no
        
# 1. 患者ごとの最新の中間データを取得する
def get_last_intermediate_soap(sql_connector:SQLConnector) -> None:

    with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
        # 最新の中間データを取得する
        cursor.execute("""SELECT DISTINCT e.PID, COALESCE(s.LastDocDate, 0) AS LastDocDate, COALESCE(s.LastOriginalDocNo, '') AS LastOriginalDocNo, COALESCE(c.DOC_DATAX, '') AS LastOriginalDocDataX
            FROM [dbo].[EXTBDH1] e
            LEFT JOIN (
                SELECT t.Pid, t.DocDate AS LastDocDate, t.OriginalDocNo AS LastOriginalDocNo
                FROM (
                    SELECT Pid, DocDate, OriginalDocNo,
                        ROW_NUMBER() OVER (PARTITION BY Pid ORDER BY DocDate DESC) AS rn
                    FROM IntermediateSOAP
                    WHERE IsDeleted = 0
                ) t
                WHERE t.rn = 1
            ) s ON e.PID = s.Pid
            LEFT JOIN EXTBDC1 c ON s.LastOriginalDocNo = c.DOC_NO
            WHERE e.ACTIVE_FLG = 1
            """)
        rows = cursor.fetchall() 

        for row in rows:
            pid = row[0]
            last_doc_date = row[1]
            last_original_doc_no = row[2]
            last_original_doc_datax = row[3]
            
            print("PID:" + str(pid))
            if last_doc_date > 0:
                print("中間データあり。最新の DocDate：" + str(last_doc_date))
            else:
                print("中間データを作成します。")
            
            create_intermediate_soap(cnxn, pid, 
                                     last_original_doc_no, 
                                     last_doc_date,
                                     last_original_doc_datax)

# 1. 患者ごとの最新の中間データを取得する
get_last_intermediate_soap(sql_connector)




