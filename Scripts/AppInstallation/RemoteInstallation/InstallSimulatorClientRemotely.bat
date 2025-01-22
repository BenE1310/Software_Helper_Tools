@echo off
@cd /d "%~dp0"
set /p BN=Please type the battery number:
set /p PN="Now, please type the position number. For E.g. : Position number 1 = 10.11.%BN%8.6 = Type '6': "

echo D | xcopy Installation_Scripts\Simulator\SimulatorClient.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\Simulator /E /Y /I

echo D | xcopy C:\FBE\Zip\SimulatorClient.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I

echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I

cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\Simulator\SimulatorClient.bat


