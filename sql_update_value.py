import datetime
import os
from time import sleep
from typing import dataclass_transform

BN=8

def generate_sql_script(octet_value):
    sql_script = f"""
    -- Query for CombainTraining & Training Mode --
    DECLARE @serialNumber INTEGER
    DECLARE @sendPort INTEGER
    DECLARE @recievePort INTEGER
    SET @serialNumber = 301;
    SET @recievePort = 1301;
    SET @sendPort = 1801;

    WHILE @serialNumber < 325 
    BEGIN 
        INSERT INTO dbo.MfuAddressBook VALUES (@serialNumber, '10.11.{octet_value}8.3', @sendPort, @recievePort)
        SET @sendPort = @sendPort + 1;
        SET @serialNumber = @serialNumber + 1;
        SET @recievePort = @recievePort + 1;
    END
    """
    return sql_script

# Example usage
sql_code = generate_sql_script(BN)

# Print or save the generated SQL script
print(sql_code)

# Optionally, write it to a file
with open(f"Scripts/SQL/adding_launcher_training_mode_bt_{BN}.sql", "w") as file:
    file.write(sql_code)

sleep(3)
os.remove(f"Scripts/SQL/adding_launcher_training_mode_bt_{BN}.sql")