CREATE TABLE SummarizedSOAPCache ( 
    ------------------
    -- PID
    ------------------
    Pid NUMERIC(10),  

    ------------------
    -- 要約に用いた最後の EXTBDH1.DOCDATE。
    -- この日付以降の EXTBDH1 は要約に使用されていない。
    ------------------
    LastDocDate NUMERIC(14),  

    ------------------
    -- SOAP の種類。
    -- s, o, a, p, b のいずれか。
    ------------------
    SoapKind CHAR(1),

    ------------------
    -- 要約された SOAP。
    ------------------
    SummarizedSOAP NVARCHAR(max),

    ------------------
    -- 要約に用いた CompletionTokens。
    ------------------
    CompletionTokensForSummarize int,

    ------------------
    -- 要約に用いた PromptTokens。
    ------------------
    PromptTokensForSummarize int,

    ------------------
    -- 要約に用いた TotalTokens。
    ------------------
    TotalTokensForSummarize int,

    ------------------
    -- 要約ログ。
    ------------------
    SummarizeLog NVARCHAR(max),

    CreatedBy VARCHAR(50),
    UpdatedBy VARCHAR(50),
    CreatedDateTime datetime,
    UpdatedDateTime datetime,
    IsDeleted bit
) 
