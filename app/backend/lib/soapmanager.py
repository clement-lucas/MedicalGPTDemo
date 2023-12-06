# 削除予定

from lib.sqlconnector import SQLConnector
from lib.laptimer import LapTimer
from lib.datetimeconverter import DateTimeConverter
class SOAPManager:
    
    @staticmethod
    def get_values(
        sql_connector:SQLConnector,
        pid: str,
        department_code: str,
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
                AND NOW_KA = ?
                AND SUM_SEQ = (
                SELECT MAX(SUM_SEQ)
                FROM ECSCSM_ECTBSM
                WHERE PID = ?
                AND SUM_SYUBETU = '01'
                AND NOW_KA = ?
                );
                """
            cursor.execute(select_hospitalization_sql, 
                           pid, department_code, 
                           pid, department_code)
            rows = cursor.fetchall() 
            if len(rows) < 1:
                err_msg = "サマリ管理テーブルから入院日と退院日を取得できませんでした。pid:" + str(pid) + ", now_ka:" + department_code
                print(err_msg) 
                raise Exception(err_msg)
            
            hospitalization_date = rows[0][0]   # 入院日
            hospitalization_date = DateTimeConverter.get_start_of_the_day(hospitalization_date)
            discharge_date = rows[0][1]         # 退院日
            discharge_date = DateTimeConverter.get_start_of_the_day(discharge_date)

            start_hospitalization_date = DateTimeConverter.add_days(hospitalization_date, startDayToUseSoapRangeAfterHospitalization, True)
            end_hospitalization_date = DateTimeConverter.add_days(start_hospitalization_date, useSoapRangeDaysAfterHospitalization, True)
            end_discharge_date = DateTimeConverter.add_days(discharge_date, startDayToUseSoapRangeBeforeDischarge * -1, True)
            start_discharge_date = DateTimeConverter.add_days(end_discharge_date, useSoapRangeDaysBeforeDischarge * -1, True)
            end_hospitalization_date = DateTimeConverter.get_end_of_the_day(end_hospitalization_date)
            end_discharge_date = DateTimeConverter.get_end_of_the_day(end_discharge_date)

            # 入院日と退院日の範囲を計算する。
            # hospitalization_date には、14桁の数値で日付時刻が格納されている。
            # 例）20140224095813

            select_datax_sql = f"""
                WITH CTE AS (
                    SELECT Id, OriginalDocNo, DuplicateSourceDataId
                    FROM IntermediateSOAP
                    WHERE ((DocDate >= ? AND DocDate <= ?) OR (DocDate >= ? AND DocDate <= ?))
                        AND Pid = ? AND SoapKind IN ({placeholders}) AND IsDeleted = 0
                    UNION ALL
                    SELECT i.Id, i.OriginalDocNo, i.DuplicateSourceDataId
                    FROM IntermediateSOAP i
                    INNER JOIN CTE c ON c.DuplicateSourceDataId = i.Id
                )
                SELECT DISTINCT i.DocDate, i.SoapKind, i.IntermediateData
                FROM CTE c
                INNER JOIN IntermediateSOAP i ON c.Id = i.Id
                WHERE c.DuplicateSourceDataId IS NULL OR c.DuplicateSourceDataId = i.Id
                ORDER BY c.Id"""

            # 中間データの取得
            cursor.execute(select_datax_sql,
                           start_hospitalization_date, end_hospitalization_date, 
                           start_discharge_date, end_discharge_date, 
                           pid, *target_soap_kinds)
            rows = cursor.fetchall() 

            if len(rows) < 1:
                timer.stop()
                return ""

            now_date = -1
            return_soap = "\n以下は医師の書いた SOAP です。\n\n"
            for row in rows:
                # 日付が変わったら、日付を更新する。
                doc_date = row[0]
                kind = row[1]
                intermediateData = row[2]

                if now_date != doc_date:
                    now_date = doc_date
                    return_soap = ''.join([return_soap, DateTimeConverter.int_2_str(doc_date), "\n\n"])
                return_soap = ''.join([return_soap, kind.upper(), "：\n", intermediateData, "\n\n"])
                # print(return_soap)
        timer.stop()
        return return_soap

    
