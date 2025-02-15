@echo off
cls
PowerShell.Exe Set-ExecutionPolicy unrestricted -force
PowerShell.Exe Add-Computer FireBolt%Batt%.Local -Cred FireBolt%Batt%\fbtech
GPUpdate /Force
Choice /C YN /M "Restart Now?" 
GOTO crestart_%ERRORLEVEL%
:crestart_1
shutdown.exe /r /t 00
:crestart_2