@echo off
setlocal enabledelayedexpansion
if /i %Batt% EQU 8 (set CBMCnum=1&& set domainname=Fireboltcbmc)
if /i %Batt% EQU 9 (set CBMCnum=2&& set domainname=Fireboltcbmc2)
echo Deleting old Answerfile...
set JDCBMCAnswerfile="C:\Windows\Temp\JDCBMCAnswerfile.txt"
del %JDCBMCAnswerfile%
set /p DUserName=Please enter user name with domain admin permission to add a secondary domain controller: 
set /p DPassword=Please enter password for %DUserName%: 
echo New Password for DC2 Local Administrator is: %DPassword%
net user Administrator %DPassword% /passwordreq:yes
echo [DCInstall]> %JDCBMCAnswerfile%
echo ReplicaOrNewDomain=Replica>> %JDCBMCAnswerfile%
echo ReplicaDomainDNSName=%domainname%.local>> %JDCBMCAnswerfile%
echo SiteName=Default-First-Site-Name>> %JDCBMCAnswerfile%
echo InstallDNS=Yes>> %JDCBMCAnswerfile%
echo ConfirmGc=Yes>> %JDCBMCAnswerfile%
echo CreateDNSDelegation=No>> %JDCBMCAnswerfile%
echo UserDomain=%domainname%.local>> %JDCBMCAnswerfile%
echo UserName=%domainname%.local\%DUserName%>> %JDCBMCAnswerfile%
echo Password=%DPassword%>> %JDCBMCAnswerfile%
echo ReplicationSourceDC=DC1-CBMC%CBMCnum%.%domainname%.local>> %JDCBMCAnswerfile%
echo DatabasePath="C:\Windows\NTDS">> %JDCBMCAnswerfile%
echo LogPath="C:\Windows\NTDS">> %JDCBMCAnswerfile%
echo SYSVOLPath="C:\Windows\SYSVOL">> %JDCBMCAnswerfile%
echo SafeModeAdminPassword=%DPassword%>> %JDCBMCAnswerfile%
echo RebootOnCompletion=Yes>> %JDCBMCAnswerfile%
dcpromo /answer:%JDCBMCAnswerfile%