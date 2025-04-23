@echo off
rem Version 1.0.1.0 By Ben Eytan 23042025
@setlocal enableextensions
@cd /d "%~dp0"

set /a BN=3
set /a PN=141

:Check_Permissions
echo Administrative permissions required. Detecting permissions...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Success: Administrative permissions confirmed.
    goto logo
) else (
    echo Error: Logged in as: %userdomain%\%username%
    echo        Please Login with Administrative permissions And
    echo        Right Click the file ¯ Run as administrator
    pause
    exit
)

:logo
cls
title Firebolt ICS Version Update 
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

:: Generate a sanitized timestamp
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value ^| find "="') do set datetime=%%i
set mydate=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%-%datetime:~12,2%

:: Variables
set RemoteComputer=\\10.12.%BN%8.%PN%
set RemoteShare=C$
set TargetFolder=Firebolt
set NewFolderName=Firebolt_%mydate%
set DestPath="\\10.12.%BN%8.%PN%\c$\Firebolt"
echo %RemoteComputer%

:: Map Remote Share
echo Mapping %RemoteComputer%\%RemoteShare% to T:...
NET USE T: %RemoteComputer%\%RemoteShare% >nul 2>&1
if errorlevel 1 (
    echo Failed to map the network drive. Ensure network connectivity.
    pause
    exit /b 1
)


:: Continue with BatteryClient Logic
echo ----------------------------------------------------------
echo Installation Path: %DestPath%
echo ----------------------------------------------------------

@echo Kill Processes...
:: psservice \\10.12.%BN%8.%PN% stop "FBE Watchdog"
pskill \\FB-%BN%8-%PN% mPrest.IronDome.Watchdog.Service.Battery.Host.exe
pskill \\FB-%BN%8-%PN% IcsMainAppWithSafeties.exe
pskill \\FB-%BN%8-%PN% IcsMainAppWithoutSafeties.exe


timeout /t 3

for /F "tokens=3,6 delims=: " %%I IN ('"%~dp0..\..\Tools"\"handle.exe" -accepteula C:\Firebolt') DO "%~dp0..\..\Tools"\"handle.exe" -c %%J -y -p %%I

:: Check and Rename Folder
if exist "T:\%TargetFolder%" (
    echo Folder %TargetFolder% exists. Renaming to %NewFolderName%...
    REN "T:\%TargetFolder%" "%NewFolderName%"
    if errorlevel 1 (
        echo Failed to rename the folder. Check permissions and path.
        NET USE T: /DELETE >nul 2>&1
        pause
        exit /b 1
    )
    echo Folder renamed successfully to %NewFolderName%.
) else (
    echo Folder %TargetFolder% does not exist. Continuing...
)

:: Disconnect Mapped Drive
NET USE T: /DELETE >nul 2>&1

:ICS
("%~dp0..\..\Tools\7z.exe" x "%~dp0..\..\Zip\ICS.7z" -o"%DestPath%" -y) 
IF exist %DestPath% ( echo Firebolt Source Folder Found ) ELSE (goto NoSource)

echo Installing FBE ICS, Please Wait...
echo.
echo.
rem robocopy /e /w:3 /r:3 %DestPath%%mydate%\Maps %DestPath%\Maps
robocopy /e /w:3 /r:3 /NJH /ETA /NP /NDL /NFL %NewFolderName%\BMC\Battery\Operational\ICS %DestPath%\BMC\Battery\Operational\ICS AddressBook.ini
robocopy /e /w:3 /r:3 /NJH /ETA /NP /NDL /NFL %NewFolderName%\BMC\Battery\Operational\ICS %DestPath%\BMC\Battery\Operational\ICS IcsParams.ini

robocopy /e /w:3 /r:3 /NJH /ETA /NP /NDL /NFL %NewFolderName%\BMC\Battery\Training\ICS %DestPath%\BMC\Battery\Training\ICS AddressBook.ini
robocopy /e /w:3 /r:3 /NJH /ETA /NP /NDL /NFL %NewFolderName%\BMC\Battery\Training\ICS %DestPath%\BMC\Battery\Training\ICS IcsParams.ini

echo Moving mDRSStorage to the new version, Please Wait...
robocopy /e /move /w:3 /r:3 /NJH /ETA /NP /NDL /NFL %NewFolderName%\Watchdog\mDRSAgent\mDRSStorage %DestPath%\Watchdog\mDRSAgent\mDRSStorage
echo.
goto Maps

:Maps
IF not exist C:\Maps ("%~dp0..\..\Tools\7z.exe" x "%~dp0..\..\Zip\Maps.7z" -o"C:\" -y) 
goto Run_WD

:Run_WD
echo Trying to start FBE Watchdog Service
psservice \\FB-%BN%8-%PN% start "FBE Watchdog"
goto EOF

:EOF
exit