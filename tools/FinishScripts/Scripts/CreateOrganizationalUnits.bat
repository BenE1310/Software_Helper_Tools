@echo off
setlocal enabledelayedexpansion
rem FireBolt Computers
DSAdd OU "OU=FireBolt Computers,DC=FireBolt%Batt%,DC=Local"
rem FireBolt Users
DSAdd OU "OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
rem Operational Users
DSAdd OU "OU=Operational Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
set BMCOperPath=OU=Operational Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local" -memberof "CN=BMC Operators,OU=Operational Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
DSAdd Group "CN=BMC Operators,OU=Operational Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn Commander@FireBolt%Batt%.Local "CN=Commander, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP1@FireBolt%Batt%.Local "CN=ICP1, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP2@FireBolt%Batt%.Local "CN=ICP2, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP3@FireBolt%Batt%.Local "CN=ICP3, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP4@FireBolt%Batt%.Local "CN=ICP4, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn fbop@FireBolt%Batt%.Local "CN=fbop, %BMCOperPath%
rem Launcher Operator
rem DSAdd OU "OU=Launcher Operator,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
rem DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn LauncherOP@FireBolt%Batt%.Local "CN=LauncherOP,OU=Launcher Operator,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
rem Technical Users
DSAdd OU "OU=Technical Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
set BMCTechPath=OU=Technical Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn fbtech@FireBolt%Batt%.Local "CN=fbtech, %BMCTechPath%
dsmod group "CN=Administrators,CN=Builtin,DC=FireBolt%Batt%,DC=Local" -addmbr "CN=fbtech,OU=Technical Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
dsmod group "CN=Domain Admins,CN=Users,DC=FireBolt%Batt%,DC=Local" -addmbr "CN=fbtech,OU=Technical Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
dsmod group "CN=Enterprise Admins,CN=Users,DC=FireBolt%Batt%,DC=Local" -addmbr "CN=fbtech,OU=Technical Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
dsmod group "CN=Group Policy Creator Owners,CN=Users,DC=FireBolt%Batt%,DC=Local" -addmbr "CN=fbtech,OU=Technical Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
dsmod group "CN=Schema Admins,CN=Users,DC=FireBolt%Batt%,DC=Local" -addmbr "CN=fbtech,OU=Technical Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
rem Radar Users
rem DSAdd OU "OU=Radar Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local"
rem DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn EltaTech@FireBolt%Batt%.Local "CN=EltaTech,OU=Radar Users,OU=FireBolt Users,DC=FireBolt%Batt%,DC=Local" -memberof "CN=Domain Admins,CN=Users,DC=FireBolt%Batt%,DC=Local"
rem Windows Server 2008
DSAdd OU "OU=Windows Server 2008,OU=FireBolt Computers,DC=FireBolt%Batt%,DC=Local"
DSAdd OU "OU=FireBolt Servers,OU=Windows Server 2008,OU=FireBolt Computers,DC=FireBolt%Batt%,DC=Local"
DSAdd OU "OU=Security Server,OU=Windows Server 2008,OU=FireBolt Computers,DC=FireBolt%Batt%,DC=Local"
rem Windows Server 2003
rem DSAdd OU "OU=Windows Server 2003,OU=FireBolt Computers,DC=FireBolt%Batt%,DC=Local"
rem DSAdd OU "OU=Radar,OU=Windows Server 2003,OU=FireBolt Computers,DC=FireBolt%Batt%,DC=Local"
rem Windows 7
DSAdd OU "OU=Windows 7,OU=FireBolt Computers,DC=FireBolt%Batt%,DC=Local"
DSAdd OU "OU=Clients,OU=Windows 7,OU=FireBolt Computers,DC=FireBolt%Batt%,DC=Local"
rem Windows XP
rem DSAdd OU "OU=Windows XP,OU=FireBolt Computers,DC=FireBolt%Batt%,DC=Local"
rem DSAdd OU "OU=Launchers,OU=Windows XP,OU=FireBolt Computers,DC=FireBolt%Batt%,DC=Local"
rem DSAdd OU "OU=Radar,OU=Windows XP,OU=FireBolt Computers,DC=FireBolt%Batt%,DC=Local"