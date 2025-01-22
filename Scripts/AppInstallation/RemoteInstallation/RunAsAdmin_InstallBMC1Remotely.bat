@cd /d "%~dp0"
powershell.exe "Start-Process powershell -verb runas "-file InstallBMC1Remotely.bat"
