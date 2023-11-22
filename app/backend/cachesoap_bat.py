########
# 使い方
# app\backend に移動し、以下のコマンドを実行します
# py .\cachesoap_bat.py '{your .env file path}'
# ex)
# HL-MedicalGPTDemo\app\backend> py .\cachesoap_bat.py 'C:\HL-MedicalGPTDemo\.azure\HealthcareGPTdemo-dev-GPT35\.env'
########


import os
import sys
import openai
import time
from dotenv import load_dotenv
from lib.soapmanager import SOAPManager
from lib.gptconfigmanager import GPTConfigManager
from lib.sqlconnector import SQLConnector
from azure.identity import DefaultAzureCredential

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


with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
    # SQL Server から患者情報を取得する
    cursor.execute("""SELECT DISTINCT PID
        FROM [dbo].[EXTBDH1] WHERE ACTIVE_FLG = 1""")
    rows = cursor.fetchall() 

for row in rows:
    print("PID:" + str(row[0]))
    soap_manager = SOAPManager(sql_connector, 'SYSTEM', gptconfigmanager, row[0], 
        gpt_deployment, num_tokens_for_soap)

