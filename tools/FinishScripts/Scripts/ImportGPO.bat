@echo off
cls
setlocal enabledelayedexpansion
echo Importing Group Policy Objects...
set GPOFolder="C:\GPO"

for %%A in (

			"Default Domain Policy"
			"Default Domain Controllers Policy"
			"Domain Controller Policy"
			"Operational Servers Policy"
			"Security Servers Policy"
			"Clients Computers Policy"
			"Operational Users Policy"
			"Operational Disabled Share Policy"
			"Deny-BurningTools"
			"Deny-RDP"

) do (
(
PowerShell.Exe import-module GroupPolicy; Import-GPO -BackupGpoName ""%%A"" -Path ""%GPOFolder%"" -TargetName ""%%A"" -MigrationTable ""%GPOFolder%\FB%Batt%Migration.migtable"" -CreateIfNeeded
))
GPUpdate /Force