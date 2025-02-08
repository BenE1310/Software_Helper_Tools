@cd /d "%~dp0"
@echo off
set /a BN=0
set USER=123
set PASS=

sqlcmd -S "." -d FireBolt_BMCConfigDB_Operational_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\CreateBatteryConfig.sql

sqlcmd -S "." -d FireBolt_FaultsDB_Operational_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\CreateFaultsDBTables.sql

sqlcmd -S "." -d FireBolt_ReportingDB_Operational_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\CreateReportsTables.sql

sqlcmd -S "." -d FireBolt_PolicyDB_Operational_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\PolicyDBSetup.sql
