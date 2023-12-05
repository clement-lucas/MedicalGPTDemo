import re

# 文章中の重複部分を削除するクラス
class Deduplicator:
    def __init__():
        pass

    #SPLITTES に含まれる文字列で分割する
    # このコードでは、re.splitを使用して文字列を分割しますが、([、。])というパターンを指定しています。このパターンは、「、」または「。」とマッチします。
    # re.splitの結果を処理するため、結果のリストをペアごとに結合します。zip関数を使用して、奇数番目と偶数番目の要素をペアにしています。そして、"".join(pair)を使用してそれぞれのペアを結合し、最終的な結果を得ることができます。
    @staticmethod
    def split_string(text):
        pattern = r'(\.|\。|\!|\?|\！|\？|\r\n|\n|<BR><\/BR>|<BR\/>|<br><\/br>|<br\/>)'
        result = re.split(pattern, text)
        result = ["".join(pair) for pair in zip(result[0::2], result[1::2])]
        return result

    @staticmethod
    def deduplicate(org_text:str, compare_target:str) -> [bool,str]:
        ret_text = ""
        found = False
        org_text_splited = Deduplicator.split_string(org_text)
        compare_target_splited = Deduplicator.split_string(compare_target)
        for org_text_splited_item in org_text_splited:
            if org_text_splited_item in compare_target_splited:
                found = True
                continue
            ret_text += org_text_splited_item
        return found, ret_text
    
    