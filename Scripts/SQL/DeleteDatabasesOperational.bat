@echo off
setlocal enabledelayedexpansion
set /a BN=10
set /a PN=4
echo Deleting Databases for Battery number %BN% Operational Mode
set CDBase="C:\Windows\Temp\DeleteDatabases.sql"
del %CDBase%

for %%A in (
    FireBolt_BMCConfigDB_Operational
    FireBolt_FaultsDB_Operational
    FireBolt_PolicyDB_Operational
    FireBolt_ReportingDB_Operational
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
    FireBolt_BMCConfigDB_Operational
    FireBolt_FaultsDB_Operational
    FireBolt_PolicyDB_Operational
    FireBolt_ReportingDB_Operational
) do (
    del "C:\FireBoltDB\%%A_%BN%.mdf"
    del "C:\FireBoltDB\%%A_%BN%_log.ldf"
)

echo Databases and files deleted successfully!
