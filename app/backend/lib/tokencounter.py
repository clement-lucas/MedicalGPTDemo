import tiktoken

class TokenCounter:
    # 文字列の Token 数を返却する
    # 　以下の関数から得られるカウントは、見積もりであり、永久的な保証ではありません。
    #
    #   model_name_for_tiktoken:
    #        "gpt-3.5-turbo-0613",
    #        "gpt-3.5-turbo-16k-0613",
    #        "gpt-4-0314",
    #        "gpt-4-32k-0314",
    #        "gpt-4-0613",
    #        "gpt-4-32k-0613",
    #
    # 　see also 
    # 　　https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    @staticmethod
    def count(text:str, model_name_for_tiktoken:str):
        encoding = tiktoken.encoding_for_model(model_name_for_tiktoken)
        num_tokens = len(encoding.encode(text))
        return num_tokens
    
    # チャットコンプリーションAPI呼び出しのためのトークン数の計算
    # 　以下の関数から得られるカウントは、見積もりであり、永久的な保証ではありません。
    #
    #   model_name_for_tiktoken:
    #        "gpt-3.5-turbo-0613",
    #        "gpt-3.5-turbo-16k-0613",
    #        "gpt-4-0314",
    #        "gpt-4-32k-0314",
    #        "gpt-4-0613",
    #        "gpt-4-32k-0613",
    #
    # 　see also 
    # 　　https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    @staticmethod
    def num_tokens_from_messages(messages:list, model_name_for_tiktoken:str):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model_name_for_tiktoken)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model_name_for_tiktoken in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model_name_for_tiktoken == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model_name_for_tiktoken:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return TokenCounter.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model_name_for_tiktoken:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return TokenCounter.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model_name_for_tiktoken}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

