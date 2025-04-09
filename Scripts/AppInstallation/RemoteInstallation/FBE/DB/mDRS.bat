@echo off
rem Version 1.0.2.0 By Ben Eytan 09042025
@setlocal enableextensions
@cd /d "%~dp0"

set /a BN=0
set /a PN=0

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
title Firebolt mDRS in DB Version Update
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
set TargetFolder=mDRS
set NewFolderName=mDRS_%mydate%
set TargetFolder_DB=DB
set NewFolderName_DB=DB_%mydate%
set DestPath="\\10.11.%BN%8.%PN%\c$\mDRS"
set DestPath_DB="\\10.11.%BN%8.%PN%\c$\DB"

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
:: psservice \\10.11.%BN%8.%PN% stop "mDRS Agent Service"
:: psservice \\10.11.%BN%8.%PN% stop "mDRS Server Service"
pskill \\10.11.%BN%8.%PN% stop "mDRSAgent.exe"
pskill \\10.11.%BN%8.%PN% stop "mDRSServer.exe"

timeout /t 5

:: Check and Rename Folder mDRS
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

:: Check and Rename Folder DB
if exist "T:\%TargetFolder_DB%" (
    echo Folder %TargetFolder_DB% exists. Renaming to %NewFolderName_DB%...
    REN "T:\%TargetFolder_DB%" "%NewFolderName_DB%"
    if errorlevel 1 (
        echo Failed to rename the folder. Check permissions and path.
        NET USE T: /DELETE >nul 2>&1
        pause
        exit /b 1
    )
    echo Folder renamed successfully to %NewFolderName_DB%.
) else (
    echo Folder %TargetFolder_DB% does not exist. Continuing...
)

:: Disconnect Mapped Drive
NET USE T: /DELETE >nul 2>&1

:mDRS
echo Installing FBE mDRS, Please Wait...
("%~dp0..\..\Tools\7z.exe" x "%~dp0..\..\Zip\mDRS.7z" -o"%DestPath%" -y)
IF exist %DestPath% ( echo mDRS Source Folder Found ) ELSE (goto NoSource)
goto DB

:DB
echo Creating FBE DB folder, Please Wait...
("%~dp0..\..\Tools\7z.exe" x "%~dp0..\..\Zip\DB.7z" -o"%DestPath_DB%" -y)
IF exist %DestPath_DB% ( echo DB Source Folder Found ) ELSE (goto NoSource_DB)
goto EOF

:EOF
exit