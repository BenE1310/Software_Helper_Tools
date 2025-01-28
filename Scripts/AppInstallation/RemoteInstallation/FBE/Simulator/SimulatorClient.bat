@echo off
rem Version 1.0.0.5 By Ben Eytan 28012025
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
title Firebolt Simulator Client Version Update 
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
set RemoteComputer=\\10.11.%BN%8.%PN%
set RemoteShare=C$
set TargetFolder=Firebolt
set NewFolderName=Firebolt_%mydate%
set DestPath="\\10.11.%BN%8.%PN%\c$\Firebolt"
echo %RemoteComputer%

:: Map Remote Share
echo Mapping %RemoteComputer%\%RemoteShare% to T:...
NET USE T: %RemoteComputer%\%RemoteShare% >nul 2>&1
if errorlevel 1 (
    echo Failed to map the network drive. Ensure network connectivity.
    pause
    exit /b 1
)

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

:: Continue with SimulatorClient Logic
echo ----------------------------------------------------------
echo Installation Path: %DestPath%
echo ----------------------------------------------------------

@echo Kill Processes...
"%~dp0..\..\Tools"\"PsKill.exe" -accepteula -t FBEIronDomeSimClient.exe

for /F "tokens=3,6 delims=: " %%I IN ('"%~dp0..\..\Tools"\"handle.exe" -accepteula C:\Firebolt') DO "%~dp0..\..\Tools"\"handle.exe" -c %%J -y -p %%I
goto Simulator_Client

:Simulator_Client
echo Installing Simulator Client, Please Wait...
("%~dp0..\..\Tools\7z.exe" x "%~dp0..\..\Zip\SimulatorClient.7z" -o"%DestPath%" -y) 
IF exist %DestPath% ( echo Firebolt Source Folder Found ) ELSE (goto NoSource)

goto Maps

:Maps
IF not exist C:\Maps ("%~dp0..\..\Tools\7z.exe" x "%~dp0..\..\Zip\Maps.7z" -o"C:\" -y) 
goto EOF

:Error
echo.
echo.
echo Error! Failed to update SimulatorClient folder.
echo        Make sure you are not running any process
echo.
goto eof
:NoSource
echo.
echo [%~dp0..\..\Zip\SimulatorClient.7z] Not Exist
echo Error! Source Files Not Found
echo.
:EOF
pause
exit