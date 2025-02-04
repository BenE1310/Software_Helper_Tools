@cd /d "%~dp0"
@echo off
set /a BN=1
set USER=mPrest
set PASS=MprIt12#4%

sqlcmd -S "." -d FireBolt_BMCConfigDB_Operational_%BN% -U %USER% -P %PASS% -i C:\DB\Sql\adding_launcher_operational_mode.sql
