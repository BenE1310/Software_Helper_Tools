@cd /d "%~dp0"
@echo off
set /a BN=3
set USER=123
set PASS=12

sqlcmd -S "." -d FireBolt_BMCConfigDB_Training_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\CreateBatteryConfig.sql

sqlcmd -S "." -d FireBolt_FaultsDB_Training_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\CreateFaultsDBTables.sql

sqlcmd -S "." -d FireBolt_ReportingDB_Training_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\CreateReportsTables.sql

sqlcmd -S "." -d FireBolt_PolicyDB_Training_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\PolicyDBSetup.sql
