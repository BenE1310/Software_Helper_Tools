@echo off
@cd /d "%~dp0"
set /a BN=21
set LogFile=RegionalInstallation.log

rem Banner
echo.
echo  #######                         ######                   ###                                          
echo  #       #    # #      #         #     # ######  ####      #  #    #  ####  #####   ##   #      #      
echo  #       #    # #      #         #     # #      #    #     #  ##   # #        #    #  #  #      #      
echo  #####   #    # #      #         ######  #####  #          #  # #  #  ####    #   #    # #      #      
echo  #       #    # #      #         #   #   #      #  ###     #  #  # #      #   #   ###### #      #      
echo  #       #    # #      #         #    #  #      #    #     #  #   ## #    #   #   #    # #      #      
echo  #        ####  ###### ######    #     # ######  ####     ### #    #  ####    #   #    # ###### ###### 
echo.                                                                                                       
echo.
echo ----------------------------------------------------------
echo 		Start installation Regional
echo ----------------------------------------------------------
echo Start installation Regional >> %LogFile%


:: Install CBMC1
set /a PN=1
set CBMC1= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to CBMC1 >> %LogFile%
ping -n 2 %CBMC1% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryServer on CBMC1. >> %LogFile%
    echo D | xcopy Installation_Scripts\BMC\BatteryServer.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryServer.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryServer.bat
	echo %date% %time% - INFO Installation completed successfully on CBMC1 >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to CBMC1. >> %LogFile%
)


:: Install CBMC2
set /a PN=2
set CBMC2= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to CBMC2 >> %LogFile%
ping -n 2 %CBMC2% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryServer on CBMC2. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\BatteryServer.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryServer.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryServer.bat
	echo %date% %time% - INFO Installation completed successfully on CBMC2 >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to CBMC2. >> %LogFile%
)


:: Install CBMC-DB1
set /a PN=3
set CBMC-DB1= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to CBMC-DB1 >> %LogFile%
ping -n 2 %CBMC-DB1% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install mDRS on CBMC-DB1. >> %LogFile%
	echo D | xcopy Installation_Scripts\DB\mDRS.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\DB /E /Y /I
	echo D | xcopy C:\FBE\Zip\mDRS.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\DB\mDRS.bat
	echo %date% %time% - INFO Installation completed successfully on CBMC-DB1 >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to CBMC-DB1. >> %LogFile%
)


:: Install CBMC-DB2
set /a PN=4
set CBMC-DB2= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to CBMC-DB2 >> %LogFile%
ping -n 2 %CBMC-DB2% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install mDRS on CBMC-DB2. >> %LogFile%
	echo D | xcopy Installation_Scripts\DB\mDRS.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\DB /E /Y /I
	echo D | xcopy C:\FBE\Zip\mDRS.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\DB\mDRS.bat
	echo %date% %time% - INFO Installation completed successfully on CBMC-DB2 >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to CBMC-DB2. >> %LogFile%
)



:: Install Clients

:: Client1
set /a PN=51
set Client1= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client1 >> %LogFile%
ping -n 2 %Client1% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryClient on Client1. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\BatteryClient.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryClient.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryClient.bat
	echo %date% %time% - INFO Installation completed successfully on Client1 >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to Client1. >> %LogFile%
)


:: Client2
set /a PN=52
set Client2= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client2 >> %LogFile%
ping -n 2 %Client2% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryClient on Client2. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\BatteryClient.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryClient.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryClient.bat
	echo %date% %time% - INFO Installation completed successfully on Client2. >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to Client2. >> %LogFile%
)

:: Client3
set /a PN=53
set Client3= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client3 >> %LogFile%
ping -n 2 %Client3% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryClient on Client3. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\BatteryClient.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryClient.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryClient.bat
	echo %date% %time% - INFO Installation completed successfully on Client3. >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to Client3. >> %LogFile%
)


:: Client4
set /a PN=54
set Client4= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client4 >> %LogFile%
ping -n 2 %Client4% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryClient on Client4. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\BatteryClient.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryClient.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryClient.bat
	echo %date% %time% - INFO Installation completed successfully on Client4. >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to Client4. >> %LogFile%
)


:: Client5
set /a PN=55
set Client5= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client5 >> %LogFile%
ping -n 2 %Client5% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryClient on Client5. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\BatteryClient.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryClient.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryClient.bat
	echo %date% %time% - INFO Installation completed successfully on Client5. >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to Client5. >> %LogFile%
)

:: Client6
set /a PN=56
set Client6= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client6 >> %LogFile%
ping -n 2 %Client6% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryClient on Client6. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\BatteryClient.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryClient.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryClient.bat
	echo %date% %time% - INFO Installation completed successfully on Client6. >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to Client6. >> %LogFile%
)

:: Client7
set /a PN=57
set Client7= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client7 >> %LogFile%
ping -n 2 %Client7% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryClient on Client7. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\BatteryClient.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryClient.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryClient.bat
	echo %date% %time% - INFO Installation completed successfully on Client7. >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to Client7. >> %LogFile%
)

:: Client8
set /a PN=57
set Client8= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client8 >> %LogFile%
ping -n 2 %Client8% >nul

if %errorlevel% equ 0 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryClient on Client8. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\BatteryClient.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryClient.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryClient.bat
	echo %date% %time% - INFO Installation completed successfully on Client8. >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to Client8. >> %LogFile%
)

echo Regional installation is complete. >> %LogFile%

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