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
num_tokens_for_soap = int(gptconfigmanager.get_value("MAX_TOTAL_TOKENS")) - int(gptconfigmanager.get_value("TOKEN_NUM_FOR_QUESTION"))

# 中間データから、指定した条件のレコードのId を取得する
def get_intermediate_soap_id(sql_connector:SQLConnector, kind:str, original_doc_no:str) -> int:
    # SQL Server に接続する
    with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
        # レコードを取得する
        select_sql = """SELECT Id FROM IntermediateSOAP
            WHERE IsDeleted = 0
            AND SoapKind = ?
            AND OriginalDocNo = ?"""
        cursor.execute(select_sql, kind, original_doc_no)
        rows = cursor.fetchall() 
        if len(rows) < 1:
            return -1
        return rows[0][0]

def insert_intermediate_soap(sql_connector:SQLConnector, data_list:[]) -> None:
    # SQL Server に接続する
    with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
        # レコードを挿入する
        insert_sql = """
            INSERT INTO IntermediateSOAP (
                OriginalDocNo, DuplicateSourceDataId, Pid, DocDate, SoapKind, DocData, 
                CreatedBy, UpdatedBy, CreatedDateTime, UpdatedDateTime, IsDeleted)  
                VALUES (?, ?, ?, ?, ?, ?, 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0)"""
        cursor.executemany(insert_sql, data_list)
        cnxn.commit()

# 中間データ作成
def create_intermediate_soap_row(pid:str,
                                 kind:str, 
                                 pre_soap:DoctorsNoteParser, 
                                 current_soap:DoctorsNoteParser, 
                                 doc_date:int, last_doc_date:int, 
                                 original_doc_no:str, 
                                 pre_doc_no:str):
    # 相対→絶対日時変換
    #pre = DateTimeConverter.relative_datetime_2_absolute_datetime(pre_soap.get(kind), last_doc_date)
    #current = DateTimeConverter.relative_datetime_2_absolute_datetime(current_soap.get(kind), doc_date)
    # 重複記述削除
    current = Deduplicator.deduplicate(pre, current)
    duplicate_source_data_id = get_intermediate_soap_id(sql_connector, kind, pre_doc_no)
    if duplicate_source_data_id < 0:
        duplicate_source_data_id = None
    data = (original_doc_no, duplicate_source_data_id, pid, doc_date, kind, current)
    return data
    # OriginalDocNo, DuplicateSourceDataId, Pid, DocDate, SoapKind, DocData

# 中間データ作成
def create_intermediate_soap(sql_connector:SQLConnector, 
                             pid:str,
                             last_doc_no:str,
                             last_doc_date:int,
                             last_original_doc_datax:str) -> None:
    # SQL Server に接続する
    with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
        # まだ中間データが作成されていないレコードを取得する
        select_datax_sql = """SELECT EXTBDH1.DOCDATE, EXTBDH1.DOC_NO, EXTBDC1.DOC_DATAX FROM EXTBDC1 
            INNER JOIN EXTBDH1 
            ON EXTBDC1.DOC_NO = EXTBDH1.DOC_NO
            AND EXTBDH1.DOC_K = ? 
            AND EXTBDH1.ACTIVE_FLG = 1 
            AND EXTBDC1.ACTIVE_FLG = 1 
            AND EXTBDH1.PID = ?
            AND EXTBDH1.DOCDATE > ?
            ORDER BY EXTBDH1.DOCDATE"""
        cursor.execute(select_datax_sql,'MD01', pid)

        # レコードを取得する
        rows = cursor.fetchall()
    if len(rows) < 1:
        print("中間データを作成する対象のレコードがありません。")
        return

    pre_soap = DoctorsNoteParser(last_original_doc_datax)
    rows_to_insert = []
    for row in rows:
        doc_date = row[0]
        doc_no = row[1]
        doc_datax = row[2]
        print("中間データを作成します。doc_no:" + doc_no)
        current_soap = DoctorsNoteParser(doc_datax)
        data = create_intermediate_soap_row(pid,
                                     "s", 
                                     pre_soap, 
                                     current_soap, 
                                     doc_date, 
                                     last_doc_date, 
                                     doc_no, 
                                     last_doc_no)
        rows_to_insert.append(data)
        data = create_intermediate_soap_row(pid,
                                     "o", 
                                     pre_soap, 
                                     current_soap, 
                                     doc_date, 
                                     last_doc_date, 
                                     doc_no, 
                                     last_doc_no)
        rows_to_insert.append(data)
        data = create_intermediate_soap_row(pid,
                                     "a", 
                                     pre_soap, 
                                     current_soap, 
                                     doc_date, 
                                     last_doc_date, 
                                     doc_no, 
                                     last_doc_no)
        rows_to_insert.append(data)
        data = create_intermediate_soap_row(pid,
                                     "p", 
                                     pre_soap, 
                                     current_soap, 
                                     doc_date, 
                                     last_doc_date, 
                                     doc_no, 
                                     last_doc_no)
        rows_to_insert.append(data)
        data = create_intermediate_soap_row(pid,
                                     "b", 
                                     pre_soap, 
                                     current_soap, 
                                     doc_date, 
                                     last_doc_date, 
                                     doc_no, 
                                     last_doc_no)
        rows_to_insert.append(data)

        insert_intermediate_soap(sql_connector, rows_to_insert)
        
# 最新の中間データを取得する
def get_last_intermediate_soap(sql_connector:SQLConnector) -> None:

    with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
        # 患者に該当する最新の中間データ日付を取得する
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
                continue
            else:
                print("中間データを作成します。")
                create_intermediate_soap(sql_connector, pid, last_original_doc_no, last_doc_date, last_original_doc_datax)

# 最新の中間データを取得する
get_last_intermediate_soap(sql_connector)




