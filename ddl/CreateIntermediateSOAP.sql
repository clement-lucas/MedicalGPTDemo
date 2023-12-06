CREATE TABLE IntermediateSOAP ( 
    ------------------
    -- ID
    ------------------
    Id INT NOT NULL IDENTITY,

    ------------------
    -- 元データNO
    -- EXTBDH1.DOC_NO と対応する。
    ------------------
    OriginalDocNo CHAR(30),  

    ------------------
    -- 重複元データID
    -- IntermediateSOAP.Id と対応する。
    ------------------
    DuplicateSourceDataId INT,

    ------------------
    -- PID
    ------------------
    Pid NUMERIC(10),  

    ------------------
    -- EXTBDH1.DOCDATE。
    ------------------
    DocDate NUMERIC(14),  

    ------------------
    -- SOAP の種類。
    -- s, o, a, p, b(#) のいずれか。
    ------------------
    SoapKind CHAR(1),

    ------------------
    -- 中間データとしてのSOAP。
    ------------------
    IntermediateData NVARCHAR(max),

    CreatedBy VARCHAR(50),
    UpdatedBy VARCHAR(50),
    CreatedDateTime datetime,
    UpdatedDateTime datetime,
    IsDeleted bit,
    PRIMARY KEY (Id)
) 
