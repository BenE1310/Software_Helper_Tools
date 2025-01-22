:: @echo off
set ScriptPath=%~dp0
echo The script is located at: %ScriptPath%

echo path test > Ben.txt

set LogFolder=Logs
@cd /d "%~dp0\..\..\.."
if not exist %LogFolder% (
	mkdir %LogFolder%
	echo Folder "%LogFolder%" created successfully.)
) else (
    echo Folder "%LogFolder%" already exists.
)
cd Logs
xcopy %~dp0Ben.txt %cd% /E /H /C /I
pause