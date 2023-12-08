import re
from datetime import datetime, timedelta
from lib.datetimeconverter import DateTimeConverter

# 基準となる日時を設定
base_datetime = datetime(2022, 1, 1, 12, 0, 0)

# 相対的な日時と時刻を含む文章を変換
text = '現在時刻から３０分後の時間です。'
converted_text = DateTimeConverter.convert_relative_datetime(text, base_datetime)
print(converted_text)
