from lib.sqlconnector import SQLConnector
from parser.doctorsnoteparser import DoctorsNoteParser as DNP

class SOAPManager:
    _soap_by_date_list = []

    def SOAP(self, target: str):
        # target には、S, O, A, P のいずれかを指定する。
        # 指定された target に対応する SOAP を返却する。
        # SOAP が存在しない場合は、空文字を返却する。
        target = target.upper()
        records = ""
        for soap_by_date in self._soap_by_date_list:
            record_of_the_day = ""
            if target.find('S') >= 0:
                if soap_by_date[1].S != "":
                    record_of_the_day += "S：" + soap_by_date[1].S + "\n\n"
            if target.find('O') >= 0:
                if soap_by_date[1].O != "":
                    record_of_the_day += "O：" + soap_by_date[1].O + "\n\n"
            if target.find('A') >= 0:
                if soap_by_date[1].A != "":
                    record_of_the_day += "A：" + soap_by_date[1].A + "\n\n"
            if target.find('P') >= 0:
                if soap_by_date[1].P != "":
                    record_of_the_day += "P：" + soap_by_date[1].P + "\n\n"
            records += "記入日：" + soap_by_date[0] + "\n\n"
            records += record_of_the_day
            records += "\n"
        soap_prefix = "\n以下は医師の書いた SOAP です。\n\n"
        return soap_prefix + records

    def __init__(self, patient_code: str):
        # SQL Server に接続する
        cnxn = SQLConnector.get_conn()
        cursor = cnxn.cursor()

        # TODO 日付等の各種取得条件は適宜実装のこと
        select_datax_sql = """SELECT EXTBDH1.DOCDATE, EXTBDC1.DOC_DATAX FROM EXTBDC1 
            INNER JOIN EXTBDH1 
            ON EXTBDC1.DOC_NO = EXTBDH1.DOC_NO
            AND EXTBDH1.DOC_K = ? 
            AND EXTBDH1.ACTIVE_FLG = 1 
            AND EXTBDC1.ACTIVE_FLG = 1 
            AND EXTBDH1.PID = ?
            ORDER BY EXTBDH1.DOCDATE DESC"""

        # 医師記録の取得
        cursor.execute(select_datax_sql,'MD01', patient_code)
        rows = cursor.fetchall() 
        
        for row in rows:
            datetime = self.get_datetime(row[0])
            # XML のまま GPT に投げても解釈してくれないこともないが、
            # XML のままだとトークン数をとても消費してしまうので、
            # XML を解釈して、平文に変換する。
            soap = DNP(row[1])
            self._soap_by_date_list.append((datetime, soap))

    # yyyyMMddHHMISS -> yyyy/MM/dd HH:MI:SS に変換する関数
    # 例）20140224095813 -> 2014/02/24 09:58:13
    def get_datetime(self, org: str):
        strdate = str(org)
        if len(strdate) != 14:
            return strdate
        year = strdate[0:4]
        month = strdate[4:6]
        day = strdate[6:8]
        hour = strdate[8:10]
        minute = strdate[10:12]
        second = strdate[12:14]
        return year + "/" + month + "/" + day + " " + hour + ":" + minute + ":" + second
    
