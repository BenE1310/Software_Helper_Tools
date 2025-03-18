@cd /d "%~dp0"
@echo off
set /a BN=2
set /a PN=3

sqlcmd -S 10.11.18.3 -d FireBolt_BMCConfigDB_VSIL_%BN% -i P:\DB\Sql\adding_launcher_training_mode.sql

