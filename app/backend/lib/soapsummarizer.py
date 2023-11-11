import openai
from lib.tokencounter import TokenCounter
from lib.gptconfigmanager import GPTConfigManager

class SOAPSummarizer:

    @property
    def capacity_for_befor_and_after_summarize_text(self):
        return self._capacity_for_befor_and_after_summarize_text

    def __init__(self, 
                gptconfigmanager:GPTConfigManager, 
                engine:str):
        self._engine = engine
        self._max_total_tokens = int(gptconfigmanager.get_value("MAX_TOTAL_TOKENS"))
        self._model_name_for_tiktoken = gptconfigmanager.get_value("MODEL_NAME_FOR_TIKTOKEN")
        self._system_content = gptconfigmanager.get_value("SUMMARIZE_SOAP_PROMPT_SYSTEM_CONTENTS")
        self._user_content = gptconfigmanager.get_value("SUMMARIZE_SOAP_PROMPT_USER_CONTENTS")
        self._temperature = float(gptconfigmanager.get_value("SUMMARIZE_SOAP_TEMPERATURE"))

        self._capacity_for_befor_and_after_summarize_text = self._get_capacity_for_befor_text()

    # 要約前のテキストとして渡せる最大トークン数を返却する。
    def _get_capacity_for_befor_text(self):
        messages = [{"role":"system","content": self._system_content},
            {"role":"user","content": self._user_content.format(expected_token_num='', soap='')}]
        tokens = TokenCounter.num_tokens_from_messages(messages, self._model_name_for_tiktoken)
        return self._max_total_tokens - tokens
    
    # GPT を利用して SOAP を要約する。
    def summarize(self, soap:str, expected_token_num:int):
        messages = [{"role":"system","content": self._system_content},
            {"role":"user","content": self._user_content.format(expected_token_num=expected_token_num, soap=soap)}]
        
        # print(expected_token_num)

        completion = openai.ChatCompletion.create(
            engine=self._engine,
            messages = messages,
            temperature=self._temperature,
            max_tokens=expected_token_num,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None)

        # print(completion.choices[0].message.content)
        # print(completion.usage.completion_tokens)
        # print(completion.usage.prompt_tokens)
        # print(completion.usage.total_tokens)
        ret = completion.choices[0].message.content
        log = ''.join([str(TokenCounter.count(soap, self._model_name_for_tiktoken)), 
                       "=>", 
                       str(TokenCounter.count(ret, self._model_name_for_tiktoken)), ", "])
        return ret, completion.usage, log
