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

set hour=%time: =0%
set mydate=_"%Date:~7,2%.%Date:~4,2%.%Date:~12,4%-%hour:~0,2%%Time:~3,2%%Time:~6,2%"

set DestPath="\\10.11.%BN%8.%PN%\c$\mDRS"

IF not exist "%~dp0..\..\Zip\mDRS.7z" (goto NoSource)

echo ----------------------------------------------------------
echo Installation Path: %DestPath%
echo ----------------------------------------------------------

@echo Kill Processes...
sc \\10.11.%BN%8.%PN% stop "mDRS Agent Service"
sc \\10.11.%BN%8.%PN% stop "mDRS Server Service"
timeout /t 10

FOR /L %%A IN (1,1,500) DO (
if not exist %DestPath%  ( goto mDRS
   ) else IF EXIST %DestPath%  ( Ren %DestPath% mDRS%mydate% 
	if errorlevel 1 goto Error
   goto mDRS
  goto EOF  ) )
goto mDRS

:mDRS
echo Installing FBE mDRS, Please Wait...
("%~dp0..\..\Tools\7z.exe" x "%~dp0..\..\Zip\mDRS.7z" -o"%DestPath%" -y) 
IF exist %DestPath% ( echo Firebolt Source Folder Found ) ELSE (goto NoSource)

goto EOF


:Error
echo.
echo.
echo Error! Failed to update DB folder.
echo        Make sure you are not running any process
echo.
goto eof

:NoSource
echo.
echo [%~dp0..\..\Zip\DB.7z] Not Exist
echo [%~dp0..\..\Zip\DB.7z] Not Exist
echo Error! Source Files Not Found
echo.

:EOF
pause
exit