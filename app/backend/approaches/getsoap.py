from approaches.approach import Approach
from lib.soapmanager import SOAPManager as SOAPManager
from lib.gptconfigmanager import GPTConfigManager

class GetSoapApproach(Approach):
    def __init__(self, sourcepage_field: str, content_field: str):
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, patient_code:str) -> any:

        self.gptconfigmanager = GPTConfigManager()
        # 医師記録の取得
        soap_manager = SOAPManager(self.gptconfigmanager, patient_code, 
            None)
        records_soap = soap_manager.SOAP("soapb")[0]

        if records_soap == "":
            return {"soap":"SOAP が見つかりませんでした。"}
        
        return {"soap":records_soap}

