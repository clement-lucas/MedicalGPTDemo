#############################################
# soapmanager の呼び出し用テストファイルです。
#############################################
########
# 使い方
# app\backend に移動し、以下のコマンドを実行します
# py .\soapmanager_test.py '{your .env file path}'
# ex)
# HL-MedicalGPTDemo\app\backend> py .\soapmanager_test.py 'C:\HL-MedicalGPTDemo\.azure\HealthcareGPTdemo-dev-GPT35\.env'
########


import os
import sys
import openai
import time
from dotenv import load_dotenv
from lib.gptconfigmanager import GPTConfigManager
from lib.sqlconnector import SQLConnector
from azure.identity import DefaultAzureCredential
from lib.soapmanager import SOAPManager

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

#soap = SOAPManager.get_values(sql_connector, '001', '8888000059', 'soapb', 0, 1, 0, 1)
soap = SOAPManager.get_values(sql_connector, '001', '8888001192', 'soapb', 0, 1, 0, 1)
print(soap[0])
print(soap[1])
