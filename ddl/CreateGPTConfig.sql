CREATE TABLE GPTConfig (
    ConfigKey VARCHAR(128) NOT NULL,
    ConfigDescription NVARCHAR(max),
    ConfigValue NVARCHAR(max),
    CreatedBy VARCHAR(50),
    UpdatedBy VARCHAR(50),
	CreatedDateTime [datetime] NULL,
	UpdatedDateTime [datetime] NULL,
	IsDeleted [bit] NULL
);
