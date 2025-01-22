@echo off
@cd /d "%~dp0"
set /p PN="Now, please type the position number. For E.g. : Position number 1 = 10.11.218.51 = Type '51': "

echo D | xcopy Installation_Scripts\CBMC\RegionalClient.bat \\10.11.218.%PN%\c$\FBE\Scripts\CBMC /E /Y /I

echo D | xcopy C:\FBE\\Zip\RegionalClient.7z \\10.11.218.%PN%\c$\FBE\Zip /E /Y /I

echo D | xcopy C:\FBE\Tools \\10.11.218.%PN%\c$\FBE\Tools /E /Y /I

cmd /c \\10.11.218.5%PN%\c$\FBE\Scripts\CBMC\RegionalClient.bat


