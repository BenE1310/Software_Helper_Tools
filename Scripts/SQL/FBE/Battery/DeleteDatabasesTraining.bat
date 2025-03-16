@echo off
setlocal enabledelayedexpansion
set /a BN=0
set /a PN=0

echo Deleting Databases for Battery number %BN% Training Mode
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
>> %CDBase% echo ALTER DATABASE [%%A_%BN%] SET SINGLE_USER WITH ROLLBACK IMMEDIATE
>> %CDBase% echo GO
>> %CDBase% echo DROP DATABASE [%%A_%BN%]
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
    del "C:\FireBoltDB\%%A_%BN%.mdf"
    del "C:\FireBoltDB\%%A_%BN%_log.ldf"
)

echo Databases and files deleted successfully!
