@echo off
setlocal enabledelayedexpansion
set /a BN=0
set /a PN=0

echo Deleting Databases for Regional Training Mode
set CDBase="C:\Windows\Temp\DeleteDatabases.sql"
del %CDBase%

for %%A in (
    FireBolt_BMCConfigDB_Training
    FireBolt_FaultsDB_Training
    FireBolt_PolicyDB_Training
    FireBolt_ReportingDB_Training
) do (
(
>> %CDBase% echo USE [master]
>> %CDBase% echo GO
>> %CDBase% echo ALTER DATABASE [%%A_Regional] SET SINGLE_USER WITH ROLLBACK IMMEDIATE
>> %CDBase% echo GO
>> %CDBase% echo DROP DATABASE [%%A_Regional]
>> %CDBase% echo GO
))

sqlcmd -S 10.11.%BN%8.%PN% -i %CDBase%

echo Removing database files...
for %%A in (
    FireBolt_BMCConfigDB_Training
    FireBolt_FaultsDB_Training
    FireBolt_PolicyDB_Training
    FireBolt_ReportingDB_Training
) do (
    del "C:\FireBoltDB\%%A_Regional.mdf"
    del "C:\FireBoltDB\%%A_Regional_log.ldf"
)

echo Databases and files deleted successfully!
