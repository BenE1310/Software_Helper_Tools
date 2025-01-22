@echo off
setlocal

REM Set the target IP or hostname
set TARGET=10.11.18.1

REM Ping the target with a single echo request and store the output in a temporary file
ping -n 1 %TARGET% > ping_result.txt

REM Initialize a variable to track if an error is found
set errorFound=0

REM Search for "Request timed out."
findstr /C:"Request timed out." ping_result.txt > nul
if %ERRORLEVEL%==0 (
    echo Ping to %TARGET% failed: Request timed out.
    set errorFound=1
)

REM Search for "Destination host unreachable."
findstr /C:"Destination host unreachable." ping_result.txt > nul
if %ERRORLEVEL%==0 (
    echo Ping to %TARGET% failed: Destination host unreachable.
    set errorFound=1
)

REM If no error messages were found, the ping was successful
if %errorFound%==0 (
    echo Ping to %TARGET% successful.
)

REM Clean up
rem del ping_result.txt
endlocal
pause
