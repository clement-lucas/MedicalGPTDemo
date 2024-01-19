import os
class OpenAIManager:
    def __init__(self):
        AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE") or "myopenai"
        AZURE_OPENAI_GPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_GPT_DEPLOYMENT") or "chat"
        AZURE_OPENAI_KEY=os.environ.get("AZURE_OPENAI_KEY") or ""
        AZURE_OPENAI_API_VERSION=os.environ.get("AZURE_OPENAI_API_VERSION") or "2023-05-15"
        if ((not AZURE_OPENAI_KEY) or (AZURE_OPENAI_KEY == "")):
            raise Exception("AZURE_OPENAI_KEY is required")

        self._url = f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com/openai/deployments/{AZURE_OPENAI_GPT_DEPLOYMENT}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}"
        #print("gpt url: " + self._url)
        self._headers = {
                "Content-Type": "application/json",
                "api-key": AZURE_OPENAI_KEY
            }

    async def get_response(self, session, messages, temperature, max_tokens):
        async with session.post(self._url, headers=self._headers, json={
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "top_p": 0.95,
            "stop": None
                  }) as resp:
            response_json = await resp.json()
        if resp.status != 200:
            raise Exception(f"Failed to get response from OpenAI. status={resp.status}, response={response_json}")
        return response_json
