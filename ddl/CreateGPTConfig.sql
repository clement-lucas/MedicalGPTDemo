CREATE TABLE GPTConfig (
    ConfigKey VARCHAR(128) NOT NULL,
    ConfigDescription NVARCHAR(max),
    ConfigValue NVARCHAR(max),
	CreatedDateTime [datetime] NULL,
	UpdatedDateTime [datetime] NULL,
	IsDeleted [bit] NULL
);
