# 削除予定

from lib.sqlconnector import SQLConnector
from lib.laptimer import LapTimer
from lib.datetimeconverter import DateTimeConverter
class SOAPManager:
    
    @staticmethod
    def get_values(
        sql_connector:SQLConnector,
        department_code: str,
        pid: str,
        target_soap_kinds: str,
        startDayToUseSoapRangeAfterHospitalization: int,
        useSoapRangeDaysAfterHospitalization: int,
        startDayToUseSoapRangeBeforeDischarge: int,
        useSoapRangeDaysBeforeDischarge: int) -> str:

        # 'SoP' -> 'sop'
        target_soap_kinds = target_soap_kinds.lower()

        # 'sop' -> ['s', 'o', 'p']
        target_soap_kinds = list(target_soap_kinds)

        # IN (?, ?, ?) にするために、カンマ区切りの文字列にする。
        placeholders = ', '.join('?' for _ in target_soap_kinds)

        timer = LapTimer()
        timer.start("SQL SELECT 処理")
        
        with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
            # サマリ管理テーブルから、入院日と退院日を取得する。
            select_hospitalization_sql = """
                SELECT 
                    CASE 
                        WHEN NOW_DATE IS NOT NULL THEN NOW_DATE
                        ELSE ORIGINAL_DATE 
                    END as NYUI_DATE,
                    TAIIN_DATE
                FROM ECSCSM_ECTBSM
                WHERE PID = ?
                AND SUM_SYUBETU = '01'
                AND (NOW_KA = ? OR ORIGINAL_KA = ?)
                AND SUM_SEQ = (
                SELECT MAX(SUM_SEQ)
                FROM ECSCSM_ECTBSM
                WHERE PID = ?
                AND SUM_SYUBETU = '01'
                AND (NOW_KA = ? OR ORIGINAL_KA = ?)
                );
                """
            cursor.execute(select_hospitalization_sql, 
                           pid, department_code, department_code, 
                           pid, department_code, department_code)
            rows = cursor.fetchall() 
            if len(rows) < 1:
                err_msg = "サマリ管理テーブルから入院日と退院日を取得できませんでした。pid:" + str(pid) + ", now_ka:" + department_code
                print(err_msg) 
                raise Exception(err_msg)
            
            # 入院日と退院日の範囲を計算する。
            # hospitalization_date には、14桁の数値で日付時刻が格納されている。
            # 例）20140224095813

            hospitalization_date = rows[0][0]   # 入院日
            hospitalization_date = DateTimeConverter.get_start_of_the_day(hospitalization_date)
            discharge_date = rows[0][1]         # 退院日
            discharge_date = DateTimeConverter.get_start_of_the_day(discharge_date)

            start_hospitalization_date = DateTimeConverter.add_days(hospitalization_date, startDayToUseSoapRangeAfterHospitalization)
            end_hospitalization_date = DateTimeConverter.add_days(start_hospitalization_date, useSoapRangeDaysAfterHospitalization)
            end_discharge_date = DateTimeConverter.add_days(discharge_date, startDayToUseSoapRangeBeforeDischarge * -1)
            start_discharge_date = DateTimeConverter.add_days(end_discharge_date, useSoapRangeDaysBeforeDischarge * -1)
            end_hospitalization_date = DateTimeConverter.get_end_of_the_day(end_hospitalization_date)
            end_discharge_date = DateTimeConverter.get_end_of_the_day(end_discharge_date)

            range_str = "入院日カルテ期間：" + str(start_hospitalization_date) + "～" + str(end_hospitalization_date) + "\n退院日カルテ期間：" + str(start_discharge_date) + "～" + str(end_discharge_date)

            select_data_sql = f"""
                SELECT Id, DocDate, SoapKind, DuplicateSourceDataId, IntermediateData
                FROM IntermediateSOAP
                WHERE ((DocDate >= ? AND DocDate <= ?) OR (DocDate >= ? AND DocDate <= ?))
                    AND Pid = ? AND SoapKind IN ({placeholders}) AND IsDeleted = 0
                ORDER BY Id"""

            # 中間データの取得
            cursor.execute(select_data_sql,
                           start_hospitalization_date, end_hospitalization_date, 
                           start_discharge_date, end_discharge_date, 
                           pid, *target_soap_kinds)
            rows = cursor.fetchall() 

            if len(rows) < 1:
                timer.stop()
                raise Exception("中間データが取得できませんでした。pid:" + str(pid) + ", now_ka:" + department_code + range_str)

            id_list = []
            rows_include_duplicate = []
            # 芋づる式に重複データを取得する。
            for row in rows:
                # 日付が変わったら、日付を更新する。
                id = row[0]
                doc_date = row[1]
                kind = row[2]
                duplicate_source_data_id = row[3]
                intermediateData = row[4]

                SOAPManager._get_duplicate_data_source(
                    cnxn, duplicate_source_data_id, id_list, rows_include_duplicate)

                id_list.append(id)
                rows_include_duplicate.append(row)

            now_date = -1
            return_soap = "\n以下は医師の書いた SOAP です。\n\n"
            for row in rows_include_duplicate:
                # 日付が変わったら、日付を更新する。
                id = row[0]
                doc_date = row[1]
                kind = row[2]
                duplicate_source_data_id = row[3]
                intermediateData = row[4]

                if now_date != doc_date:
                    now_date = doc_date
                    return_soap = ''.join([return_soap, "\n", DateTimeConverter.int_2_str(doc_date), "\n\n"])
                return_soap = ''.join([return_soap, kind.upper(), "：\n", intermediateData, "\n\n"])
        timer.stop()
        return return_soap, id_list

    @staticmethod
    def _get_duplicate_data_source(cnxn, duplicate_source_data_id:int, id_list:[], rows_include_duplicate:[]):
        if duplicate_source_data_id is None or \
            duplicate_source_data_id < 0 or \
            duplicate_source_data_id in id_list:
            return

        # 芋づる式に重複データを取得する。
        source_data = SOAPManager._get_data_by_duplicate_source_data_id(
            cnxn, duplicate_source_data_id)
        if source_data is None:
            raise Exception("重複データが取得できませんでした。Id:" + str(duplicate_source_data_id))
        
        # 再帰的に重複データを取得する。
        source_duplicate_source_data_id = source_data[3]
        SOAPManager._get_duplicate_data_source(
            cnxn, source_duplicate_source_data_id, id_list, rows_include_duplicate)

        rows_include_duplicate.append(source_data)

    @staticmethod
    def _get_data_by_duplicate_source_data_id(cnxn, duplicate_source_data_id:int):
        with cnxn.cursor() as cursor:
            select_data_sql = """
                SELECT Id, DocDate, SoapKind, DuplicateSourceDataId, IntermediateData
                FROM IntermediateSOAP
                WHERE Id = ? AND IsDeleted = 0
                """
            cursor.execute(select_data_sql, duplicate_source_data_id)
            rows = cursor.fetchall() 
            if len(rows) < 1:
                return None
            return rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4]
