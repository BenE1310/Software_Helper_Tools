@echo off
rem Version 1.0.1.0 By Ben Eytan 12022025
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
title VSIL AV_Server Version Update 
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
set RemoteComputer=\\10.11.%BN%3.%PN%
set RemoteShare=C$
set TargetFolder=VSIL
set NewFolderName=VSIL_%mydate%
set DestPath="\\10.11.%BN%3.%PN%\c$\VSIL"
echo %RemoteComputer%

:: Map Remote Share
echo Mapping %RemoteComputer%\%RemoteShare% to T:...
NET USE T: %RemoteComputer%\%RemoteShare% >nul 2>&1
if errorlevel 1 (
    echo Failed to map the network drive. Ensure network connectivity.
    pause
    exit /b 1
)


echo ----------------------------------------------------------
echo Installation Path: %DestPath%
echo ----------------------------------------------------------

@echo Kill Processes...
psservice \\10.11.%BN%3.%PN% stop "VSIL Watchdog"

timeout /t 10

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


for /F "tokens=3,6 delims=: " %%I IN ('"%~dp0..\..\Tools"\"handle.exe" -accepteula C:\VSIL') DO "%~dp0..\..\Tools"\"handle.exe" -c %%J -y -p %%I
goto AV_Server

:AV_Server
echo Installing AV_Server, Please Wait...
("%~dp0..\..\Tools\7z.exe" x "%~dp0..\..\Zip\WD_Common.7z" -o"%DestPath%" -y) 
IF exist %DestPath% ( echo VSIL Source Folder Found ) ELSE (goto NoSource)


echo Trying to start VSIL Watchdog Service
psservice \\10.11.%BN%3.%PN% start "VSIL Watchdog"
goto EOF

:EOF
exit