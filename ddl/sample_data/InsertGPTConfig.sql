INSERT INTO [dbo].[GPTConfig] (ConfigKey, ConfigDescription, ConfigValue,
    CreatedBy,
    UpdatedBy,
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
'gpt-3.5-turbo-16k-0613', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),

('MAX_TOTAL_TOKENS', N'GPT モデルが受け入れ可能な最大 Token 数。送信プロンプトと応答の合計。バッファを持たせ実際よりも小さい値を設定しても良い。', 
'14000', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),

('COMPRESSIBILITY_FOR_SUMMARY', N'繰り返し要約を行う際の一回の要約処理における圧縮率。', '0.7', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),

('SUMMARIZE_SOAP_PROMPT_USER_CONTENTS', N'SOAP の要約に用いるプロンプト（user contents の部分）。', '
以下は医師の書いた SOAP 文書です。これを {expected_token_num} 以下で要約してください。
文書は、S,O,A,P,＃ の各セクションから構成されます。要約は、各セクション内で行ってください。セクション間での内容の混在は許可されません。
例えば、Sセクションの内容を要約する場合、Sセクションの内容のみを用いて要約を行ってください。
要約後の文書は、以下のようにセクションで分けられた形式で出力してください。
ただし、元々の文章に当該のセクションが存在しない場合は、セクションを出力しないでください。

S：
要約されたS

O：
要約されたO

A：
要約されたA

P：
要約されたP

＃：
要約された＃

{soap}', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),

('SUMMARIZE_SOAP_PROMPT_SYSTEM_CONTENTS', 'SOAP の要約に用いるプロンプト（system contents の部分）。', 
'You are AI assistant.', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),

('SUMMARIZE_SOAP_TEMPERATURE', N'SOAP 要約に使用する temperature.', '0.01', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),

('TOKEN_NUM_FOR_QUESTION', N'退院時サマリ作成時の GPT Call にて、SOAP 部分を除く質問文の領域に割り当てるトークン数.', '1200', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0)
