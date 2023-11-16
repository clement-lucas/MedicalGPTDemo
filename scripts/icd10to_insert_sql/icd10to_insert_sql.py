
# 同階層にある icd10.txt を一行ずつ読み込む。
# 一行ずつ、insert文を作成する。
# 作成したinsert文を、同階層にある icd10.sql に書き込む。

with open("icd10.txt", 'r', encoding='utf-8') as f:
    with open("icd10_insert_values.txt", 'w', encoding='utf-8') as fw:
        for line in f:
        # 行頭が空白であれば、大項目と判定する。
            level = -1
            if line[0] == '　':
                level = 0
                # 行頭の空白を削除する。
                line = line.strip()
            # line を空白で分割する。
            splited_line = line.split('　')
            icd10_code = splited_line[0]
            caption = splited_line[1]
            # caption の行末の改行を削除する。
            caption = caption.strip()
            # caption のシングルクォーテーションをエスケープする。
            caption = caption.replace("'", "''")
            # icd10_code に . が含まれていれば、小項目と判定する。
            if icd10_code.find('.') != -1:
                level = 2
            if level == -1:
                level = 1
            # insert文を作成する。
            sql = "('" + icd10_code + "', " + str(level) + ", '" + caption + "', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),"
            # insert文を書き込む。
            fw.write(sql + '\n')
       