@cd /d "%~dp0"
@echo off
set /a BN=21
set /a PN=3

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_BMCConfigDB_Operational_Regional -i P:\DB\Sql\CreateBatteryConfig.sql

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_FaultsDB_Operational_Regional -i P:\DB\Sql\CreateFaultsDBTables.sql

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_ReportingDB_Operational_Regional -i P:\DB\Sql\CreateReportsTables.sql

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_PolicyDB_Operational_Regional -i P:\DB\Sql\PolicyDBSetup.sql
