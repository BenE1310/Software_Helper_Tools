@cd /d "%~dp0"
@echo off
set /a BN=6
set /a PN=4

:: BMCConfig VSIL Reg
sqlcmd -S 10.11.218.3 -d FireBolt_BMCConfigDB_VSIL_Regional -i P:\DB\Sql\CreateBatteryConfig.sql

:: FaultsDB VSIL Reg
sqlcmd -S 10.11.218.3 -d FireBolt_FaultsDB_VSIL_Regional -i P:\DB\Sql\CreateFaultsDBTables.sql

:: Report VSIL Reg
sqlcmd -S 10.11.218.3 -d FireBolt_ReportingDB_VSIL_Regional -i P:\DB\Sql\CreateReportsTables.sql

:: PolicyDB VSIL Reg
sqlcmd -S 10.11.218.3 -d FireBolt_PolicyDB_VSIL_Regional -i P:\DB\Sql\PolicyDBSetup.sql




