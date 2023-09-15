INSERT INTO [dbo].[Users]
           ([UserId]
           ,[UserName]
           ,[CreatedDateTime]
           ,[UpdatedDateTime]
           ,[IsDeleted])
     VALUES
           ('000001'
           ,'テストユーザー001'
           ,GETDATE()
           ,GETDATE()
           ,0)
GO


