@echo off
setlocal enabledelayedexpansion
set /a BN=1
set /a PN=3
echo Creating Databases For Regional Operational Mode
set CDBase="C:\Windows\Temp\CDBase.sql"
del %CDBase%
MD C:\FireBoltDB

for %%A in (
			FireBolt_BMCConfigDB_Operational
			FireBolt_FaultsDB_Operational
			FireBolt_PolicyDB_Operational
			FireBolt_ReportingDB_Operational
) do (
(
>> %CDBase% echo USE [master]
>> %CDBase% echo GO
>> %CDBase% echo CREATE DATABASE [%%A_Regional] ON  PRIMARY
>> %CDBase% echo ^( NAME = N'%%A_Regional', FILENAME = N'C:\FireBoltDB\%%A_Regional.mdf' , SIZE = 5048KB , MAXSIZE = UNLIMITED, FILEGROWTH = 1024KB ^)
>> %CDBase% echo  LOG ON
>> %CDBase% echo ^( NAME = N'%%A_Regional_log', FILENAME = N'C:\FireBoltDB\%%A_Regional_log.ldf' , SIZE = 5024KB , MAXSIZE = 2048GB , FILEGROWTH = 10%% ^)
>> %CDBase% echo GO
>> %CDBase% echo ALTER DATABASE [%%A_Regional] SET COMPATIBILITY_LEVEL = 100
>> %CDBase% echo GO
>> %CDBase% echo IF ^(1 = FULLTEXTSERVICEPROPERTY^('IsFullTextInstalled'^)^)
>> %CDBase% echo begin
>> %CDBase% echo EXEC [%%A_Regional].[dbo].[sp_fulltext_database] @action = 'enable'
>> %CDBase% echo end
>> %CDBase% echo GO
>> %CDBase% echo ALTER DATABASE [%%A_Regional] SET RECOVERY SIMPLE
>> %CDBase% echo GO
>> %CDBase% echo USE [%%A_Regional]
>> %CDBase% echo CREATE USER [IronDomeSRV1] FOR LOGIN [IronDomeSRV1]
>> %CDBase% echo EXEC sp_addrolemember N'db_owner', N'IronDomeSRV1'
))

for %%A in (
			FireBolt_FaultsDB_Operational
			FireBolt_ReportingDB_Operational
) do (
(
>> %CDBase% echo USE [%%A_Regional]
>> %CDBase% echo CREATE USER [IronDomeClient1] FOR LOGIN [IronDomeClient1]
>> %CDBase% echo EXEC sp_addrolemember N'db_datawriter', N'IronDomeClient1'
>> %CDBase% echo EXEC sp_addrolemember N'db_datareader', N'IronDomeClient1'
))

sqlcmd -S 10.11.%BN%8.%PN% -i %CDBase%