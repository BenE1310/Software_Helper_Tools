@echo off
setlocal enabledelayedexpansion
set /a BN=21
set /a PN=3
echo Creating Databases For VSIL Bat
set CDBase="C:\Windows\Temp\CDBase.sql"
del %CDBase%
MD C:\FireBoltDB

for %%A in (
			FireBolt_BMCConfigDB_VSIL_Regional
			FireBolt_FaultsDB_VSIL_Regional
			FireBolt_PolicyDB_VSIL_Regional
			FireBolt_ReportingDB_VSIL_Regional

) do (
(
>> %CDBase% echo USE [master]
>> %CDBase% echo GO
>> %CDBase% echo CREATE DATABASE [%%A] ON  PRIMARY
>> %CDBase% echo ^( NAME = N'%%A', FILENAME = N'C:\FireBoltDB\%%A.mdf' , SIZE = 5048KB , MAXSIZE = UNLIMITED, FILEGROWTH = 1024KB ^)
>> %CDBase% echo  LOG ON
>> %CDBase% echo ^( NAME = N'%%A_log', FILENAME = N'C:\FireBoltDB\%%A_log.ldf' , SIZE = 5024KB , MAXSIZE = 2048GB , FILEGROWTH = 10%% ^)
>> %CDBase% echo GO
>> %CDBase% echo ALTER DATABASE [%%A] SET COMPATIBILITY_LEVEL = 100
>> %CDBase% echo GO
>> %CDBase% echo IF ^(1 = FULLTEXTSERVICEPROPERTY^('IsFullTextInstalled'^)^)
>> %CDBase% echo begin
>> %CDBase% echo EXEC [%%A].[dbo].[sp_fulltext_database] @action = 'enable'
>> %CDBase% echo end
>> %CDBase% echo GO
>> %CDBase% echo ALTER DATABASE [%%A] SET RECOVERY SIMPLE
>> %CDBase% echo GO
>> %CDBase% echo USE [%%A]
>> %CDBase% echo CREATE USER [IronDomeSRV1] FOR LOGIN [IronDomeSRV1]
>> %CDBase% echo EXEC sp_addrolemember N'db_owner', N'IronDomeSRV1'
))

for %%A in (
			FireBolt_FaultsDB_VSIL_Regional
		    FireBolt_ReportingDB_VSIL_Regional

) do (
(
>> %CDBase% echo USE [%%A]
>> %CDBase% echo CREATE USER [IronDomeClient1] FOR LOGIN [IronDomeClient1]
>> %CDBase% echo EXEC sp_addrolemember N'db_datawriter', N'IronDomeClient1'
>> %CDBase% echo EXEC sp_addrolemember N'db_datareader', N'IronDomeClient1'
))

sqlcmd -S 10.11.218.3 -i %CDBase%