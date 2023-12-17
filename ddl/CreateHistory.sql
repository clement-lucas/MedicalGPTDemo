CREATE TABLE History (
    Id INT NOT NULL IDENTITY,
    PID VARCHAR(10),  
    DocumentName NVARCHAR(50),
    Prompt NVARCHAR(max),

    ----------------------------
    -- 入院日
    ----------------------------
    HospitalizationDate VARCHAR(10),

    ----------------------------
    -- 退院日
    ----------------------------
    DischargeDate VARCHAR(10), 

    ----------------------------
    -- 使用した DocumentFormatIndex の ID
    ----------------------------
    DocumentFormatIndexId INT,

    ----------------------------
    -- 使用した元データの EXTBDH1.DOC_NO のリスト
    ----------------------------
    OriginalDocNoList VARCHAR(max),

    ----------------------------
    -- 使用した中間データの ID のリスト
    ----------------------------
    IntermediateDataIds VARCHAR(max),

    ----------------------------
    -- 使用したデータの期間と対象SOAPのリスト
    -- 例) 
    -- 【入院までの経過 データ使用期間】
    -- 2014/02/18 00:00:00 ～ 2014/02/22 23:59:59
    -- soap
    -- 
    -- 【入院経過 データ使用期間】
    -- 2014/02/18 00:00:00 ～ 2014/02/21 23:59:59
    -- a
    -- 
    -- 【退院時状況 データ使用期間】
    -- 2014/02/19 00:00:00 ～ 2014/02/22 23:59:59
    -- op
    ----------------------------
    UseDateRangeList NVARCHAR(max),

    ----------------------------
    -- 各カテゴリーの SOAP 入力データ
    ----------------------------
    SoapForCategories NVARCHAR(max),

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
