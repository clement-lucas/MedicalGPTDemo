CREATE TABLE History (
    Id INT NOT NULL IDENTITY,
    PID VARCHAR(10),  
    DocumentName NVARCHAR(50),
    Prompt NVARCHAR(max),

    ----------------------------
    -- 使用した DocumentFormatIndex の ID
    ----------------------------
    DocumentFormatIndexId INT,

    ----------------------------
    -- 使用した中間データの ID のリスト
    ----------------------------
    IntermediateDataIds NVARCHAR(max),

    Response NVARCHAR(max),
    CompletionTokens INT,
    PromptTokens INT,
    TotalTokens INT,
	CreatedLocalDateTime [datetime],
	UpdatedLocalDateTime [datetime],
    CreatedBy VARCHAR(50),
    UpdatedBy VARCHAR(50),
	CreatedDateTime [datetime],
	UpdatedDateTime [datetime],
	IsDeleted [bit]
    PRIMARY KEY (Id)
);
