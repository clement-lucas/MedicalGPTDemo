from approaches.approach import Approach
from lib.documentformatmanager import DocumentFormatManager
DOCUMENT_FORMAT_KIND_SYSTEM_CONTENT = 0
DEFAULT_DEPARTMENT_CODE = "0000"

class GetDocumentFormatApproach(Approach):
    def __init__(self, sourcepage_field: str, content_field: str):
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, document_name: str, department_code:str, 
            icd10_code:str, 
            user_id:str,
            force_master:bool   # マスターを強制的に取得するかどうか
            ) -> any:
        
        manager = DocumentFormatManager(
            document_name, department_code,
            icd10_code, 
            user_id,
            force_master)
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
                "use_discharge_medicine_records":row[10]
            })
        return {
            "system_contents":system_contetns,
            "system_contents_suffix":system_contetns_suffix,
            "document_formats":ret}
