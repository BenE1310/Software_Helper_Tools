@echo off
@cd /d "%~dp0"
set /p BN=Please Type the battery number:
set /a PN=13

echo D | xcopy Installation_Scripts\BMC\ICS.bat \\10.12.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I

echo D | xcopy C:\FBE\Zip\ICS.7z \\10.12.%BN%8.%PN%\c$\FBE\Zip /E /Y /I

echo D | xcopy C:\FBE\Tools \\10.12.%BN%8.%PN%\c$\FBE\Tools /E /Y /I

cmd /c \\10.12.%BN%8.%PN%\c$\FBE\Scripts\BMC\ICS.bat


