import os
from lib.sqlconnector import SQLConnector
from approaches.approach import Approach

class UpdateDocumentFormatApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, 
                 sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, 
            document_format_index_id:int, 
            document_format_index_name:str, 
            document_name:str, 
            tags:str,
            user_id:str, 
            system_contents:str, system_contents_suffix:str, document_formats: []
            ) -> any:
        print("UpdateDocumentFormatApproach.run")  
        print("document_format_index_id:" + str(document_format_index_id))
        print("document_format_index_name:" + document_format_index_name)
        print("document_name:" + document_name)
        print("user_id:" + user_id)

        gpt_model_name = os.getenv("AZURE_GPT_MODEL_NAME")
        # print(gpt_model_name)
        if gpt_model_name is None:
            gpt_model_name = "gpt-35-turbo"

        # トランザクションを開始する
        with self.sql_connector.get_conn() as cnxn:
            cnxn.autocommit = False
            with cnxn.cursor() as cursor:

                try:
                    if document_format_index_id == -1:
                        # ドキュメントフォーマットの新規登録
                        insert_document_format_sql = """
                            INSERT INTO DocumentFormatIndex
                            ( 
                                IsMaster,
                                [IndexName],
                                Tags,
                                DocumentName,
                                GPTModelName,
                                CreatedBy,
                                UpdatedBy,
                                CreatedDateTime,
                                UpdatedDateTime,
                                IsDeleted
                            )
                            VALUES
                            (0, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE(), 0);"""
                        cursor.execute(insert_document_format_sql,
                                    document_format_index_name,
                                    tags,
                                    document_name,
                                    gpt_model_name,
                                    user_id,
                                    user_id)
                        cursor.execute("SELECT @@IDENTITY AS ID;")
                        document_format_index_id = cursor.fetchone()[0]
                    else:
                        # ドキュメントフォーマットの論理削除
                        update_document_format_sql = """UPDATE DocumentFormatData SET
                                IsDeleted = 1,
                                UpdatedBy = ?,
                                UpdatedDateTime = GETDATE()
                            WHERE IndexId = ?
                            AND IsDeleted = 0"""
                        cursor.execute(update_document_format_sql,
                                    user_id,
                                    document_format_index_id)
                    
                        # ドキュメントフォーマットファイルの更新
                        update_document_format_sql = """UPDATE DocumentFormatIndex SET
                                IndexName = ?,
                                Tags = ?,
                                UpdatedBy = ?,
                                UpdatedDateTime = GETDATE()
                            WHERE IndexId = ?
                            AND IsDeleted = 0"""
                        cursor.execute(update_document_format_sql,
                                    document_format_index_name,
                                    tags,
                                    user_id,
                                    document_format_index_id)
                    
                    insert_document_format_sql = """INSERT INTO DocumentFormatData
                        ( 
                            IsMaster,
                            IndexId,
                            Kind, 
                            OrderNo, 
                            CategoryName, 
                            Temperature,
                            Question, 
                            QuestionSuffix,
                            ResponseMaxTokens, 
                            TargetSoapRecords, 
                            UseAllergyRecords, 
                            UseDischargeMedicineRecords,
                            StartDayToUseSoapRangeAfterHospitalization,
                            UseSoapRangeDaysAfterHospitalization,
                            StartDayToUseSoapRangeBeforeDischarge,
                            UseSoapRangeDaysBeforeDischarge,
                            CreatedBy,
                            UpdatedBy,
                            CreatedDateTime,
                            UpdatedDateTime,
                            IsDeleted
                        )
                        VALUES
                        ( 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?, ?, ?, ?, ?, GETDATE(), GETDATE(), 0)"""

                    rows_to_insert = []
                    for document_format in document_formats:
                        target_soap = ""
                        if document_format['is_s']:
                            target_soap += "s"
                        if document_format['is_o']:
                            target_soap += "o"
                        if document_format['is_a']:
                            target_soap += "a"
                        if document_format['is_p']:
                            target_soap += "p"
                        if document_format['is_b']:
                            target_soap += "b"
                        rows_to_insert.append((
                            document_format_index_id,
                            document_format['kind'],
                            document_format['order_no'],
                            document_format['category_name'],
                            document_format['temperature'],
                            document_format['question'],
                            document_format['question_suffix'],
                            document_format['response_max_tokens'],
                            target_soap,
                            document_format['start_day_to_use_soap_range_after_hospitalization'],
                            document_format['use_soap_range_days_after_hospitalization'],
                            document_format['start_day_to_use_soap_range_before_discharge'],
                            document_format['use_soap_range_days_before_discharge'],
                            user_id,
                            user_id
                        ))

                    # システムコンテンツの登録
                    rows_to_insert.append((
                        document_format_index_id,
                        0,
                        0,
                        '',
                        0,
                        system_contents,
                        system_contents_suffix,
                        0,
                        '',
                        0,
                        0,
                        0,
                        0,
                        user_id,
                        user_id
                    ))
                    cursor.executemany(insert_document_format_sql, rows_to_insert)

                    # トランザクションのコミット
                    cnxn.commit()
                except:
                    # トランザクションのロールバック
                    cnxn.rollback()
                    raise

        return {"document_format_index_id": document_format_index_id}
