
INSERT INTO [dbo].[DepartmentMaster]
           ([DepartmentCode]
           ,[DepartmentName]
           ,[CreatedBy]
           ,[UpdatedBy]
           ,[CreatedDateTime]
           ,[UpdatedDateTime]
           ,[IsDeleted])
     VALUES
('0001', '内科', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
('0002', '外科', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
('0003', '小児科', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0),
('0004', '産婦人科', 'SYSTEM', 'SYSTEM', GETDATE(), GETDATE(), 0) 
