import os
from lib.sqlconnector import SQLConnector
DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT = 0
DEFAULT_DEPARTMENT_CODE = "0000"
DEFAULT_ICD10_CODE = "0000"

# DocumentFormat テーブルの内容を取得するクラス
# 取得優先順位は以下の通り
# 1. DocumentFormat テーブルに該当レコードが存在する場合
#    条件：ユーザーID、科コード、ICD10コード、文書名、種別、GPTモデル名
# 2. DocumentFormat テーブルに該当レコードが存在する場合
#    条件：マスターレコード、科コード、ICD10コード、文書名、種別、GPTモデル名
# 3. DocumentFormat テーブルに該当レコードが存在する場合
#    条件：マスターレコード、ICD10コード、文書名、種別、GPTモデル名
# 更にそれぞれの条件の中で、当該 ICD10 コードに該当するレコードが存在しない場合は、
# 一階層上の ICD10 コードに該当するレコードを取得する。
# 順に遡り、最上位の ICD10 コードに該当するレコードが存在しない場合は、
# 条件に該当するレコードが無いと判断する。

class DocumentFormatManager:
    # 自分が属する親階層のコードを取得する
    def _get_parent_code(self, icd10_code:str, cnxn) -> str:
        with cnxn.cursor() as cursor:
            get_parent_code_sql = """
                SELECT ParentIcd10Code FROM Icd10Master WHERE Icd10Code = ?
                    AND IsDeleted = 0"""
            cursor.execute(get_parent_code_sql, icd10_code)
            rows = cursor.fetchall()
            parent_code = ""
            for row in rows:
                parent_code = row[0]
                break
            return parent_code


    def __init__(self, sql_connector:SQLConnector, document_name: str, department_code:str, 
            icd10_code:str, 
            user_id:str,
            force_master:bool = False
                ) -> None:
        self._sql_connector = sql_connector
        self._icd10_code = icd10_code
        self._department_code = department_code
        self._document_name = document_name
        self._force_master = force_master
        self._user_id = user_id

        self._gpt_model_name = os.getenv("AZURE_GPT_MODEL_NAME")
        if self._gpt_model_name is None:
            self._gpt_model_name = "gpt-35-turbo"

        # 親の一覧を作成する
        self._parent_list = []
        with self._sql_connector.get_conn() as cnxn:
            target_code = self._icd10_code
            while True:
                parent_code = self._get_parent_code(target_code, cnxn)
                if parent_code == "":
                    break
                else:
                    self._parent_list.append(parent_code)
                    target_code = parent_code
    
    @property
    def parent_list(self):
        return self._parent_list

    def _get_system_contents_by_department_and_user(self, cnxn, department_code:str, user_id:str) -> str:
        with cnxn.cursor() as cursor:
            # システムコンテンツの取得
            select_system_contents_sql = """SELECT 
                    ISNULL(Question, '') AS Question,
                    ISNULL(QuestionSuffix, '') AS QuestionSuffix
                FROM DocumentFormat 
                WHERE IsMaster = 0
                AND UserId = ?
                AND DepartmentCode = ?
                AND Icd10Code = ?
                AND DocumentName = ?
                AND Kind = ?
                AND GPTModelName = ?
                AND IsDeleted = 0
                ORDER BY OrderNo"""
            cursor.execute(select_system_contents_sql,
                        user_id,
                        department_code, self._icd10_code,
                        self._document_name,
                        DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                        self._gpt_model_name)            
            rows = cursor.fetchall() 

            if len(rows) == 0:
                # HIT しなかった場合は、上位階層の ICD10 該当レコードを取得する
                for parent_code in self._parent_list:
                    # 上位階層の ICD10 該当レコードを取得する
                    cursor.execute(select_system_contents_sql,
                                user_id,
                                department_code, parent_code,
                                self._document_name,
                                DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                                self._gpt_model_name)  
                    rows = cursor.fetchall() 
                    if len(rows) > 0:
                        break
            if len(rows) == 0:
                # 最上位階層まで遡ったが、HIT しなかった場合は、ICD10「指定なし」
                cursor.execute(select_system_contents_sql,
                            user_id,
                            department_code, DEFAULT_ICD10_CODE,
                            self._document_name,
                            DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                            self._gpt_model_name)            
                rows = cursor.fetchall() 
            return rows

    def _get_system_contents_master_and_department(self, cnxn, department_code) -> str:
        with cnxn.cursor() as cursor:
            select_system_content_master_sql = """SELECT 
                    ISNULL(Question, '') AS Question,
                    ISNULL(QuestionSuffix, '') AS QuestionSuffix
                FROM DocumentFormat 
                WHERE IsMaster = 1
                AND DepartmentCode = ?
                AND Icd10Code = ?
                AND DocumentName = ?
                AND Kind = ?
                AND GPTModelName = ?
                AND IsDeleted = 0"""

            cursor.execute(select_system_content_master_sql,
                        department_code, self._icd10_code,
                        self._document_name,
                        DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                        self._gpt_model_name)
            rows = cursor.fetchall() 

            if len(rows) == 0:
                # HIT しなかった場合は、上位階層の ICD10 該当レコードを取得する
                for parent_code in self._parent_list:
                    # 上位階層の ICD10 該当レコードを取得する
                    cursor.execute(select_system_content_master_sql,
                                department_code, parent_code,
                                self._document_name,
                                DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                                self._gpt_model_name)
                    rows = cursor.fetchall() 
                    if len(rows) > 0:
                        break
            if len(rows) == 0:
                # 最上位階層まで遡ったが、HIT しなかった場合は、ICD10「指定なし」
                cursor.execute(select_system_content_master_sql,
                            department_code, DEFAULT_ICD10_CODE,
                            self._document_name,
                            DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                            self._gpt_model_name)
                rows = cursor.fetchall() 
            return rows

    def get_system_contents(self
            ) -> any:
        
        # SQL Server に接続する
        with self._sql_connector.get_conn() as cnxn:

            rows = []
            if self._force_master == False:
                rows = self._get_system_contents_by_department_and_user(cnxn, self._department_code, self._user_id)

                if len(rows) == 0:
                    print("DocumentFormat.SystemContents が存在しないため、科を指定して、ユーザー指定なしのレコードを取得します。user_id:" + self._user_id + ", department_code:" + self._department_code + ", icd10_code:" + self._icd10_code + ", document_name:" + self._document_name + ", gpt_model_name:" + self._gpt_model_name)
                    rows = self._get_system_contents_by_department_and_user(cnxn, self._department_code, '')

                if len(rows) == 0:
                    print("DocumentFormat.SystemContents が存在しないため、科を指定せず、ユーザーを指定してレコードを取得します。user_id:" + self._user_id + ", department_code:" + self._department_code + ", icd10_code:" + self._icd10_code + ", document_name:" + self._document_name + ", gpt_model_name:" + self._gpt_model_name)
                    rows = self._get_system_contents_by_department_and_user(cnxn, DEFAULT_DEPARTMENT_CODE, self._user_id)

                if len(rows) == 0:
                    print("DocumentFormat.SystemContents が存在しないため、科とユーザーを指定せずレコードを取得します。user_id:" + self._user_id + ", department_code:" + self._department_code + ", icd10_code:" + self._icd10_code + ", document_name:" + self._document_name + ", gpt_model_name:" + self._gpt_model_name)
                    rows = self._get_system_contents_by_department_and_user(cnxn, DEFAULT_DEPARTMENT_CODE, '')

            if len(rows) == 0:
                if self._force_master == False:
                    print("DocumentFormat.SystemContents が存在しないため、科を指定してマスターを取得します。department_code:" + self._department_code + ", icd10_code:" + self._icd10_code + ", document_name:" + self._document_name + ", gpt_model_name:" + self._gpt_model_name)
                rows = self._get_system_contents_master_and_department(cnxn, self._department_code)

            if len(rows) == 0:
                print("DocumentFormat.SystemContents が存在しないため、科を指定せずマスターを取得します。department_code:" + self._department_code + ", icd10_code:" + self._icd10_code + ", document_name:" + self._document_name + ", gpt_model_name:" + self._gpt_model_name)
                rows = self._get_system_contents_master_and_department(cnxn, DEFAULT_DEPARTMENT_CODE)

            system_contetns = ""
            system_contetns_suffix = ""
            for row in rows:
                system_contetns = row[0]
                system_contetns_suffix = row[1]
                break
            return system_contetns, system_contetns_suffix

    def _get_contents_by_department_and_user(self, cnxn, department_code, user_id:str) -> str:
        with cnxn.cursor() as cursor:
            select_document_format_sql = """SELECT 
                    Id, 
                    Kind, 
                    CategoryName, 
                    OrderNo,
                    Temperature,
                    ISNULL(Question, '') AS Question,
                    ISNULL(QuestionSuffix, '') AS QuestionSuffix,
                    ResponseMaxTokens,
                    TargetSoapRecords, 
                    UseAllergyRecords, 
                    UseDischargeMedicineRecords 
                FROM DocumentFormat 
                WHERE IsMaster = 0
                AND UserId = ?
                AND DepartmentCode = ?
                AND Icd10Code = ?
                AND DocumentName = ?
                AND Kind <> ?
                AND GPTModelName = ?
                AND IsDeleted = 0
                ORDER BY OrderNo"""
            cursor.execute(select_document_format_sql,
                        user_id,
                        department_code, self._icd10_code,
                        self._document_name,
                        DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                        self._gpt_model_name)            
            rows = cursor.fetchall() 

            if len(rows) == 0:
                # HIT しなかった場合は、上位階層の ICD10 該当レコードを取得する
                for parent_code in self._parent_list:
                    # 上位階層の ICD10 該当レコードを取得する
                    cursor.execute(select_document_format_sql,
                                user_id,
                                department_code, parent_code,
                                self._document_name,
                                DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                                self._gpt_model_name)            
                    rows = cursor.fetchall() 
                    if len(rows) > 0:
                        break
            if len(rows) == 0:
                # 最上位階層まで遡ったが、HIT しなかった場合は、ICD10「指定なし」
                cursor.execute(select_document_format_sql,
                            user_id,
                            department_code, DEFAULT_ICD10_CODE,
                            self._document_name,
                            DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                            self._gpt_model_name)            
                rows = cursor.fetchall() 
            return rows

    def _get_contents_master_and_department(self, cnxn, department_code) -> str:
        with cnxn.cursor() as cursor:
            # ドキュメントフォーマットの取得
            select_document_format_master_sql = """SELECT 
                    Id, 
                    Kind, 
                    CategoryName, 
                    OrderNo,
                    Temperature,
                    ISNULL(Question, '') AS Question,
                    ISNULL(QuestionSuffix, '') AS QuestionSuffix,
                    ResponseMaxTokens,
                    TargetSoapRecords, 
                    UseAllergyRecords, 
                    UseDischargeMedicineRecords 
                FROM DocumentFormat 
                WHERE IsMaster = 1
                AND DepartmentCode = ?
                AND Icd10Code = ?
                AND DocumentName = ?
                AND Kind <> ?
                AND GPTModelName = ?
                AND IsDeleted = 0
                ORDER BY OrderNo"""

            cursor.execute(select_document_format_master_sql,
                        department_code, self._icd10_code,
                        self._document_name,
                        DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                        self._gpt_model_name)
            rows = cursor.fetchall() 

            if len(rows) == 0:
                # HIT しなかった場合は、上位階層の ICD10 該当レコードを取得する
                for parent_code in self._parent_list:
                    # 上位階層の ICD10 該当レコードを取得する
                    cursor.execute(select_document_format_master_sql,
                                department_code, parent_code,
                                self._document_name,
                                DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                                self._gpt_model_name)
                    rows = cursor.fetchall() 
                    if len(rows) > 0:
                        break
            if len(rows) == 0:
                # 最上位階層まで遡ったが、HIT しなかった場合は、ICD10「指定なし」
                cursor.execute(select_document_format_master_sql,
                            department_code, DEFAULT_ICD10_CODE,
                            self._document_name,
                            DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT,
                            self._gpt_model_name)
                rows = cursor.fetchall() 
            return rows

    # id:row[0],
    # kind:row[1],
    # category_name:row[2],
    # order_no:row[3], 
    # temperature:row[4],
    # temperature_str:str(row[4]),
    # question:row[5],
    # question_suffix:row[6],
    # response_max_tokens:row[7],
    # target_soap:row[8],
    # use_allergy_records:row[9],
    # use_discharge_medicine_records:row[10]
    def get_document_format(self
            ) -> any:
        
        # SQL Server に接続する
        with self._sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:
            rows = []
            if self._force_master == False:
                rows = self._get_contents_by_department_and_user(cnxn, self._department_code, self._user_id)

                if len(rows) == 0:
                    print("DocumentFormat が存在しないため、科を指定して、ユーザー指定なしのレコードを取得します。user_id:" + self._user_id + ", department_code:" + self._department_code + ", icd10_code:" + self._icd10_code + ", document_name:" + self._document_name + ", gpt_model_name:" + self._gpt_model_name)
                    rows = self._get_contents_by_department_and_user(cnxn, self._department_code, '')

                if len(rows) == 0:
                    print("DocumentFormat が存在しないため、科を指定せず、ユーザーを指定してレコードを取得します。user_id:" + self._user_id + ", department_code:" + self._department_code + ", icd10_code:" + self._icd10_code + ", document_name:" + self._document_name + ", gpt_model_name:" + self._gpt_model_name)
                    rows = self._get_contents_by_department_and_user(cnxn, DEFAULT_DEPARTMENT_CODE, self._user_id)

                if len(rows) == 0:
                    print("DocumentFormat が存在しないため、科とユーザーを指定せずレコードを取得します。user_id:" + self._user_id + ", department_code:" + self._department_code + ", icd10_code:" + self._icd10_code + ", document_name:" + self._document_name + ", gpt_model_name:" + self._gpt_model_name)
                    rows = self._get_contents_by_department_and_user(cnxn, DEFAULT_DEPARTMENT_CODE, '')

            if len(rows) == 0:
                if self._force_master == False:
                    print("DocumentFormat が存在しないため、科を指定してマスターを取得します。department_code:" + self._department_code + ", icd10_code:" + self._icd10_code + ", document_name:" + self._document_name + ", gpt_model_name:" + self._gpt_model_name)
                rows = self._get_contents_master_and_department(cnxn, self._department_code)

            if len(rows) == 0:
                print("DocumentFormat が存在しないため、科を指定せずマスターを取得します。department_code:" + self._department_code + ", icd10_code:" + self._icd10_code + ", document_name:" + self._document_name + ", gpt_model_name:" + self._gpt_model_name)
                rows = self._get_contents_master_and_department(cnxn, DEFAULT_DEPARTMENT_CODE)

        return rows
                


        


