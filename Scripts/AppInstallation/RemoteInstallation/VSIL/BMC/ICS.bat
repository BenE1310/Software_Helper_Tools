@echo off
rem Version 1.0.0.2
@setlocal enableextensions
@cd /d "%~dp0"

:Check_Permissions
echo Administrative permissions required. Detecting permissions...
echo.
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
title VSIL ICS Version Update 
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
set SourcePath="%~dp0..\..\VSIL"
set DestPath="C:\VSIL"

IF not exist "%~dp0..\..\Zip\ICS.7z" (goto NoSource)

echo ----------------------------------------------------------
echo Installation Path: %DestPath%
echo ----------------------------------------------------------

@echo Kill Processes...
"%~dp0..\..\Tools"\"PsService.exe" -accepteula Stop "VSIL Watchdog"
"%~dp0..\..\Tools"\"PsKill.exe" -accepteula -t IcsMainAppWithoutSafeties.exe

for /F "tokens=3,6 delims=: " %%I IN ('"%~dp0..\..\Tools"\"handle.exe" -accepteula C:\VSIL') DO "%~dp0..\..\Tools"\"handle.exe" -c %%J -y -p %%I

FOR /L %%A IN (1,1,500) DO (
if not exist %DestPath%  ( goto ICS
   ) else IF EXIST %DestPath%  ( Ren %DestPath% VSIL%mydate% 
	if errorlevel 1 goto Error
   goto ICS
  goto EOF  ) )

:ICS
("%~dp0..\..\Tools\7z.exe" x "%~dp0..\..\Zip\ICS.7z" -o"%DestPath%" -y) 
IF exist %DestPath% ( echo VSIL Source Folder Found ) ELSE (goto NoSource)

echo Installing VSIL ICS, Please Wait...
echo.
echo.
rem robocopy /e /w:3 /r:3 %DestPath%%mydate%\Maps %DestPath%\Maps

robocopy /e /w:3 /r:3 /NJH /ETA /NP /NDL /NFL %DestPath%%mydate%\BMC\Battery\VSIL\ICS %DestPath%\BMC\Battery\VSIL\ICS AddressBook.ini
robocopy /e /w:3 /r:3 /NJH /ETA /NP /NDL /NFL %DestPath%%mydate%\BMC\Battery\VSIL\ICS %DestPath%\BMC\Battery\VSIL\ICS IcsParams.ini


echo Moving mDRSStorage to the new version, Please Wait...
robocopy /e /move /w:3 /r:3 /NJH /ETA /NP /NDL /NFL %DestPath%%mydate%\Watchdog\mDRSAgent\mDRSStorage %DestPath%\Watchdog\mDRSAgent\mDRSStorage
echo.
goto Maps

:Maps
IF not exist C:\Maps ("%~dp0..\..\Tools\7z.exe" x "%~dp0..\..\Zip\Maps.7z" -o"C:\" -y) 
goto Run_WD

:Run_WD
echo Trying to start VSIL Watchdog Service
"%~dp0..\..\Tools"\"PsService.exe" -accepteula Start "VSIL Watchdog"
goto EOF


:Error
echo.
echo.
echo Error! Failed to update ICS folder.
echo        Make sure you are not running any process
echo.
goto eof

:NoSource
echo.
echo [%~dp0..\..\Zip\ICS.7z] Not Exist
echo [%~dp0..\..\Zip\ICS.7z] Not Exist
echo Error! Source Files Not Found
echo.

:EOF
pause
exit