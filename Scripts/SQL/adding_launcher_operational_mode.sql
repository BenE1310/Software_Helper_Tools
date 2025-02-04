-- Query for Operatinal Mode --

DECLARE @serialNumber INTEGER
SET @serialNumber = 1;
WHILE @serialNumber < 251 
BEGIN 
	INSERT INTO dbo.MfuAddressBook VALUES (@serialNumber, NULL, NULL, NULL)
	SET @serialNumber = @serialNumber + 1;

END