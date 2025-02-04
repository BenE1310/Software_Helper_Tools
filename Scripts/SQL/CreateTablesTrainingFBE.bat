@cd /d "%~dp0"
@echo off
set /a BN=1
set USER=mPrest
set PASS=MprIt12#4%

sqlcmd -S "." -d FireBolt_BMCConfigDB_Training_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\CreateBatteryConfig.sql

sqlcmd -S "." -d FireBolt_FaultsDB_Training_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\CreateFaultsDBTable.sql

sqlcmd -S "." -d FireBolt_ReportingDB_Training_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\CreateReportsTables.sql

sqlcmd -S "." -d FireBolt_PolicyDB_Training_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\PolicyDBSetup.sql
