CREATE TABLE DepartmentMaster ( 

    ------------------
    -- 診療科コード
    ------------------
    DepartmentCode NVARCHAR(16),

    ------------------
    -- 診療科名
    ------------------
    DepartmentName NVARCHAR(64),

    CreatedBy VARCHAR(50),
    UpdatedBy VARCHAR(50),
    CreatedDateTime datetime,
    UpdatedDateTime datetime,
    IsDeleted bit
) 
