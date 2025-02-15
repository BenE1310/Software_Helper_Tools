@echo off
setlocal enabledelayedexpansion
echo Creating Databases For CBMC %SN%
set CDBase="C:\Windows\Temp\CDBase.sql"
del %CDBase%
MD C:\FireBoltDB

>> %CDBase% echo CREATE LOGIN [IronDomeSRV1] WITH PASSWORD='QAZ', DEFAULT_DATABASE=[master], DEFAULT_LANGUAGE=[us_english], CHECK_EXPIRATION=OFF, CHECK_POLICY=OFF
>> %CDBase% echo GO
>> %CDBase% echo CREATE LOGIN [IronDomeClient1] WITH PASSWORD='QAZ', DEFAULT_DATABASE=[master], DEFAULT_LANGUAGE=[us_english], CHECK_EXPIRATION=OFF, CHECK_POLICY=OFF
>> %CDBase% echo GO

for %%A in (
			FireBolt_BMCConfigDB_Operational_Regional
			FireBolt_BMCConfigDB_Training_Regional
			FireBolt_FaultsDB_Operational_Regional
			FireBolt_FaultsDB_Training_Regional
			FireBolt_PolicyDB_Operational_Regional
			FireBolt_PolicyDB_Training_Regional
			FireBolt_ReportingDB_Operational_Regional
			FireBolt_ReportingDB_Training_Regional
) do (
(
>> %CDBase% echo USE [master]
>> %CDBase% echo GO
>> %CDBase% echo CREATE DATABASE [%%A] ON  PRIMARY 
>> %CDBase% echo ^( NAME = N'%%A', FILENAME = N'C:\FireBoltDB\%%A.mdf' , SIZE = 2048KB , MAXSIZE = UNLIMITED, FILEGROWTH = 1024KB ^)
>> %CDBase% echo  LOG ON
>> %CDBase% echo ^( NAME = N'%%A_log', FILENAME = N'C:\FireBoltDB\%%A_log.ldf' , SIZE = 1024KB , MAXSIZE = 2048GB , FILEGROWTH = 10%% ^)
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
			FireBolt_FaultsDB_Operational_Regional
			FireBolt_FaultsDB_Training_Regional
			FireBolt_ReportingDB_Operational_Regional
			FireBolt_ReportingDB_Training_Regional
) do (
(
>> %CDBase% echo USE [%%A]
>> %CDBase% echo CREATE USER [IronDomeClient1] FOR LOGIN [IronDomeClient1]
>> %CDBase% echo EXEC sp_addrolemember N'db_datawriter', N'IronDomeClient1'
>> %CDBase% echo EXEC sp_addrolemember N'db_datareader', N'IronDomeClient1'
))

sqlcmd -i %CDBase%