@echo off
setlocal enabledelayedexpansion
set /a BN=10
set /a PN=4
echo Deleting Databases For VSIL Bat
set CDBase="C:\Windows\Temp\DeleteDatabases.sql"
del %CDBase%

for %%A in (
			FireBolt_BMCConfigDB_VSIL_Regional
			FireBolt_FaultsDB_VSIL_Regional
			FireBolt_PolicyDB_VSIL_Regional
			FireBolt_ReportingDB_VSIL_Regional
) do (
(
>> %CDBase% echo USE [master]
>> %CDBase% echo GO
>> %CDBase% echo ALTER DATABASE [%%A] SET SINGLE_USER WITH ROLLBACK IMMEDIATE
>> %CDBase% echo GO
>> %CDBase% echo DROP DATABASE [%%A]
>> %CDBase% echo GO
))

sqlcmd -S 10.11.218.3 -i %CDBase%

echo Removing database files...
for %%A in (
			FireBolt_BMCConfigDB_VSIL_Regional
			FireBolt_FaultsDB_VSIL_Regional
			FireBolt_PolicyDB_VSIL_Regional
			FireBolt_ReportingDB_VSIL_Regional
) do (
    del "C:\FireBoltDB\%%A.mdf"
    del "C:\FireBoltDB\%%A_log.ldf"
)

echo Databases and files deleted successfully!
