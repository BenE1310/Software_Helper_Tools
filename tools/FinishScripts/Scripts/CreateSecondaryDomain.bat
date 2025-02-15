@echo off
setlocal enabledelayedexpansion
echo Deleting old Answerfile...
set JDCAnswerfile="C:\Windows\Temp\JDCAnswerfile.txt"
del %JDCAnswerfile%
set /p DBMCUserName=Please enter user name with domain admin permission to add a secondary domain controller: 
set /p DBMCPassword=Please enter password for %DBMCPassword%: 
echo New Password for DC2 Local Administrator is: %DBMCPassword%
net user Administrator %DBMCPassword% /passwordreq:yes
echo [DCInstall]> %JDCAnswerfile%
echo ReplicaOrNewDomain=Replica>> %JDCAnswerfile%
echo ReplicaDomainDNSName=FireBolt%Batt%.local>> %JDCAnswerfile%
echo SiteName=Default-First-Site-Name>> %JDCAnswerfile%
echo InstallDNS=Yes>> %JDCAnswerfile%
echo ConfirmGc=Yes>> %JDCAnswerfile%
echo CreateDNSDelegation=No>> %JDCAnswerfile%
echo UserDomain=FireBolt%Batt%.local>> %JDCAnswerfile%
echo UserName=FireBolt%Batt%.local\%DBMCUserName%>> %JDCAnswerfile%
echo Password=%DBMCPassword%>> %JDCAnswerfile%
echo ReplicationSourceDC=DC1-Bat%Batt%.FireBolt%Batt%.local>> %JDCAnswerfile%
echo DatabasePath="C:\Windows\NTDS">> %JDCAnswerfile%
echo LogPath="C:\Windows\NTDS">> %JDCAnswerfile%
echo SYSVOLPath="C:\Windows\SYSVOL">> %JDCAnswerfile%
echo SafeModeAdminPassword=%DBMCPassword%>> %JDCAnswerfile%
echo RebootOnCompletion=Yes>> %JDCAnswerfile%
dcpromo /answer:%JDCAnswerfile%