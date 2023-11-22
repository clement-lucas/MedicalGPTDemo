########
# 使い方
# app\backend に移動し、以下のコマンドを実行します
# py .\cachesoap_bat.py '{your .env file path}'
# ex)
# HL-MedicalGPTDemo\app\backend> py .\cachesoap_bat.py 'C:\HL-MedicalGPTDemo\.azure\HealthcareGPTdemo-dev-GPT35\.env'
########

import os
import sys
from dotenv import load_dotenv
from lib.sqlconnector import SQLConnector
from lib.documentformatmanager import DocumentFormatManager

# 第一パラメーター：.envファイルのパスを指定します
# パラメーター取得
args = sys.argv

print(args)
print("第1引数：" + args[1])

# ファイルパスを指定して、.envファイルの内容を読み込みます
load_dotenv(dotenv_path=args[1])

sql_connector = SQLConnector()

def add_document_format(is_master:bool, 
                        user_id: str,
                        department_code: str, 
                        icd10_code: str,
                        kind: int, 
                        order_no: int,
                        question: str, 
                        question_suffix: str):
    gpt_model_name = os.getenv("AZURE_GPT_MODEL_NAME")
    if gpt_model_name is None:
        gpt_model_name = "gpt-35-turbo"
    with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
        # ドキュメントフォーマットの登録
        insert_document_format_sql = """INSERT INTO DocumentFormat
            ( 
                IsMaster,
                UserId,
                DepartmentCode,
                Icd10Code,
                DocumentName,
                GPTModelName,
                Kind, 
                OrderNo, 
                CategoryName, 
                Temperature,
                Question, 
                QuestionSuffix,
                ResponseMaxTokens, 
                TargetSoapRecords, 
                UseAllergyRecords, 
                UseDischargeMedicineRecords,
                CreatedBy,
                UpdatedBy,
                CreatedDateTime,
                UpdatedDateTime,
                IsDeleted
            )
            VALUES
            ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, GETDATE(), GETDATE(), 0)"""

        rows_to_insert = []
        target_soap = "soapb"
        rows_to_insert.append((
            1 if is_master else 0,
            user_id,
            department_code,
            icd10_code,
            '退院時サマリ',
            gpt_model_name,
            kind,
            order_no,
            'TEST_CATEGORY',
            0.01,
            question,
            question_suffix,
            1000,
            target_soap,
            'TEST',
            'TEST'
        ))
        cursor.executemany(insert_document_format_sql, rows_to_insert)

        # トランザクションのコミット
        cnxn.commit()


# SQL Server に接続する
with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
    delete_test_rows_sql = """DELETE FROM DocumentFormat WHERE CreatedBy = 'TEST'"""
    cursor.execute(delete_test_rows_sql)
    cnxn.commit()

try:
    # テストデータの登録
    add_document_format(1, "0000", "TEST_DPTMT", "0000", 0, 0, "q1", "sq1")
    add_document_format(1, "0000", "TEST_DPTMT", "0000", 1, 0, "q2", "sq2")
    add_document_format(1, "0000", "TEST_DPTMT", "0000", 1, 1, "q3", "sq3")
    add_document_format(1, "0000", "TEST_DPTMT", "0000", 2, 2, "", "")
    add_document_format(1, "0000", "TEST_DPTMT", "0000", 3, 3, "", "")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "0000", 0, 0, "q4", "sq4")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "0000", 1, 0, "q5", "sq5")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "0000", 1, 1, "q6", "sq6")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "0000", 2, 2, "", "")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "0000", 3, 3, "", "")
    add_document_format(1, "0000", "TEST_DPTMT", "A00-A09", 0, 0, "q7", "sq7")
    add_document_format(1, "0000", "TEST_DPTMT", "A00-A09", 1, 0, "q8", "sq8")
    add_document_format(1, "0000", "TEST_DPTMT", "A00-A09", 1, 1, "q9", "sq9")
    add_document_format(1, "0000", "TEST_DPTMT", "A00", 0, 0, "q10", "sq10")
    add_document_format(1, "0000", "TEST_DPTMT", "A00", 1, 0, "q11", "sq11")
    add_document_format(1, "0000", "TEST_DPTMT", "A00", 1, 1, "q12", "sq12")
    add_document_format(1, "0000", "TEST_DPTMT", "A00.1", 0, 0, "q13", "sq13")
    add_document_format(1, "0000", "TEST_DPTMT", "A00.1", 1, 0, "q14", "sq14")
    add_document_format(1, "0000", "TEST_DPTMT", "A00.1", 1, 1, "q15", "sq15")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "A00-A09", 0, 0, "q16", "sq16")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "A00-A09", 1, 0, "q17", "sq17")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "A00-A09", 1, 1, "q18", "sq18")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "A00", 0, 0, "q19", "sq19")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "A00", 1, 0, "q20", "sq20")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "A00", 1, 1, "q21", "sq21")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "A00.1", 0, 0, "q22", "sq22")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "A00.1", 1, 0, "q23", "sq23")
    add_document_format(0, "test_slot1", "TEST_DPTMT", "A00.1", 1, 1, "q24", "sq24")
    add_document_format(1, "0000", "0000", "A00-A09", 0, 0, "q25", "sq25")
    add_document_format(1, "0000", "0000", "A00-A09", 1, 0, "q26", "sq26")
    add_document_format(1, "0000", "0000", "A00-A09", 1, 1, "q27", "sq27")

    # 親リストの取得テスト
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "TEST_DPTMT", 
            "0000", 
            "TEST",
            False)
    parent_list = document_format_manager.parent_list
    if len(parent_list) != 0:
        raise Exception("parent_list is not empty")

    # 親リストの取得テスト
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "TEST_DPTMT", 
            "B98.1", 
            "TEST",
            False)
    parent_list = document_format_manager.parent_list
    if len(parent_list) != 2:
        raise Exception("parent_list is not empty")
    if parent_list[0] != "B98":
        raise Exception("parent_list[0] is not B98")
    if parent_list[1] != "B95-B98":
        raise Exception("parent_list[1] is not B95-B98")

    # 親リストの取得テスト
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "TEST_DPTMT", 
            "B98", 
            "TEST",
            False)
    parent_list = document_format_manager.parent_list
    if len(parent_list) != 1:
        raise Exception("parent_list is not empty")
    if parent_list[0] != "B95-B98":
        raise Exception("parent_list[0] is not B95-B98")

    # ユーザーに該当あり、科に該当ありの時、force_master フラグが True であれば 科のマスターデータが取得できることを確認する
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "TEST_DPTMT", 
            "0000", 
            "test_slot1",
            True)
    system_constents = document_format_manager.get_system_contents()
    if system_constents[0] != "q1":
        raise Exception("system_constents is wrong.")
    if system_constents[1] != "sq1":
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 4:
        raise Exception("document_format doesn't have 4 rows")
    if rows[0][5] != "q2":
        raise Exception("constents is wrong.")
    if rows[0][6] != "sq2":
        raise Exception("constents is wrong.")
    if rows[1][5] != "q3":
        raise Exception("constents is wrong.")
    if rows[1][6] != "sq3":
        raise Exception("constents is wrong.")
    if rows[2][1] != 2:
        raise Exception("constents is wrong.")
    if rows[3][1] != 3:
        raise Exception("constents is wrong.")

    # ユーザーに該当あり、科に該当なしの時、force_master フラグが True であれば マスターデータが取得できることを確認する
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "WRONG_DPTMT", 
            "0000", 
            "test_slot1",
            True)
    system_constents = document_format_manager.get_system_contents()
    print(system_constents[0])
    print(system_constents[1])
    if len(system_constents[0]) < 24:
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 7:
        raise Exception("wrong rows count")
    if len(rows[1][5]) < 24:
        raise Exception("constents is wrong.")

    # ユーザーに該当なし、科に該当なしの時、マスタデータが取得できることを確認する    
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "WRONG_DPTMT", 
            "0000", 
            "NO_USER",
            False)
    system_constents = document_format_manager.get_system_contents()
    print(system_constents[0])
    print(system_constents[1])
    if len(system_constents[0]) < 24:
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 7:
        raise Exception("wrong rows count")
    if len(rows[1][5]) < 24:
        raise Exception("constents is wrong.")

    # ユーザーに該当なし、科に該当なしの時、マスタデータが取得できることを確認する    
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "WRONG_DPTMT", 
            "", 
            "NO_USER",
            False)
    system_constents = document_format_manager.get_system_contents()
    print(system_constents[0])
    print(system_constents[1])
    if len(system_constents[0]) < 24:
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 7:
        raise Exception("wrong rows count")
    if len(rows[1][5]) < 24:
        raise Exception("constents is wrong.")

    # ユーザーに該当なし、科に該当なしの時、マスタデータが取得できることを確認する    
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "WRONG_DPTMT", 
            "NO_ICD10", 
            "NO_USER",
            False)
    system_constents = document_format_manager.get_system_contents()
    print(system_constents[0])
    print(system_constents[1])
    if len(system_constents[0]) < 24:
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 7:
        raise Exception("wrong rows count")
    if len(rows[1][5]) < 24:
        raise Exception("constents is wrong.")

    # ユーザーに該当なし、科に該当ありの時、科のマスタデータが取得できることを確認する
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "TEST_DPTMT", 
            "0000", 
            "NO_USER",
            False)
    system_constents = document_format_manager.get_system_contents()
    if system_constents[0] != "q1":
        raise Exception("system_constents is wrong.")
    if system_constents[1] != "sq1":
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 4:
        raise Exception("document_format doesn't have 4 rows")
    if rows[0][5] != "q2":
        raise Exception("constents is wrong.")
    if rows[0][6] != "sq2":
        raise Exception("constents is wrong.")
    if rows[1][5] != "q3":
        raise Exception("constents is wrong.")
    if rows[1][6] != "sq3":
        raise Exception("constents is wrong.")
    if rows[2][1] != 2:
        raise Exception("constents is wrong.")
    if rows[3][1] != 3:
        raise Exception("constents is wrong.")

    # ユーザーに該当あり、科に該当ありの時、ユーザーのデータが取得できることを確認する
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "TEST_DPTMT", 
            "0000", 
            "test_slot1",
            False)
    system_constents = document_format_manager.get_system_contents()
    if system_constents[0] != "q4":
        raise Exception("system_constents is wrong.")
    if system_constents[1] != "sq4":
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 4:
        raise Exception("document_format doesn't have 4 rows")
    if rows[0][5] != "q5":
        raise Exception("constents is wrong.")
    if rows[0][6] != "sq5":
        raise Exception("constents is wrong.")
    if rows[1][5] != "q6":
        raise Exception("constents is wrong.")
    if rows[1][6] != "sq6":
        raise Exception("constents is wrong.")
    if rows[2][1] != 2:
        raise Exception("constents is wrong.")
    if rows[3][1] != 3:
        raise Exception("constents is wrong.")

    # ユーザーと科に該当あり、ICD10コードに該当ありの場合、当該レコードが取得できる。
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "TEST_DPTMT", 
            "A00-A09", 
            "test_slot1",
            False)
    system_constents = document_format_manager.get_system_contents()
    if system_constents[0] != "q16":
        raise Exception("system_constents is wrong.")
    if system_constents[1] != "sq16":
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 2:
        raise Exception("document_format doesn't have 4 rows")
    if rows[0][5] != "q17":
        raise Exception("constents is wrong.")
    if rows[0][6] != "sq17":
        raise Exception("constents is wrong.")
    if rows[1][5] != "q18":
        raise Exception("constents is wrong.")
    if rows[1][6] != "sq18":
        raise Exception("constents is wrong.")

    # ユーザーと科に該当あり、ICD10コードに該当なし、親コードに該当ありの場合、当該レコードが取得できる。
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "TEST_DPTMT", 
            "A01", 
            "test_slot1",
            False)
    system_constents = document_format_manager.get_system_contents()
    if system_constents[0] != "q16":
        raise Exception("system_constents is wrong.")
    if system_constents[1] != "sq16":
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 2:
        raise Exception("document_format doesn't have 4 rows")
    if rows[0][5] != "q17":
        raise Exception("constents is wrong.")
    if rows[0][6] != "sq17":
        raise Exception("constents is wrong.")
    if rows[1][5] != "q18":
        raise Exception("constents is wrong.")
    if rows[1][6] != "sq18":
        raise Exception("constents is wrong.")

    # ユーザーと科に該当あり、ICD10コードと親コードに該当なし、祖父母コードに該当ありの場合、当該レコードが取得できる。
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "TEST_DPTMT", 
            "A01.1", 
            "test_slot1",
            False)
    system_constents = document_format_manager.get_system_contents()
    if system_constents[0] != "q16":
        raise Exception("system_constents is wrong.")
    if system_constents[1] != "sq16":
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 2:
        raise Exception("wrong rows count")
    if rows[0][5] != "q17":
        raise Exception("constents is wrong.")
    if rows[0][6] != "sq17":
        raise Exception("constents is wrong.")
    if rows[1][5] != "q18":
        raise Exception("constents is wrong.")
    if rows[1][6] != "sq18":
        raise Exception("constents is wrong.")

    # ユーザーに該当なし、科に該当ありの時、科のマスタデータが取得できることを確認する
    # ICD10コード該当あり
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "TEST_DPTMT", 
            "A00-A09", 
            "NO_USER",
            False)
    system_constents = document_format_manager.get_system_contents()
    if system_constents[0] != "q7":
        raise Exception("system_constents is wrong.")
    if system_constents[1] != "sq7":
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 2:
        raise Exception("wrong rows count")
    if rows[0][5] != "q8":
        raise Exception("constents is wrong.")
    if rows[0][6] != "sq8":
        raise Exception("constents is wrong.")
    if rows[1][5] != "q9":
        raise Exception("constents is wrong.")
    if rows[1][6] != "sq9":
        raise Exception("constents is wrong.")

    # ユーザーに該当なし、科に該当ありの時、科のマスタデータが取得できることを確認する
    # ICD10コード該当なし、親コード該当あり
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "TEST_DPTMT", 
            "A01", 
            "NO_USER",
            False)
    system_constents = document_format_manager.get_system_contents()
    if system_constents[0] != "q7":
        raise Exception("system_constents is wrong.")
    if system_constents[1] != "sq7":
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 2:
        raise Exception("wrong rows count")
    if rows[0][5] != "q8":
        raise Exception("constents is wrong.")
    if rows[0][6] != "sq8":
        raise Exception("constents is wrong.")
    if rows[1][5] != "q9":
        raise Exception("constents is wrong.")
    if rows[1][6] != "sq9":
        raise Exception("constents is wrong.")

    # ユーザーに該当なし、科に該当ありの時、科のマスタデータが取得できることを確認する
    # ICD10コード該当なし、親コード該当なし、祖父母コード該当あり
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "TEST_DPTMT", 
            "A01.1", 
            "NO_USER",
            False)
    system_constents = document_format_manager.get_system_contents()
    if system_constents[0] != "q7":
        raise Exception("system_constents is wrong.")
    if system_constents[1] != "sq7":
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 2:
        raise Exception("wrong rows count")
    if rows[0][5] != "q8":
        raise Exception("constents is wrong.")
    if rows[0][6] != "sq8":
        raise Exception("constents is wrong.")
    if rows[1][5] != "q9":
        raise Exception("constents is wrong.")
    if rows[1][6] != "sq9":
        raise Exception("constents is wrong.")

    # ユーザーに該当なし、科に該当なしの時、マスタデータが取得できることを確認する
    # ICD10コード該当あり
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "WRONG_DPTMT", 
            "A00-A09", 
            "NO_USER",
            False)
    system_constents = document_format_manager.get_system_contents()
    if system_constents[0] != "q25":
        raise Exception("system_constents is wrong.")
    if system_constents[1] != "sq25":
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 2:
        raise Exception("wrong rows count")
    if rows[0][5] != "q26":
        raise Exception("constents is wrong.")
    if rows[0][6] != "sq26":
        raise Exception("constents is wrong.")
    if rows[1][5] != "q27":
        raise Exception("constents is wrong.")
    if rows[1][6] != "sq27":
        raise Exception("constents is wrong.")

    # ユーザーに該当なし、科に該当なしの時、マスタデータが取得できることを確認する
    # ICD10コード該当なし、親コード該当あり
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "WRONG_DPTMT", 
            "A01", 
            "NO_USER",
            False)
    system_constents = document_format_manager.get_system_contents()
    if system_constents[0] != "q25":
        raise Exception("system_constents is wrong.")
    if system_constents[1] != "sq25":
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 2:
        raise Exception("wrong rows count")
    if rows[0][5] != "q26":
        raise Exception("constents is wrong.")
    if rows[0][6] != "sq26":
        raise Exception("constents is wrong.")
    if rows[1][5] != "q27":
        raise Exception("constents is wrong.")
    if rows[1][6] != "sq27":
        raise Exception("constents is wrong.")

    # ユーザーに該当なし、科に該当なしの時、マスタデータが取得できることを確認する
    # ICD10コード該当なし、親コード該当なし、祖父母コード該当あり
    document_format_manager = DocumentFormatManager(
        sql_connector,
        "退院時サマリ", "WRONG_DPTMT", 
            "A01.1", 
            "NO_USER",
            False)
    system_constents = document_format_manager.get_system_contents()
    if system_constents[0] != "q25":
        raise Exception("system_constents is wrong.")
    if system_constents[1] != "sq25":
        raise Exception("system_constents is wrong.")
    rows = document_format_manager.get_document_format()
    if len(rows) != 2:
        raise Exception("wrong rows count")
    if rows[0][5] != "q26":
        raise Exception("constents is wrong.")
    if rows[0][6] != "sq26":
        raise Exception("constents is wrong.")
    if rows[1][5] != "q27":
        raise Exception("constents is wrong.")
    if rows[1][6] != "sq27":
        raise Exception("constents is wrong.")

        # id:row[0],
        # kind:row[1],
        # category_name:row[2],
        # order_no:row[3], 
        # temperature:row[4],
        # temperature_str:str(row[4]),
        # question:row[5],
        # question_suffix:row[6],
        # response_max_tokens:row[7],
        # target_soap:row[8],
        # use_allergy_records:row[9],
        # use_discharge_medicine_records:row[10]

    print("OK")

finally:
    with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
        delete_test_rows_sql = """DELETE FROM DocumentFormat WHERE CreatedBy = 'TEST'"""
        cursor.execute(delete_test_rows_sql)
        cnxn.commit()

