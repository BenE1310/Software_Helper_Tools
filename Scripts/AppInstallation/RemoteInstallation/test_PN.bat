
@echo off
@cd /d "%~dp0"
set /p BN="Please Type the battery number: "
set LogFile=Battery%BN%Installation.log

set /a PN=100
set Client1= 10.0.%BN%.%PN%
echo %date% %time% - INFO Check connection to Client1 >> %LogFile%
ping -n 2 %Client1% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryClient on Client1. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\Ben.bat \\10.0.%BN%.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryClient.7z \\10.0.%BN%.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.0.%BN%.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.0.%BN%.%PN%\c$\FBE\Scripts\BMC\Ben.bat
	echo %date% %time% - INFO Installation completed successfully on Client1 >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to Client1. >> %LogFile%
)




set /a PN=101
set Client1= 10.0.%BN%.%PN%
echo %date% %time% - INFO Check connection to Client1 >> %LogFile%
ping -n 2 %Client1% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryClient on Client1. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\Ben.bat \\10.0.%BN%.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryClient.7z \\10.0.%BN%.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.0.%BN%.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.0.%BN%.%PN%\c$\FBE\Scripts\BMC\Ben.bat
	echo %date% %time% - INFO Installation completed successfully on Client1 >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to Client1. >> %LogFile%
)


set LogFolder=Logs
@cd /d "%~dp0\..\..\.."
if not exist %LogFolder% (
	mkdir %LogFolder%
	echo Folder "%LogFolder%" created successfully.)
) else (
    echo Folder "%LogFolder%" already exists.
)
cd Logs
echo %~dp0%LogFile%
echo y | xcopy %~dp0%LogFile% %cd% 
pause