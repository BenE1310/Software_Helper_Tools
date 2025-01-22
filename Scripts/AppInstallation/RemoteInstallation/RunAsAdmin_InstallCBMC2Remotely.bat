@cd /d "%~dp0"
powershell.exe "Start-Process powershell -verb runas "-file InstallCBMC2Remotely.bat"
