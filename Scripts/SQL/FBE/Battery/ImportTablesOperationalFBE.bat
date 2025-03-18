@cd /d "%~dp0"
@echo off
set /a BN=6
set /a PN=4

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_BMCConfigDB_Operational_%BN% -i P:\DB\Sql\CreateBatteryConfig.sql

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_FaultsDB_Operational_%BN% -i P:\DB\Sql\CreateFaultsDBTables.sql

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_ReportingDB_Operational_%BN% -i P:\DB\Sql\CreateReportsTables.sql

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_PolicyDB_Operational_%BN% -i P:\DB\Sql\PolicyDBSetup.sql
