@echo off
cls
if /i %Batt% EQU 8 (set CBMCnum=1&& set domainname=Fireboltcbmc)
if /i %Batt% EQU 9 (set CBMCnum=2&& set domainname=Fireboltcbmc2)
PowerShell.Exe Set-ExecutionPolicy unrestricted -force
PowerShell.Exe Add-Computer %domainname%.Local -Cred %domainname%\fbtech
GPUpdate /Force
Choice /C YN /M "Restart Now?" 
GOTO crestart_%ERRORLEVEL%
:crestart_1
shutdown.exe /r /t 00
:crestart_2