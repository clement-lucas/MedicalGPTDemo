# 削除予定

from approaches.approach import Approach
from lib.soapmanager import SOAPManager as SOAPManager
from lib.gptconfigmanager import GPTConfigManager
from lib.sqlconnector import SQLConnector

class GetSoapApproach(Approach):
    def __init__(self, sql_connector:SQLConnector, sourcepage_field: str, content_field: str):
        self.sql_connector = sql_connector
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field
        
    def run(self, pid:str) -> any:

        self.gptconfigmanager = GPTConfigManager(self.sql_connector)
        # 医師記録の取得
        soap_manager = SOAPManager(self.sql_connector, '', self.gptconfigmanager, pid, '', 0, True)
        records_soap = soap_manager.SOAP("soapb", True)

        if records_soap == "":
            return {"soap":"SOAP が見つかりませんでした。"}
        
        return {"soap":records_soap}

