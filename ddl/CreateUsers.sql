CREATE TABLE Users (
    UserId VARCHAR(50) NOT NULL,
    UserName NVARCHAR(max) NOT NULL,
	CreatedDateTime [datetime] NULL,
	UpdatedDateTime [datetime] NULL,
	IsDeleted [bit] NULL
);
