@echo off
setlocal enabledelayedexpansion
echo Creating Databases For Battery %Batt%
set CDBase="C:\Windows\Temp\CDBase.sql"
del %CDBase%
MD C:\FireBoltDB

>> %CDBase% echo CREATE LOGIN [IronDomeSRV1] WITH PASSWORD='QAZ', DEFAULT_DATABASE=[master], DEFAULT_LANGUAGE=[us_english], CHECK_EXPIRATION=OFF, CHECK_POLICY=OFF
>> %CDBase% echo GO
>> %CDBase% echo CREATE LOGIN [IronDomeClient1] WITH PASSWORD='QAZ', DEFAULT_DATABASE=[master], DEFAULT_LANGUAGE=[us_english], CHECK_EXPIRATION=OFF, CHECK_POLICY=OFF
>> %CDBase% echo GO

for %%A in (
			FireBolt_BMCConfigDB_Operational
			FireBolt_BMCConfigDB_Training
			FireBolt_FaultsDB_Operational
			FireBolt_FaultsDB_Training
			FireBolt_PolicyDB_Operational
			FireBolt_PolicyDB_Training
			FireBolt_ReportingDB_Operational
			FireBolt_ReportingDB_Training
) do (
(
>> %CDBase% echo USE [master]
>> %CDBase% echo GO
>> %CDBase% echo CREATE DATABASE [%%A_%Batt%] ON  PRIMARY 
>> %CDBase% echo ^( NAME = N'%%A_%Batt%', FILENAME = N'C:\FireBoltDB\%%A_%Batt%.mdf' , SIZE = 5048KB , MAXSIZE = UNLIMITED, FILEGROWTH = 1024KB ^)
>> %CDBase% echo  LOG ON
>> %CDBase% echo ^( NAME = N'%%A_%Batt%_log', FILENAME = N'C:\FireBoltDB\%%A_%Batt%_log.ldf' , SIZE = 5024KB , MAXSIZE = 2048GB , FILEGROWTH = 10%% ^)
>> %CDBase% echo GO
>> %CDBase% echo ALTER DATABASE [%%A_%Batt%] SET COMPATIBILITY_LEVEL = 100
>> %CDBase% echo GO
>> %CDBase% echo IF ^(1 = FULLTEXTSERVICEPROPERTY^('IsFullTextInstalled'^)^)
>> %CDBase% echo begin
>> %CDBase% echo EXEC [%%A_%Batt%].[dbo].[sp_fulltext_database] @action = 'enable'
>> %CDBase% echo end
>> %CDBase% echo GO
>> %CDBase% echo ALTER DATABASE [%%A_%Batt%] SET RECOVERY SIMPLE 
>> %CDBase% echo GO
>> %CDBase% echo USE [%%A_%Batt%]
>> %CDBase% echo CREATE USER [IronDomeSRV1] FOR LOGIN [IronDomeSRV1]
>> %CDBase% echo EXEC sp_addrolemember N'db_owner', N'IronDomeSRV1'
))

for %%A in (
			FireBolt_FaultsDB_Operational
			FireBolt_FaultsDB_Training
			FireBolt_ReportingDB_Operational
			FireBolt_ReportingDB_Training
) do (
(
>> %CDBase% echo USE [%%A_%Batt%]
>> %CDBase% echo CREATE USER [IronDomeClient1] FOR LOGIN [IronDomeClient1]
>> %CDBase% echo EXEC sp_addrolemember N'db_datawriter', N'IronDomeClient1'
>> %CDBase% echo EXEC sp_addrolemember N'db_datareader', N'IronDomeClient1'
))

sqlcmd -i %CDBase%