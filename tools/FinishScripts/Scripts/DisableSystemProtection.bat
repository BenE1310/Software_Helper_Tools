@echo off
echo Disable System Protection
Reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore" /v DisableSR /t REG_DWORD /d 1 /f
PowerShell.exe -Command "& {Disable-ComputerRestore -Drive 'C:\';"}