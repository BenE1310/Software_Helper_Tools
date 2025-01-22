@echo off
rem Version 1.0.0.2
@setlocal enableextensions
@cd /d "%~dp0"
:Check_Permissions
set /a BN=3
set /a PN=141
net session >nul 2>&1
   if %errorLevel% == 0 (
echo Success: Administrative permissions confirmed.
goto logo
) else (
echo Error: Logged in as: %userdomain%\%username%
echo        Please Login with Administrative permissions And
echo        Right Click the file ¯ Run as administrator
echo.
    ) 
pause
exit
:logo
cls
title Firebolt Server Version Update 
echo.  
echo	8888888888 d8b                 888               888 888    
echo	888        Y8P                 888               888 888    
echo	888                            888               888 888    
echo	8888888    888 888d888 .d88b.  88888b.   .d88b.  888 888888 
echo	888        888 888P"  d8P  Y8b 888 "88b d88""88b 888 888    
echo	888        888 888    88888888 888  888 888  888 888 888    
echo	888        888 888    Y8b.     888 d88P Y88..88P 888 Y88b.  
echo	888        888 888     "Y8888  88888P"   "Y88P"  888  "Y888
echo.

set hour=%time: =0%
set mydate=_"%Date:~7,2%.%Date:~4,2%.%Date:~12,4%-%hour:~0,2%%Time:~3,2%%Time:~6,2%"
set SourcePath="%~dp0..\..\Firebolt"
set DestPath="\\10.11.%BN%8.%PN%\c$\Firebolt"

IF not exist "%~dp0..\..\Zip\BatteryServer.7z" (goto NoSource)

echo ----------------------------------------------------------
echo Installation Path: %DestPath%
echo ----------------------------------------------------------

@echo Kill Processes...
sc \\10.11.%BN%8.%PN% stop "FBE Watchdog"
timeout /t 10
"%~dp0..\..\Tools"\"PsService.exe" -accepteula Stop "FBE Watchdog"
"%~dp0..\..\Tools"\"PsKill.exe" -accepteula -t FBEIronDomeBmcOperationalServer.exe
"%~dp0..\..\Tools"\"PsKill.exe" -accepteula -t FBEPlaybackServer.exe
"%~dp0..\..\Tools"\"PsKill.exe" -accepteula -t FBEBmcTrainingServer.exe
"%~dp0..\..\Tools"\"PsKill.exe" -accepteula -t SafetiesService.exe
"%~dp0..\..\Tools"\"PsKill.exe" -accepteula -t FBETrainerServer.exe

for /F "tokens=3,6 delims=: " %%I IN ('"%~dp0..\..\Tools"\"handle.exe" -accepteula C:\Firebolt') DO "%~dp0..\..\Tools"\"handle.exe" -c %%J -y -p %%I

FOR /L %%A IN (1,1,500) DO (
if not exist %DestPath%  ( goto BMC_Server
   ) else IF EXIST %DestPath%  ( Ren %DestPath% Firebolt%mydate% 
	if errorlevel 1 goto Error
   goto BMC_Server
  goto EOF  ) )


:BMC_Server
("%~dp0..\..\Tools\7z.exe" x "%~dp0..\..\Zip\BatteryServer.7z" -o"%DestPath%" -y) 
IF exist %DestPath% ( echo Firebolt Source Folder Found ) ELSE (goto NoSource)

echo Installing FBE Server, Please Wait...
echo.
echo.
echo Copying Safeties Transport Catalog, Please Wait...
robocopy /w:3 /r:3 /NJH /NP /NDL /NFL %DestPath%%mydate%\Watchdog\Safeties\SafetiesService\ %DestPath%\Watchdog\Safeties\SafetiesService\ ServiceTransportCatalog.xml
robocopy /w:3 /r:3 /NJH /NP /NDL /NFL %DestPath%%mydate%\Watchdog\WDService\Battery\ %DestPath%\Watchdog\WDService\Battery\ ServiceTransportCatalog.xml

echo.
rem robocopy /e /w:3 /r:3 %DestPath%%mydate%\Maps %DestPath%\Maps
echo Moving mDRSStorage to the new version, Please Wait...
robocopy /e /move /w:3 /r:3 /NJH /ETA /NP /NDL /NFL %DestPath%%mydate%\BMC\Battery\Operational\Server\mDRSStorage %DestPath%\BMC\Battery\Operational\Server\mDRSStorage
echo.
goto Maps

:Maps
IF not exist C:\Maps ("%~dp0..\..\Tools\7z.exe" x "%~dp0..\..\Zip\Maps.7z" -o"C:\" -y) 
goto Run_WD

:Run_WD
echo Trying to start FBE Watchdog Service
sc \\10.11.%BN%8.%PN% start "FBE Watchdog"
goto EOF

:Error
echo.
echo.
echo Error! Failed to update BatteryServer folder.
echo        Make sure you are not running any process
echo.
goto eof

:NoSource
echo.
echo [%~dp0..\..\Zip\BatteryServer.7z] Not Exist
echo [%~dp0..\..\Zip\BatteryServer.7z] Not Exist
echo Error! Source Files Not Found
echo.

:EOF
pause
exit