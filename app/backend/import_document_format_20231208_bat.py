#############################################
# 旧 DocumentFormat テーブルのデータを新テーブルにインポートする
#############################################
########
# 使い方
# app\backend に移動し、以下のコマンドを実行します
# py .\import_document_format_20231208_bat.py '{your .env file path}'
# ex)
# HL-MedicalGPTDemo\app\backend> py .\import_document_format_20231208_bat.py 'C:\HL-MedicalGPTDemo\.azure\HealthcareGPTdemo-dev-GPT35\.env'
########


import sys
from dotenv import load_dotenv
from lib.sqlconnector import SQLConnector
from azure.identity import DefaultAzureCredential

# 第一パラメーター：.envファイルのパスを指定します
# パラメーター取得
args = sys.argv

print(args)
print("第1引数：" + args[1])

# ファイルパスを指定して、.envファイルの内容を読み込みます
load_dotenv(dotenv_path=args[1])
azure_credential = DefaultAzureCredential()
sql_connector = SQLConnector(azure_credential)

# SQL Server に接続する
with SQLConnector().get_conn() as cnxn, cnxn.cursor() as cursor:
    # 旧テーブルからデータを取得する
    select_document_format_sql = """
        SELECT [Id]
            ,[IsMaster]
            ,[UserId]
            ,[DocumentName]
            ,[GPTModelName]
            ,[Kind]
            ,[OrderNo]
            ,[CategoryName]
            ,[Temperature]
            ,[Question]
            ,[QuestionSuffix]
            ,[ResponseMaxTokens]
            ,[TargetSoapRecords]
            ,[UseAllergyRecords]
            ,[UseDischargeMedicineRecords]
            ,[CreatedBy]
            ,[UpdatedBy]
            ,[CreatedDateTime]
            ,[UpdatedDateTime]
            ,[IsDeleted]
        FROM [dbo].[DocumentFormat]"""
    cursor.execute(select_document_format_sql)
    rows = cursor.fetchall()
    for row in rows:
        id = row[0]
        is_master = row[1]
        user_id = row[2]
        document_name = row[3]
        gpt_model_name = row[4]
        kind = row[5]
        order_no = row[6]
        category_name = row[7]
        temperature = row[8]
        question = row[9]
        question_suffix = row[10]
        response_max_tokens = row[11]
        target_soap_records = row[12]
        use_allergy_records = row[13]
        use_discharge_medicine_records = row[14]
        created_by = row[15]
        updated_by = row[16]
        created_date_time = row[17]
        updated_date_time = row[18]
        is_deleted = row[19]
        
        new_user_id = ""
        if user_id is None:
            new_user_id = user_id
        else:
            new_user_id = user_id.replace('slot', 'user')

        new_index_name = ""
        if is_master == 1:
            new_index_name = "マスターファイル"
            new_user_id = "SYSTEM"
        else:
            if user_id is None:
                new_index_name = 'Import from NO USER'
            else:
                new_index_name = 'Import from ' + user_id

        # 新テーブルにデータを登録する
        if kind == 0:
            insert_document_format_sql = """
                INSERT INTO [dbo].[DocumentFormatIndex]
                    ([IsMaster]
                    ,[IndexName]
                    ,[DocumentName]
                    ,[GPTModelName]
                    ,[CreatedBy]
                    ,[UpdatedBy]
                    ,[CreatedDateTime]
                    ,[UpdatedDateTime]
                    ,[IsDeleted])
                VALUES
                    (?
                    ,?
                    ,?
                    ,?
                    ,?
                    ,?
                    ,?
                    ,?
                    ,?)
            ;"""
            cursor.execute(insert_document_format_sql,
                        is_master,
                        new_index_name,
                            document_name,
                            gpt_model_name,
                                new_user_id,
                                new_user_id,
                                created_date_time,
                                updated_date_time,
                                is_deleted)
            cursor.commit()

        # 新テーブルにデータを登録する
        insert_document_format_sql = """
            INSERT INTO [dbo].[DocumentFormatData]
                ([IsMaster]
                ,[IndexId]
                ,[Kind]
                ,[OrderNo]
                ,[CategoryName]
                ,[Temperature]
                ,[Question]
                ,[QuestionSuffix]
                ,[ResponseMaxTokens]
                ,[TargetSoapRecords]
                ,[UseAllergyRecords]
                ,[UseDischargeMedicineRecords]
                ,[StartDayToUseSoapRangeAfterHospitalization]
                ,[UseSoapRangeDaysAfterHospitalization]
                ,[StartDayToUseSoapRangeBeforeDischarge]
                ,[UseSoapRangeDaysBeforeDischarge]
                ,[CreatedBy]
                ,[UpdatedBy]
                ,[CreatedDateTime]
                ,[UpdatedDateTime]
                ,[IsDeleted])
            VALUES
                (?
                ,(SELECT MAX(IndexId) FROM DocumentFormatIndex)
                ,?
                ,?
                ,?
                ,?
                ,?
                ,?
                ,?
                ,?
                ,?
                ,?
                ,0
                ,3
                ,0
                ,3
                ,?
                ,?
                ,?
                ,?
                ,?)
            ;"""
        
        cursor.execute(insert_document_format_sql,
                       is_master,
                       kind,
                       order_no,
                       category_name,
                       temperature,
                       question,
                       question_suffix,
                       response_max_tokens,
                       target_soap_records,
                       use_allergy_records,
                       use_discharge_medicine_records,
                       new_user_id,
                       new_user_id,
                       created_date_time,
                       updated_date_time,
                       is_deleted)
        cursor.commit()

