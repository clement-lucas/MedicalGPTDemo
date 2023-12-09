import re
from datetime import datetime, timedelta
from lib.datetimeconverter import DateTimeConverter

# 基準となる日時を設定
base_datetime = datetime(2022, 1, 1, 12, 0, 0)

# 相対的な日時と時刻を含む文章を変換
text = '１３日前に転んだ。'
converted_text = DateTimeConverter.convert_relative_datetime(text, base_datetime)
print(converted_text)

ret = DateTimeConverter.int_2_str(20220101120000)
print(ret)

ret = DateTimeConverter.get_datetime(20220101120000)
print(ret)

ret = DateTimeConverter.relative_datetime_2_absolute_datetime("１３日前に転んだ。", 20220101120000)
print(ret)

ret = DateTimeConverter.add_days(20220101120000, 13)
print(ret)
