@cd /d "%~dp0"
powershell.exe "Start-Process powershell -verb runas "-file InstallCBMCLocally.bat"
