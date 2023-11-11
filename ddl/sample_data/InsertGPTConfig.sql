INSERT INTO [dbo].[GPTConfig] (ConfigKey, ConfigDescription, ConfigValue,
    CreatedDateTime,
	UpdatedDateTime,
	IsDeleted
)
     VALUES
('MODEL_NAME_FOR_TIKTOKEN', N'tiktoken による トークン数見積取得に用いるモデル名。ex)  
gpt-3.5-turbo-0613, 
gpt-3.5-turbo-16k-0613, 
gpt-4-0314,
gpt-4-32k-0314,
gpt-4-0613,
gpt-4-32k-0613',
'gpt-3.5-turbo-0613', GETDATE(), GETDATE(), 0),

('MAX_TOTAL_TOKENS', N'GPT モデルが受け入れ可能な最大 Token 数。送信プロンプトと応答の合計。バッファを持たせ実際よりも小さい値を設定しても良い。', 
'3900', GETDATE(), GETDATE(), 0),

('COMPRESSIBILITY_FOR_SUMMARY', N'繰り返し要約を行う際の一回の要約処理における圧縮率。', '0.7', GETDATE(), GETDATE(), 0),

('SUMMARIZE_SOAP_PROMPT_USER_CONTENTS', N'SOAP の要約に用いるプロンプト（user contents の部分）。', '
Summarize the following text that captures the main idea within {expected_token_num} tokens.
Answers should be provided in the same language as the text. If the text is Japanese, please provide the summary result in Japanese as well.
Text:
{soap}', GETDATE(), GETDATE(), 0),

('SUMMARIZE_SOAP_PROMPT_SYSTEM_CONTENTS', 'SOAP の要約に用いるプロンプト（system contents の部分）。', 
'You are AI assistant.', GETDATE(), GETDATE(), 0),

('SUMMARIZE_SOAP_TEMPERATURE', N'SOAP 要約に使用する temperature.', '0.01', GETDATE(), GETDATE(), 0)
