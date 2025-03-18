@cd /d "%~dp0"
@echo off
set /a BN=0
set /a PN=0

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_BMCConfigDB_Training_Regional -i P:\DB\Sql\CreateBatteryConfig.sql

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_FaultsDB_Training_Regional -i P:\DB\Sql\CreateFaultsDBTables.sql

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_ReportingDB_Training_Regional -i P:\DB\Sql\CreateReportsTables.sql

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_PolicyDB_Training_Regional -i P:\DB\Sql\PolicyDBSetup.sql
