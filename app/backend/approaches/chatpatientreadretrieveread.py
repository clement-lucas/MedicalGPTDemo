import openai
from lib.sqlconnector import SQLConnector
from azure.search.documents import SearchClient
from approaches.approach import Approach

# Simple retrieve-then-read implementation, using the Cognitive Search and OpenAI APIs directly. It first retrieves
# top documents from search, then constructs a prompt with them, and then uses OpenAI to generate an completion 
# (answer) with that prompt.
class ChatPatientReadRetrieveReadApproach(Approach):
    prompt_prefix = """
The assistant will answer questions about the contents of the medical file as source. Medical record data consists of the date of receipt and the contents of the description. Be brief in your answers.
Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below. If asking a clarifying question to the user would help, ask the question.
For tabular information return it as an html table. Do not return markdown format.
Each source has a date followed by colon and the actual information, always include date for each fact you use in the response.At the end of the response, give the date of the data used in the format [yyyy/mm/dd].
"""
    def __init__(self, search_client: SearchClient, sql_connector:SQLConnector, chatgpt_deployment: str, gpt_deployment: str, sourcepage_field: str, content_field: str):
        self.search_client = search_client
        self.sql_connector = sql_connector
        self.chatgpt_deployment = chatgpt_deployment
        self.gpt_deployment = gpt_deployment
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field

    def run(self, history: list[dict], history_patient_code: list[dict], overrides: dict) -> any:
        exclude_category = overrides.get("exclude_category") or None

        # ユーザーの入力した質問内容を取得する
        question = history[-1]["user"]

        # 質問内容に期間が含まれていたら、期間を取得する
        # TODO : 期間を取得する処理を実装する

        # ユーザーの入力した患者コードを取得する
        patient_code = history_patient_code[-1]["patientcode"]

        with self.sql_connector.get_conn() as cnxn, cnxn.cursor() as cursor:

            # SQL Server から患者情報を取得する
            cursor.execute("""SELECT TOP (1000) 
                CONVERT(VARCHAR,[Date],111) + ':' + [Record] AS Record
                FROM [dbo].[MedicalRecord] WHERE IsDeleted = 0 AND PatientCode = ?""", patient_code)
            #cursor.execute('SELECT Name FROM Patient WHERE PatientCode = ?', patient_code)
            rows = cursor.fetchall() 

        records = ""
        for row in rows:
            # print(row[0])
            records += row[0] + "\n\n"
        # print(records)
        # historyの中身を確認する
        # print(history)
        messages = self.get_chat_history_as_list(history, question, records)
        # print(messages)

        completion = openai.ChatCompletion.create(
            engine=self.gpt_deployment,
            messages = messages,
            temperature=0.7,
            max_tokens=800,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)
        answer = completion.choices[0].message.content

        # print(answer)
        return {"data_points": "test results", "answer": answer, "thoughts": f"Searched for:<br>q test<br><br>Prompt:<br>"}
    
    def get_chat_history_as_list(self, history, question, records) -> list:
        ret = []
        ret.append({"role":"system","content":self.prompt_prefix})
        for h in reversed(history[:-1]):
            if h.get("user"):
                ret.append({"role":"user","content":h["user"]})
            if h.get("bot"):
                ret.append({"assistant":"system","content":h["bot"]})
        ret.append({"role":"user","content":question + "\n\nカルテデータ：\n\n" + records})
        return ret
    