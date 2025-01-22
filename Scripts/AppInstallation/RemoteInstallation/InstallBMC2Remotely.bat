@echo off
@cd /d "%~dp0"
set /p BN=Please Type the battery number:
set /a PN=2

echo D | xcopy Installation_Scripts\BMC\BatteryServer.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I

echo D | xcopy C:\FBE\Zip\BatteryServer.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I

echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I

cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryServer.bat

