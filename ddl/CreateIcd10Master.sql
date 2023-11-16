CREATE TABLE Icd10Master ( 

    ------------------
    -- ICD10 コード
    ------------------
    Icd10Code NVARCHAR(16),

    ------------------
    -- CodeLevel
    -- 0: 大項目
    -- 1: 中項目
    -- 2: 小項目
    ------------------
    CodeLevel INT,

    ------------------
    -- Caption
    ------------------
    Caption NVARCHAR(256),

    CreatedBy VARCHAR(50),
    UpdatedBy VARCHAR(50),
    CreatedDateTime datetime,
    UpdatedDateTime datetime,
    IsDeleted bit
) 
