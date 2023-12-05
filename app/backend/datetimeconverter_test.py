from datetime import datetime, timedelta
import re

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

# 基準となる日時を設定
base_datetime = datetime(2022, 1, 1, 12, 0, 0)

# 相対的な日時と時刻を含む文章を変換
text = '現在時刻から３０分後の時間です。'
converted_text = convert_relative_datetime(text, base_datetime)
print(converted_text)
