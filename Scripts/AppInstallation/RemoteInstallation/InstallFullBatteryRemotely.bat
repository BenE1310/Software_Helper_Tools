@echo off
@cd /d "%~dp0"

rem Banner
echo.
echo  #######                         ######                        ###                                          
echo  #       #    # #      #         #     #   ##   ##### #####     #  #    #  ####  #####   ##   #      #      
echo  #       #    # #      #         #     #  #  #    #     #       #  ##   # #        #    #  #  #      #      
echo  #####   #    # #      #         ######  #    #   #     #       #  # #  #  ####    #   #    # #      #      
echo  #       #    # #      #         #     # ######   #     #       #  #  # #      #   #   ###### #      #      
echo  #       #    # #      #         #     # #    #   #     #       #  #   ## #    #   #   #    # #      #      
echo  #        ####  ###### ######    ######  #    #   #     #      ### #    #  ####    #   #    # ###### ###### 
echo.
echo.                                                                                                            

set /p BN="Please Type the battery number: "
set LogFile=Battery%BN%Installation.log
echo.
echo ----------------------------------------------------------
echo 		Start installation Battery%BN%
echo ----------------------------------------------------------
echo Start installation Battery%BN% >> %LogFile%

:: Install BMC1
set /a PN=1
set BMC1= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to BMC1 >> %LogFile%
ping -n 1 %BMC1% > ping_result.txt
set errorFound=0

findstr /C:"Request timed out." ping_result.txt > nul
if %ERRORLEVEL%==0 (
    echo %date% %time% - ERROR Connection failed - no connection to BMC1 - "Request timed out". >> %LogFile%
    set errorFound=1
)

findstr /C:"Destination host unreachable." ping_result.txt > nul
if %ERRORLEVEL%==0 (
    echo %date% %time% - ERROR Connection failed - no connection to BMC1 - "Destination host unreachable". >> %LogFile%
    set errorFound=1
)

if %errorFound%==0 (
    echo %date% %time% - INFO Connection successful - Start to install BatteryServer on BMC1. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\BatteryServer.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryServer.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I	
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I	
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryServer.bat	
	echo %date% %time% - INFO Installation completed successfully on BMC1 >> %LogFile%		
)

del ping_result.txt


:: Install BMC2
set /a PN=2
set BMC2= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to BMC2 >> %LogFile%
ping -n 1 %BMC2% > ping_result.txt
set errorFound=0

findstr /C:"Request timed out." ping_result.txt > nul
if %ERRORLEVEL%==0 (
    echo %date% %time% - ERROR Connection failed - no connection to BMC2 - "Request timed out". >> %LogFile%
    set errorFound=1
)

findstr /C:"Destination host unreachable." ping_result.txt > nul
if %ERRORLEVEL%==0 (
    echo %date% %time% - ERROR Connection failed - no connection to BMC2 - "Destination host unreachable". >> %LogFile%
    set errorFound=1
)

if %errorFound%==0 (
    echo %date% %time% - INFO Connection successful - Start to install BatteryServer on BMC2. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\BatteryServer.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryServer.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I	
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I	
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryServer.bat	
	echo %date% %time% - INFO Installation completed successfully on BMC2 >> %LogFile%		
)

del ping_result.txt

:: Install DB1
set /a PN=3
set DB1= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to DB1 >> %LogFile%
ping -n 1 %DB1% | findstr /c:"Destination host unreachable" >nul

if errorlevel 1 (
	echo %date% %time% - INFO Connection successful - Start to install mDRS on DB1. >> %LogFile%
	echo D | xcopy Installation_Scripts\DB\mDRS.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\DB /E /Y /I
	echo D | xcopy C:\FBE\Zip\mDRS.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\DB\mDRS.bat
	echo %date% %time% - INFO Installation completed successfully on DB1 >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to DB1. >> %LogFile%
)


:: Install DB2
set /a PN=4
set DB2= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to DB2 >> %LogFile%
ping -n 1 %DB2% | findstr /c:"Destination host unreachable" >nul

if errorlevel 1 (
	echo %date% %time% - INFO Connection successful - Start to install mDRS on DB2. >> %LogFile%
	echo D | xcopy Installation_Scripts\DB\mDRS.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\DB /E /Y /I
	echo D | xcopy C:\FBE\Zip\mDRS.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\DB\mDRS.bat
	echo %date% %time% - INFO Installation completed successfully on DB2 >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to DB2. >> %LogFile%
)

:: Install ICS1
set /a PN=13
set ICS1= 10.12.%BN%8.%PN%
echo %date% %time% - INFO Check connection to ICS1 >> %LogFile%
ping -n 1 %ICS1% | findstr /c:"Destination host unreachable" >nul

if errorlevel 1 (
	echo %date% %time% - INFO Connection successful - Start to install ICS on ICS1. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\ICS.bat \\10.12.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\ICS.7z \\10.12.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.12.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.12.%BN%8.%PN%\c$\FBE\Scripts\BMC\ICS.bat
	echo %date% %time% - INFO Installation completed successfully on ICS1 >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to ICS1. >> %LogFile%
)

 
:: Install ICS2
set /a PN=14
set ICS2= 10.12.%BN%8.%PN%
echo %date% %time% - INFO Check connection to ICS2 >> %LogFile%
ping -n 1 %ICS2% | findstr /c:"Destination host unreachable" >nul

if errorlevel 1 (
	echo %date% %time% - INFO Connection successful - Start to install ICS on ICS2. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\ICS.bat \\10.12.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\ICS.7z \\10.12.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.12.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.12.%BN%8.%PN%\c$\FBE\Scripts\BMC\ICS.bat
	echo %date% %time% - INFO Installation completed successfully on ICS2 >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to ICS2. >> %LogFile%
)



:: Install Clients

:: Client1
set /a PN=6
set Client1= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client1 >> %LogFile%
ping -n 1 %Client1% | findstr /c:"Destination host unreachable" >nul

if errorlevel 1 (
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
set /a PN=7
set Client2= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client2 >> %LogFile%
ping -n 1 %Client2% | findstr /c:"Destination host unreachable" >nul

if errorlevel 1 (
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
set /a PN=8
set Client3= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client3 >> %LogFile%
ping -n 1 %Client3% | findstr /c:"Destination host unreachable" >nul

if errorlevel 1 (
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
set /a PN=9
set Client4= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client4 >> %LogFile%
ping -n 1 %Client4% | findstr /c:"Destination host unreachable" >nul

if errorlevel 1 (
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
set /a PN=10
set Client5= 10.11.%BN%8.%PN%
echo %date% %time% - INFO Check connection to Client5 >> %LogFile%
ping -n 1 %Client5% | findstr /c:"Destination host unreachable" >nul

if errorlevel 1 (
	echo %date% %time% - INFO Connection successful - Start to install BatteryClient on Client5. >> %LogFile%
	echo D | xcopy Installation_Scripts\BMC\BatteryClient.bat \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC /E /Y /I
	echo D | xcopy C:\FBE\Zip\BatteryClient.7z \\10.11.%BN%8.%PN%\c$\FBE\Zip /E /Y /I
	echo D | xcopy C:\FBE\Tools \\10.11.%BN%8.%PN%\c$\FBE\Tools /E /Y /I
	cmd /c \\10.11.%BN%8.%PN%\c$\FBE\Scripts\BMC\BatteryClient.bat
	echo %date% %time% - INFO Installation completed successfully on Client5. >> %LogFile%
) else (
    echo %date% %time% - ERROR Connection failed - no connection to Client5. >> %LogFile%
)


echo Battrey%BN% installation is complete. >> %LogFile%

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