
    -- Query for CombainTraining & Training Mode --
    DECLARE @serialNumber INTEGER
    DECLARE @sendPort INTEGER
    DECLARE @recievePort INTEGER
    SET @serialNumber = 301;
    SET @recievePort = 1301;
    SET @sendPort = 1801;

    WHILE @serialNumber < 325 
    BEGIN 
        INSERT INTO dbo.MfuAddressBook VALUES (@serialNumber, '10.12.38.2', @sendPort, @recievePort)
        SET @sendPort = @sendPort + 1;
        SET @serialNumber = @serialNumber + 1;
        SET @recievePort = @recievePort + 1;
    END
    