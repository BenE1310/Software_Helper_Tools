@cd /d "%~dp0"
powershell.exe "Start-Process powershell -verb runas "-file InstallICS2Remotely.bat"
