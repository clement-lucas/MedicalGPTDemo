from datetime import datetime, timedelta

class DateTimeConverter:
    def __init__():
        pass

    # 相対日時表現を含む文字列を絶対日時表現に変換する
    # base_datetime は、絶対日時表現の基準となる日時。14桁の数値を想定している。
    @staticmethod
    def relative_datetime_2_absolute_datetime(org_text:str, base_datetime_int:int) -> str:
        base_datetime = DateTimeConverter.get_datetime(base_datetime_int)
        new_text = DateTimeConverter.convert_relative_datetime(org_text, base_datetime)
        return new_text

    # yyyyMMddHHMISS -> yyyy/MM/dd HH:MI:SS
    @staticmethod
    def get_datetime(org: int) -> datetime.datetime:
        strdate = str(org)
        if len(strdate) != 14:
            raise Exception("日時表現が14桁ではありません。")
        
        # 14桁の数値 yyyyMMddHHMISS からyyyyを取得する
        yyyy = org // 10000000000
        # 14桁の数値 yyyyMMddHHMISS からMMを取得する
        MM = (org - yyyy * 10000000000) // 100000000
        # 14桁の数値 yyyyMMddHHMISS からddを取得する
        dd = (org - yyyy * 10000000000 - MM * 100000000) // 1000000
        # 14桁の数値 yyyyMMddHHMISS からHHを取得する
        HH = (org - yyyy * 10000000000 - MM * 100000000 - dd * 1000000) // 10000
        # 14桁の数値 yyyyMMddHHMISS からMIを取得する
        MI = (org - yyyy * 10000000000 - MM * 100000000 - dd * 1000000 - HH * 10000) // 100
        # 14桁の数値 yyyyMMddHHMISS からSSを取得する
        SS = org - yyyy * 10000000000 - MM * 100000000 - dd * 1000000 - HH * 10000 - MI * 100
        return datetime.datetime(yyyy, MM, dd, HH, MI, SS)
    
    @staticmethod
    def convert_relative_datetime(text, base_datetime):
        # 日時の表現パターンを正規表現で定義
        patterns = {
            r'(\d+)秒前': lambda match: base_datetime - timedelta(seconds=int(match)),
            r'(\d+)分前': lambda match: base_datetime - timedelta(minutes=int(match)),
            r'(\d+)時間前': lambda match: base_datetime - timedelta(hours=int(match)),
            r'(\d+)日前': lambda match: base_datetime - timedelta(days=int(match)),
            r'(\d+)週間前': lambda match: base_datetime - timedelta(weeks=int(match)),
            r'(\d+)か月前': lambda match: base_datetime - timedelta(days=30*int(match)),
            r'(\d+)年前': lambda match: base_datetime - timedelta(days=365*int(match)),
            r'(\d+)秒後': lambda match: base_datetime + timedelta(seconds=int(match)),
            r'(\d+)分後': lambda match: base_datetime + timedelta(minutes=int(match)),
            r'(\d+)時間後': lambda match: base_datetime + timedelta(hours=int(match)),
            r'(\d+)日後': lambda match: base_datetime + timedelta(days=int(match)),
            r'(\d+)週間後': lambda match: base_datetime + timedelta(weeks=int(match)),
            r'(\d+)か月後': lambda match: base_datetime + timedelta(days=30*int(match)),
            r'(\d+)年後': lambda match: base_datetime + timedelta(days=365*int(match))
        }

        # テキスト内の相対的な日時表現を検索して置換
        for pattern, func in patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                converted_match = func(int(match))
                text = text.replace(match, converted_match.strftime('%Y/%m/%d %H:%M:%S'))

        return text
