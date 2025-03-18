@cd /d "%~dp0"
@echo off
set /a BN=6
set /a PN=4

:: BMCConfig VSIL Bat
sqlcmd -S 10.11.18.3 -d FireBolt_BMCConfigDB_VSIL_1 -i P:\DB\Sql\CreateBatteryConfig.sql
sqlcmd -S 10.11.18.3 -d FireBolt_BMCConfigDB_VSIL_2 -i P:\DB\Sql\CreateBatteryConfig.sql
sqlcmd -S 10.11.18.3 -d FireBolt_BMCConfigDB_VSIL_3 -i P:\DB\Sql\CreateBatteryConfig.sql
sqlcmd -S 10.11.18.3 -d FireBolt_BMCConfigDB_VSIL_4 -i P:\DB\Sql\CreateBatteryConfig.sql

:: FaultsDB VSIL Bat
sqlcmd -S 10.11.18.3 -d FireBolt_FaultsDB_VSIL_1 -i P:\DB\Sql\CreateFaultsDBTables.sql
sqlcmd -S 10.11.18.3 -d FireBolt_FaultsDB_VSIL_2 -i P:\DB\Sql\CreateFaultsDBTables.sql
sqlcmd -S 10.11.18.3 -d FireBolt_FaultsDB_VSIL_3 -i P:\DB\Sql\CreateFaultsDBTables.sql
sqlcmd -S 10.11.18.3 -d FireBolt_FaultsDB_VSIL_4 -i P:\DB\Sql\CreateFaultsDBTables.sql

:: Report VSIL Bat
sqlcmd -S 10.11.18.3 -d FireBolt_ReportingDB_VSIL_1 -i P:\DB\Sql\CreateReportsTables.sql
sqlcmd -S 10.11.18.3 -d FireBolt_ReportingDB_VSIL_2 -i P:\DB\Sql\CreateReportsTables.sql
sqlcmd -S 10.11.18.3 -d FireBolt_ReportingDB_VSIL_3 -i P:\DB\Sql\CreateReportsTables.sql
sqlcmd -S 10.11.18.3 -d FireBolt_ReportingDB_VSIL_4 -i P:\DB\Sql\CreateReportsTables.sql

:: PolicyDB VSIL Bat
sqlcmd -S 10.11.18.3 -d FireBolt_PolicyDB_VSIL_1 -i P:\DB\Sql\PolicyDBSetup.sql
sqlcmd -S 10.11.18.3 -d FireBolt_PolicyDB_VSIL_2 -i P:\DB\Sql\PolicyDBSetup.sql
sqlcmd -S 10.11.18.3 -d FireBolt_PolicyDB_VSIL_3 -i P:\DB\Sql\PolicyDBSetup.sql
sqlcmd -S 10.11.18.3 -d FireBolt_PolicyDB_VSIL_4 -i P:\DB\Sql\PolicyDBSetup.sql



