CREATE TABLE History (
    Id INT NOT NULL IDENTITY,
    UserId VARCHAR(50) NOT NULL,
    PID VARCHAR(10),  
    DocumentName NVARCHAR(50) NOT NULL,
    Prompt NVARCHAR(max) NOT NULL,
    MedicalRecord NVARCHAR(max) NOT NULL,
    ----------------------------
    -- 要約された診療記録
    -- <CATEGORY>カテゴリー名</CATEGORY>
    -- <SOAP>要約された診療記録</SOAP>
    -- <COMPLETION_TOKENS_FOR_SUMMARIZE>要約処理に使った総応答 Token 数</COMPLETION_TOKENS_FOR_SUMMARIZE>
    -- <PROMPT_TOKENS_FOR_SUMMARIZE>要約処理に使った総プロンプト Token 数</PROMPT_TOKENS_FOR_SUMMARIZE>
    -- <TOTAL_TOKENS_FOR_SUMMARIZE>要約処理に使った総トータル Token 数</TOTAL_TOKENS_FOR_SUMMARIZE>
    -- <SUMMARIZE_LOG>要約処理 Token 数記録</SUMMARIZE_LOG>
    -- の繰り返しとして記録される。
    ----------------------------
    SummarizedMedicalRecord NVARCHAR(max) NOT NULL,
    Response NVARCHAR(max) NOT NULL,
    CompletionTokens INT NOT NULL,
    PromptTokens INT NOT NULL,
    TotalTokens INT NOT NULL,
	CreatedDateTime [datetime] NULL,
	UpdatedDateTime [datetime] NULL,
	IsDeleted [bit] NULL
    PRIMARY KEY (Id)
);
