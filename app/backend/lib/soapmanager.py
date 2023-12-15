# 削除予定

from lib.sqlconnector import SQLConnector
from lib.laptimer import LapTimer
from lib.datetimeconverter import DateTimeConverter
class SOAPManager:

    def __init__(self, 
        sql_connector:SQLConnector,
        department_code: str,
        pid: str,
                 ):
        self._sql_connector = sql_connector
        self._department_code = department_code
        self._pid = pid
        with sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
            # サマリ管理テーブルから、入院日と退院日を取得する。
            select_hospitalization_sql = """
                SELECT NOW_DATE, TAIIN_DATE
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
            
            # 入院日と退院日の範囲を計算する。
            # hospitalization_date には、14桁の数値で日付時刻が格納されている。
            # 例）20140224095813

            self._hospitalization_date = rows[0][0]   # 入院日
            # print(self._hospitalization_date)
            self._hospitalization_date = DateTimeConverter.get_start_of_the_day(self._hospitalization_date)
            self._discharge_date = rows[0][1]         # 退院日
            # print(self._discharge_date)
            self._discharge_date = DateTimeConverter.get_start_of_the_day(self._discharge_date)
            self._hospitalization_date_str = DateTimeConverter.int_2_str(self._hospitalization_date, True)
            self._discharge_date_str = DateTimeConverter.int_2_str(self._discharge_date, True)

    @property
    def hospitalization_date_str(self):
        return self._hospitalization_date_str
    
    @property
    def discharge_date_str(self):
        return self._discharge_date_str

    def get_values(
        self,
        target_soap_kinds: str,
        use_range_kind: int,
        days_before_the_date_of_hospitalization_to_use: int,
        days_after_the_date_of_hospitalization_to_use: int,
        days_before_the_date_of_discharge_to_use: int,
        days_after_the_date_of_discharge_to_use: int) -> str:

        # 'SoP' -> 'sop'
        target_soap_kinds = target_soap_kinds.lower()

        # 'sop' -> ['s', 'o', 'p']
        target_soap_kinds = list(target_soap_kinds)

        # IN (?, ?, ?) にするために、カンマ区切りの文字列にする。
        placeholders = ', '.join('?' for _ in target_soap_kinds)

        timer = LapTimer()
        timer.start("SQL SELECT 処理")
        
        with self._sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
            # 期間の計算
            absolute_range_satart_date: int = 0
            absolute_range_end_date: int = 0
            if use_range_kind == 0:
                absolute_range_satart_date = self._hospitalization_date
                absolute_range_end_date = self._discharge_date
            elif use_range_kind == 1:
                absolute_range_satart_date = DateTimeConverter.add_days(self._hospitalization_date, days_before_the_date_of_hospitalization_to_use * -1)
                absolute_range_end_date = DateTimeConverter.add_days(self._hospitalization_date, days_after_the_date_of_hospitalization_to_use)
            elif use_range_kind == 2:
                absolute_range_satart_date = DateTimeConverter.add_days(self._discharge_date, days_before_the_date_of_discharge_to_use * -1)
                absolute_range_end_date = DateTimeConverter.add_days(self._discharge_date, days_after_the_date_of_discharge_to_use)
            else:
                raise Exception("不正な値です。use_range_kind:" + str(use_range_kind))
            
            # 期間を0時0分0秒から23時59分59秒にする。
            absolute_range_satart_date = DateTimeConverter.get_start_of_the_day(absolute_range_satart_date)
            absolute_range_end_date = DateTimeConverter.get_end_of_the_day(absolute_range_end_date)

            range_str = "使用するカルテ期間：" + str(absolute_range_satart_date) + "～" + str(absolute_range_end_date)
            #print(range_str)

            select_data_sql = f"""
                SELECT Id, OriginalDocNo, DocDate, SoapKind, DuplicateSourceDataId, IntermediateData
                FROM IntermediateSOAP
                WHERE (? <= DocDate AND DocDate <= ?)
                    AND Pid = ? AND SoapKind IN ({placeholders}) AND IsDeleted = 0
                ORDER BY Id"""

            # 中間データの取得
            cursor.execute(select_data_sql,
                           absolute_range_satart_date, absolute_range_end_date, 
                           self._pid, *target_soap_kinds)
            rows = cursor.fetchall() 

            if len(rows) < 1:
                timer.stop()
                raise Exception("中間データが取得できませんでした。pid:" + str(self._pid) + ", now_ka:" + self._department_code + range_str)

            id_list = []
            rows_include_duplicate = []
            # 芋づる式に重複データを取得する。
            for row in rows:
                # 日付が変わったら、日付を更新する。
                id = row[0]
                original_doc_no = row[1]
                doc_date = row[2]
                kind = row[3]
                duplicate_source_data_id = row[4]
                intermediateData = row[5]

                SOAPManager._get_duplicate_data_source(
                    cnxn, duplicate_source_data_id, id_list, rows_include_duplicate)

                id_list.append(id)
                rows_include_duplicate.append(row)

            now_date = -1
            return_soap = "\n以下は医師の書いた SOAP です。\n\n"
            original_doc_no_list = []
            for row in rows_include_duplicate:
                # 日付が変わったら、日付を更新する。
                id = row[0]
                original_doc_no = row[1]
                doc_date = row[2]
                kind = row[3]
                duplicate_source_data_id = row[4]
                intermediateData = row[5]

                if intermediateData is None or intermediateData == "":
                    continue

                if now_date != doc_date:
                    now_date = doc_date
                    return_soap = ''.join([return_soap, "\n", DateTimeConverter.int_2_str(doc_date), "\n\n"])
                return_soap = ''.join([return_soap, kind.upper(), "：\n", intermediateData, "\n\n"])
                original_doc_no_list.append(original_doc_no)
        timer.stop()
        return return_soap, id_list, \
                original_doc_no_list, \
                absolute_range_satart_date, \
                absolute_range_end_date

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
        id = source_data[0]
        source_duplicate_source_data_id = source_data[4]
        SOAPManager._get_duplicate_data_source(
            cnxn, source_duplicate_source_data_id, id_list, rows_include_duplicate)

        id_list.append(id)
        rows_include_duplicate.append(source_data)

    @staticmethod
    def _get_data_by_duplicate_source_data_id(cnxn, duplicate_source_data_id:int):
        with cnxn.cursor() as cursor:
            select_data_sql = """
                SELECT Id, OriginalDocNo, DocDate, SoapKind, DuplicateSourceDataId, IntermediateData
                FROM IntermediateSOAP
                WHERE Id = ? AND IsDeleted = 0
                """
            cursor.execute(select_data_sql, duplicate_source_data_id)
            rows = cursor.fetchall() 
            if len(rows) < 1:
                return None
            return rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5]
