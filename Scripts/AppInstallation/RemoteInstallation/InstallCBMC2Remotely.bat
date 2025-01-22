@echo off
@cd /d "%~dp0"
set /a PN=2

echo D | xcopy Installation_Scripts\CBMC\RegionalServer.bat \\10.11.218.%PN%\c$\FBE\Scripts\CBMC /E /Y /I

echo D | xcopy C:\FBE\Zip\RegionalServer.7z \\10.11.218.%PN%\c$\FBE\Zip /E /Y /I

echo D | xcopy C:\FBE\Tools \\10.11.218.%PN%\c$\FBE\Tools /E /Y /I

cmd /c \\10.11.218.%PN%\c$\FBE\Scripts\CBMC\RegionalServer.bat

