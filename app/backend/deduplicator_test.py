
import re
from lib.deduplicator import Deduplicator

text = "あい.う!え?お。かきくけこ、さしすせそ！たちつてと？なにぬねの\r\nはひふへほ\nまみむめも<BR></BR>やゆよ<BR/>らりるれろ<br></br>わをん"
result = Deduplicator.split_string(text)
print(result)


text1 = "あい<BR/>うえお。かきくけこ。さしすせそ。たちつてと。"
text2 = "あいうえお。かきくけこ。さしすせそ。"

deduplicated = Deduplicator.deduplicate(text1, text2) 
print(deduplicated)

text2 = "あい<BR/>うえお。かきくけこ。さしすせそ。たちつてと。"
deduplicated = Deduplicator.deduplicate(text1, text2) 
print(deduplicated)

text2 = "いろはにほへと。ちりぬるを"
deduplicated = Deduplicator.deduplicate(text1, text2) 
print(deduplicated)

# import re

# #text = "あいうえお、かきくけこ。さしす\nせ。そ。"
# text = "あい.う!え?お。かきくけこ、さしすせそ！たちつてと？なにぬねの\r\nはひふへほ\nまみむめも<BR></BR>やゆよ<BR/>らりるれろ<br></br>わをん"
# #pattern = r"([、。\n])"
# pattern = r'(\.|\。|\!|\?|\！|\？|\r\n|\n|<BR><\/BR>|<BR\/>|<br><\/br>|<br\/>)'

# result = re.split(pattern, text)
# result = ["".join(pair) for pair in zip(result[0::2], result[1::2])]
# print(result)




