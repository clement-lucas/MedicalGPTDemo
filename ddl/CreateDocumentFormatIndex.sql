CREATE TABLE DocumentFormatIndex ( 
    ------------------
    -- ID
    ------------------
    IndexId INT NOT NULL IDENTITY,

    ------------------
    -- マスターフラグ
    ------------------
    IsMaster bit,

    ------------------
    -- インデックス名
    ------------------
    IndexName NVARCHAR(128),

    ------------------
    -- ドキュメント名
    -- Ex) 退院時サマリ
    ------------------
    DocumentName NVARCHAR(32),

    ------------------
    -- GPT Model 名
    -- Ex) gpt-35-turbo, gpt-4
    -- .env ファイルの AZURE_GPT_MODEL_NAME および、
    -- アプリケーション設定の同設定値に設定されているものと同じものを設定する
    ------------------
    GPTModelName VARCHAR(32),
    
    ------------------
    -- 検索用タグ
    ------------------
    Tags NVARCHAR(1024),

    CreatedBy VARCHAR(50),
    UpdatedBy VARCHAR(50),
    CreatedDateTime datetime,
    UpdatedDateTime datetime,
    IsDeleted bit,
    PRIMARY KEY (IndexId)
) 
