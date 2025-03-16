@cd /d "%~dp0"
@echo off
set /a BN=2
set /a PN=4

sqlcmd -S 10.11.%BN%8.%PN% -d FireBolt_BMCConfigDB_Operational_%BN%  -i P:\DB\Sql\adding_launcher_operational_mode.sql
