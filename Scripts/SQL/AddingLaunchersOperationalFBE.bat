@cd /d "%~dp0"
@echo off
set /a BN=0


sqlcmd -S 10.11.%BN%8.3 -d FireBolt_BMCConfigDB_Operational_%BN%  -i P:\DB\Sql\adding_launcher_operational_mode.sql
