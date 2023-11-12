class SOAPCacheManager:
    def __init__(self, user_id, patinet_code):
        self._rows_to_insert = []
        self._user_id = user_id
        self._patient_code = patinet_code
        self._summarized_s = ""
        self._summarized_o = ""
        self._summarized_a = ""
        self._summarized_p = ""
        self._summarized_b = ""
        
    def InitRowsToCache(self):
        self._rows_to_insert = []

    def GetLastDocDate(self, cursor):
        cached_doc_date_sql = """SELECT TOP (1) LastDocDate
            FROM SummarizedSOAPCache
            WHERE IsDeleted = 0 AND Pid = ?
            ORDER BY LastDocDate DESC"""
        cursor.execute(cached_doc_date_sql, self._patient_code)
        rows = cursor.fetchall() 
        for row in rows:
            return int(row[0]) if row[0] != None else 0
        return 0
    
    def GetSummarizedSOAP(self, cursor):
        cached_doc_date_sql = """SELECT 
            SoapKind, SummarizedSOAP
            FROM SummarizedSOAPCache
            WHERE IsDeleted = 0 AND Pid = ? """
        cursor.execute(cached_doc_date_sql, self._patient_code)
        rows = cursor.fetchall() 
        for row in rows:
            # print(row)
            soap_kind = row[0]
            if soap_kind == 's':
                self._summarized_s = row[1]
            elif soap_kind == 'o':
                self._summarized_o = row[1]
            elif soap_kind == 'a':
                self._summarized_a = row[1]
            elif soap_kind == 'p':
                self._summarized_p = row[1]
            elif soap_kind == 'b':
                self._summarized_b = row[1]

    @property
    def SummarizedS(self):
        return self._summarized_s
    
    @property
    def SummarizedO(self):
        return self._summarized_o
    
    @property
    def SummarizedA(self):
        return self._summarized_a
    
    @property
    def SummarizedP(self):
        return self._summarized_p
    
    @property
    def SummarizedB(self):
        return self._summarized_b
    
    def AddRowToCache(self, soap_kind, 
                      last_doc_date,
                      summarized_soap, 
                      completion_tokens_for_summarize, 
                      prompt_tokens_for_summarize, 
                      total_tokens_for_summarize, 
                      summarize_log):
        self._rows_to_insert.append((
            self._patient_code, 
            last_doc_date, 
            soap_kind, 
            summarized_soap, 
            completion_tokens_for_summarize, 
            prompt_tokens_for_summarize, 
            total_tokens_for_summarize,
            summarize_log, 
            self._user_id, 
            self._user_id))
        
    def SaveCache(self, cnxn, cursor):
        if len(self._rows_to_insert) == 0:
            return
        try:
            # 既存キャッシュの論理削除
            delete_sql = """
                UPDATE SummarizedSOAPCache
                SET IsDeleted = 1
                WHERE Pid = ?
                AND IsDeleted = 0
                """
            cursor.execute(delete_sql, self._patient_code)

            insert_sql = """
            INSERT INTO SummarizedSOAPCache
                    (Pid
                    ,LastDocDate
                    ,SoapKind
                    ,SummarizedSOAP
                    ,CompletionTokensForSummarize
                    ,PromptTokensForSummarize
                    ,TotalTokensForSummarize
                    ,SummarizeLog
                    ,CreatedBy
                    ,UpdatedBy
                    ,CreatedDateTime
                    ,UpdatedDateTime
                    ,IsDeleted)
                VALUES
                    (?
                    ,?
                    ,?
                    ,?
                    ,?
                    ,?
                    ,?
                    ,?
                    ,?
                    ,?
                    ,GETDATE()
                    ,GETDATE()
                    ,0)
                    """
            cursor.executemany(insert_sql, self._rows_to_insert)

            # トランザクションのコミット
            cnxn.commit()
        except:
            # トランザクションのロールバック
            cnxn.rollback()
            raise

