from lib.tokencounter import TokenCounter
from lib.gptconfigmanager import GPTConfigManager
from lib.openaimanager import OpenAIManager
from lib.soapsummarizerexception import SOAPSummarizerException

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
    async def summarize(self, soap:str, expected_token_num:int, session):
        messages = [{"role":"system","content": self._system_content},
            {"role":"user","content": self._user_content.format(expected_token_num=expected_token_num, soap=soap)}]
        
        # print(expected_token_num)
        openaimanager = OpenAIManager()
        completion = await openaimanager.get_response(session, messages, self._temperature, expected_token_num)

        # completion が要素["choices"] を持っていない場合は、なしとして扱う
        content_error_message = "要約処理に失敗したため、処理を中断します。AI からのレスポンスが不正です。"
        if (not 'choices' in completion) \
        or (len(completion['choices']) == 0) \
        or (not 'message' in completion['choices'][0]):
            print(content_error_message)
            print(f"Failed to get response from OpenAI. response={completion}")
            raise SOAPSummarizerException(content_error_message)
        if ('finish_reason' in completion['choices'][0]) and (completion['choices'][0]['finish_reason'] == "content_filter"):
            errmsg = "要約処理が AI によりフィルタリングされました。\n"
            if 'content' in completion['choices'][0]['message']:
                errmsg += "詳細：" + completion['choices'][0]['message']['content']
            print(errmsg)
            raise SOAPSummarizerException(errmsg)
        if not 'content' in completion['choices'][0]['message']:
            print(content_error_message)
            print(f"Failed to get response from OpenAI. response={completion}")
            raise SOAPSummarizerException(content_error_message)

        ret = completion['choices'][0]['message']['content']
        log = ''.join([str(TokenCounter.count(soap, self._model_name_for_tiktoken)), 
                       "=>", 
                       str(TokenCounter.count(ret, self._model_name_for_tiktoken)), ", "])
        return ret, completion['usage'], log
