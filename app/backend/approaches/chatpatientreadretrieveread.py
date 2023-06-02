import openai
import pyodbc
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from approaches.approach import Approach
from text import nonewlines

# Simple retrieve-then-read implementation, using the Cognitive Search and OpenAI APIs directly. It first retrieves
# top documents from search, then constructs a prompt with them, and then uses OpenAI to generate an completion 
# (answer) with that prompt.
class ChatPatientReadRetrieveReadApproach(Approach):
    prompt_prefix = """<|im_start|>system
The assistant will answer questions about the contents of the medical file as source. Medical record data consists of the date of receipt and the contents of the description. Be brief in your answers.
Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below. If asking a clarifying question to the user would help, ask the question.
For tabular information return it as an html table. Do not return markdown format.
Each source has a date followed by colon and the actual information, always include date for each fact you use in the response.At the end of the response, give the date of the data used in the format [yyyy/mm/dd].
{follow_up_questions_prompt}
{injected_prompt}
Sources:
{sources}
<|im_end|>
{chat_history}
"""

    follow_up_questions_prompt_content = """Generate three very brief follow-up questions that the user would likely ask related with the answer. 
    Use double angle brackets to reference the questions, e.g. <<Are there exclusions for prescriptions?>>.
    Try not to repeat questions that have already been asked.
    Only generate questions and do not generate any text before or after the questions, such as 'Next Questions'"""

    query_prompt_template = """Below is a history of the conversation so far, and a new question asked by the user that needs to be answered by searching in a knowledge base about medical journal and research.
    Generate a search query based on the conversation and the new question. 
    Do not include cited source filenames and document names e.g info.txt or doc.pdf in the search query terms.
    Do not include any text inside [] or <<>> in the search query terms.
    If the question is not in English, translate the question to English before generating the search query.

Chat History:
{chat_history}

Question:
{question}

Search query:
"""

    def __init__(self, search_client: SearchClient, chatgpt_deployment: str, gpt_deployment: str, sourcepage_field: str, content_field: str):
        self.search_client = search_client
        self.chatgpt_deployment = chatgpt_deployment
        self.gpt_deployment = gpt_deployment
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field

    def run(self, history: list[dict], history_patient_code: list[dict], overrides: dict) -> any:
        use_semantic_captions = True if overrides.get("semantic_captions") else False
        top = overrides.get("top") or 3
        exclude_category = overrides.get("exclude_category") or None
        filter = "category ne '{}'".format(exclude_category.replace("'", "''")) if exclude_category else None

        # ユーザーの入力した質問内容を取得する
        question = history[-1]["user"]

        # 質問内容に期間が含まれていたら、期間を取得する
        # TODO : 期間を取得する処理を実装する

        # ユーザーの入力した患者コードを取得する
        patient_code = history_patient_code[-1]["patientcode"]

        # SQL Server に接続する
        # TODO 接続情報の外部化
        server = 'tcp:medical-record.database.windows.net' 
        database = 'MedicalRecordDB' 
        username = 'medical-record-admin' 
        password = '' 
        # ENCRYPT defaults to yes starting in ODBC Driver 18. It's good to always specify ENCRYPT=yes on the client side to avoid MITM attacks.
        cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';ENCRYPT=yes;UID='+username+';PWD='+ password)
        cursor = cnxn.cursor()

        # SQL Server から患者情報を取得する
        cursor.execute("""SELECT TOP (1000) 
            CONVERT(VARCHAR,[Date],111) + ':' + [Record] AS Record
            FROM [dbo].[MedicalRecord] WHERE PatientCode = ?""", patient_code)
        #cursor.execute('SELECT Name FROM Patient WHERE PatientCode = ?', patient_code)
        rows = cursor.fetchall() 
        records = ""
        for row in rows:
            print(row[0])
            records += row[0] + "\n\n"
        print(records)

        follow_up_questions_prompt = self.follow_up_questions_prompt_content if overrides.get("suggest_followup_questions") else ""
        prompt = self.prompt_prefix.format(injected_prompt="", sources=records, chat_history=self.get_chat_history_as_text(history), follow_up_questions_prompt=follow_up_questions_prompt)
        print(prompt)
        #prompt = records.join("\nAnswer the following question from the text above in Japanese.\n\nQuestion:\n" + question + "\n\nAnswer:\n<|im_end|>")
        # STEP 3: Generate a contextual and content specific answer using the search results and chat history
        completion = openai.Completion.create(
            engine=self.chatgpt_deployment, 
            prompt=prompt, 
            temperature=overrides.get("temperature") or 0.7, 
            max_tokens=1024, 
            n=1, 
            stop=["<|im_end|>", "<|im_start|>"])

        # # STEP 1: Generate an optimized keyword search query based on the chat history and the last question
        # prompt = self.query_prompt_template.format(chat_history=self.get_chat_history_as_text(history, include_last_turn=False), question=question)
        # completion = openai.Completion.create(
        #     engine=self.gpt_deployment, 
        #     prompt=prompt, 
        #     temperature=0.0, 
        #     max_tokens=32, 
        #     n=1, 
        #     stop=["\n"])
        # q = completion.choices[0].text

        # # STEP 2: Retrieve relevant documents from the search index with the GPT optimized query
        # if overrides.get("semantic_ranker"):
        #     r = self.search_client.search(q, 
        #                                   filter=filter,
        #                                   query_type=QueryType.SEMANTIC, 
        #                                   query_language="en-us", 
        #                                   query_speller="lexicon", 
        #                                   semantic_configuration_name="default", 
        #                                   top=top, 
        #                                   query_caption="extractive|highlight-false" if use_semantic_captions else None)
        # else:
        #     r = self.search_client.search(q, filter=filter, top=top)
        # if use_semantic_captions:
        #     results = [doc[self.sourcepage_field] + ": " + nonewlines(" . ".join([c.text for c in doc['@search.captions']])) for doc in r]
        # else:
        #     results = [doc[self.sourcepage_field] + ": " + nonewlines(doc[self.content_field]) for doc in r]
        # content = "\n".join(results)

        # follow_up_questions_prompt = self.follow_up_questions_prompt_content if overrides.get("suggest_followup_questions") else ""
        
        # # Allow client to replace the entire prompt, or to inject into the exiting prompt using >>>
        # prompt_override = overrides.get("prompt_template")
        # if prompt_override is None:
        #     prompt = self.prompt_prefix.format(injected_prompt="", sources=content, chat_history=self.get_chat_history_as_text(history), follow_up_questions_prompt=follow_up_questions_prompt)
        # elif prompt_override.startswith(">>>"):
        #     prompt = self.prompt_prefix.format(injected_prompt=prompt_override[3:] + "\n", sources=content, chat_history=self.get_chat_history_as_text(history), follow_up_questions_prompt=follow_up_questions_prompt)
        # else:
        #     prompt = prompt_override.format(sources=content, chat_history=self.get_chat_history_as_text(history), follow_up_questions_prompt=follow_up_questions_prompt)

        # # STEP 3: Generate a contextual and content specific answer using the search results and chat history
        # completion = openai.Completion.create(
        #     engine=self.chatgpt_deployment, 
        #     prompt=prompt, 
        #     temperature=overrides.get("temperature") or 0.7, 
        #     max_tokens=1024, 
        #     n=1, 
        #     stop=["<|im_end|>", "<|im_start|>"])

        print(completion.choices[0].text)
        return {"data_points": "test results", "answer": completion.choices[0].text, "thoughts": f"Searched for:<br>q test<br><br>Prompt:<br>" + prompt.replace('\n', '<br>')}
    
    def get_chat_history_as_text(self, history, include_last_turn=True, approx_max_tokens=1000) -> str:
        history_text = ""
        for h in reversed(history if include_last_turn else history[:-1]):
            history_text = """<|im_start|>user""" +"\n" + h["user"] + "\n" + """<|im_end|>""" + "\n" + """<|im_start|>assistant""" + "\n" + (h.get("bot") + """<|im_end|>""" if h.get("bot") else "") + "\n" + history_text
            if len(history_text) > approx_max_tokens*4:
                break    
        return history_text