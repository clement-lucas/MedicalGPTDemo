from approaches.approach import Approach
from lib.sqlconnector import SQLConnector
from lib.documentformatmanager import DocumentFormatManager
DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT = 0

class GetDocumentFormatApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, document_format_index_id:int
            ) -> any:
        print("GetDocumentFormatApproach.run")  
        print("document_format_index_id:" + str(document_format_index_id))
        
        manager = DocumentFormatManager(
            self.sql_connector,
            document_format_index_id)
        ret_system_contetns = manager.get_system_contents()
        system_contetns = ret_system_contetns[0]
        system_contetns_suffix = ret_system_contetns[1]
        rows = manager.get_document_format()

        ret = []
        for row in rows:
            isS = False
            isO = False
            isA = False
            isP = False
            isB = False

            target = row[8].upper()
            if target.find('S') >= 0:
                isS = True
            if target.find('O') >= 0:
                isO = True
            if target.find('A') >= 0:
                isA = True
            if target.find('P') >= 0:
                isP = True
            if target.find('B') >= 0:
                isB = True

            ret.append({
                "id":row[0],
                "kind":row[1],
                "category_name":row[2],
                "order_no":row[3], 
                "temperature":row[4],
                "temperature_str":str(row[4]),
                "question":row[5],
                "question_suffix":row[6],
                "response_max_tokens":row[7],
                "is_s":isS,
                "is_o":isO,
                "is_a":isA,
                "is_p":isP,
                "is_b":isB,
                "use_allergy_records":row[9],
                "use_discharge_medicine_records":row[10],
                "use_range_kind":row[11],
                "use_range_kind_str":str(row[11]),
                "days_before_the_date_of_hospitalization_to_use":row[12],
                "days_after_the_date_of_hospitalization_to_use":row[13],
                "days_before_the_date_of_discharge_to_use":row[14],
                "days_after_the_date_of_discharge_to_use":row[15],
                "days_before_the_date_of_hospitalization_to_use_str":str(row[12]),
                "days_after_the_date_of_hospitalization_to_use_str":str(row[13]),
                "days_before_the_date_of_discharge_to_use_str":str(row[14]),
                "days_after_the_date_of_discharge_to_use_str":str(row[15])
            })
        return {
            "system_contents":system_contetns,
            "system_contents_suffix":system_contetns_suffix,
            "document_formats":ret}
