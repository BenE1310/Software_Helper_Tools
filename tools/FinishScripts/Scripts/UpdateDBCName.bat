@echo off
setlocal enabledelayedexpansion
IF Not EXIST "C:\Program Files\Microsoft SQL Server" echo MSSQL is not present in this computer&& exit
set UpdateDB="C:\Windows\Temp\UpdateDB.sql"
del %UpdateDB%

FOR /F "tokens=* USEBACKQ" %%F IN (`sqlcmd.exe -W -h-1 -Q "SET NOCOUNT ON; SELECT @@SERVERNAME AS 'Server Name'"`) DO (
SET OLD_DBCNAME=%%F
)
echo Current configured computer name: %OLD_DBCNAME%

FOR /F "usebackq tokens=2,* skip=2" %%L IN (
    `reg query "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName" /v ComputerName`
) DO SET NEW_CNAME=%%M

echo New configured computer name: %NEW_CNAME%

>> %UpdateDB% echo Use Master
>> %UpdateDB% echo GO
>> %UpdateDB% echo sp_dropserver %OLD_DBCNAME%;
>> %UpdateDB% echo GO
>> %UpdateDB% echo sp_addserver %NEW_CNAME%, local;
>> %UpdateDB% echo GO

sqlcmd -i %UpdateDB%
net stop MSSQLSERVER
net start MSSQLSERVER

FOR /F "tokens=* USEBACKQ" %%A IN (`sqlcmd.exe -W -h-1 -Q "SET NOCOUNT ON; SELECT @@SERVERNAME AS 'Server Name'"`) DO (
SET NEW_DBCNAME=%%A
)
echo New configured computer name: %NEW_DBCNAME%