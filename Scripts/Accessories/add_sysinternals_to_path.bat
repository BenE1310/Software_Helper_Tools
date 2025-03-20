@echo off
setlocal

:: Get the current script directory
set "CURRENT_DIR=%~dp0"

:: Remove trailing backslash if it exists
if "%CURRENT_DIR:~-1%"=="\" set "CURRENT_DIR=%CURRENT_DIR:~0,-1%"

:: Check if there are Sysinternals tools in the folder
set "EXE_COUNT=0"
for %%F in ("%CURRENT_DIR%\*.exe") do set /A EXE_COUNT+=1

if %EXE_COUNT%==0 (
    echo No executable files found in the current directory.
    pause
    exit /b
)

:: Add current folder to system PATH permanently
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path /t REG_EXPAND_SZ /d "%CURRENT_DIR%;%PATH%" /f

:: Confirm addition
echo Sysinternals tools directory added to PATH: %CURRENT_DIR%
echo Now you can use the following Sysinternals tools from any command prompt:
for %%F in ("%CURRENT_DIR%\*.exe") do echo - %%~nF

echo Restart your command prompt or system for changes to take effect.
endlocal
pause