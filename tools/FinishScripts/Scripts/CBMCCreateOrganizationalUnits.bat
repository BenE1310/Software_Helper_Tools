@echo off
setlocal enabledelayedexpansion
if /i %Batt% EQU 8 (set domainname=Fireboltcbmc)
if /i %Batt% EQU 9 (set domainname=Fireboltcbmc2)
rem FireBolt Computers
DSAdd OU "OU=FireBolt CBMC Computers,DC=%domainname%,DC=Local"
rem FireBolt CBMC Users
DSAdd OU "OU=FireBolt CBMC Users,DC=%domainname%,DC=Local"
rem Operational Users
DSAdd OU "OU=Operational Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local"
set BMCOperPath=OU=Operational Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local" -memberof "CN=BMC Operators,OU=Operational Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local"
DSAdd Group "CN=BMC Operators,OU=Operational Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local"
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn Commander@%domainname%.Local "CN=Commander, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP1@%domainname%.Local "CN=ICP1, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP2@%domainname%.Local "CN=ICP2, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP3@%domainname%.Local "CN=ICP3, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP4@%domainname%.Local "CN=ICP4, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP5@%domainname%.Local "CN=ICP5, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP6@%domainname%.Local "CN=ICP6, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP7@%domainname%.Local "CN=ICP7, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP8@%domainname%.Local "CN=ICP8, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP9@%domainname%.Local "CN=ICP9, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP10@%domainname%.Local "CN=ICP10, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP11@%domainname%.Local "CN=ICP11, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP12@%domainname%.Local "CN=ICP12, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP13@%domainname%.Local "CN=ICP13, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP14@%domainname%.Local "CN=ICP14, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn ICP15@%domainname%.Local "CN=ICP15, %BMCOperPath%
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn fbop@%domainname%.Local "CN=fbop, %BMCOperPath%
rem Technical Users
DSAdd OU "OU=Technical Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local"
set BMCTechPath=OU=Technical Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local"
DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn fbtech@%domainname%.Local "CN=fbtech, %BMCTechPath%
dsmod group "CN=Administrators,CN=Builtin,DC=%domainname%,DC=Local" -addmbr "CN=fbtech,OU=Technical Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local"
dsmod group "CN=Domain Admins,CN=Users,DC=%domainname%,DC=Local" -addmbr "CN=fbtech,OU=Technical Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local"
dsmod group "CN=Enterprise Admins,CN=Users,DC=%domainname%,DC=Local" -addmbr "CN=fbtech,OU=Technical Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local"
dsmod group "CN=Group Policy Creator Owners,CN=Users,DC=%domainname%,DC=Local" -addmbr "CN=fbtech,OU=Technical Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local"
dsmod group "CN=Schema Admins,CN=Users,DC=%domainname%,DC=Local" -addmbr "CN=fbtech,OU=Technical Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local"
rem Radar Users
rem DSAdd OU "OU=Radar Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local"
rem DSAdd User -pwd Q1w2e3r4t5 -pwdneverexpires yes -upn EltaTech@%domainname%.Local "CN=EltaTech,OU=Radar Users,OU=FireBolt CBMC Users,DC=%domainname%,DC=Local" -memberof "CN=Domain Admins,CN=Users,DC=%domainname%,DC=Local"
rem Windows Server 2008
DSAdd OU "OU=Windows Server 2008,OU=FireBolt CBMC Computers,DC=%domainname%,DC=Local"
DSAdd OU "OU=FireBolt Servers,OU=Windows Server 2008,OU=FireBolt CBMC Computers,DC=%domainname%,DC=Local"
DSAdd OU "OU=Security Server,OU=Windows Server 2008,OU=FireBolt CBMC Computers,DC=%domainname%,DC=Local"
rem Windows Server 2003
rem DSAdd OU "OU=Windows Server 2003,OU=FireBolt CBMC Computers,DC=%domainname%,DC=Local"
rem DSAdd OU "OU=Radar,OU=Windows Server 2003,OU=FireBolt CBMC Computers,DC=%domainname%,DC=Local"
rem Windows 7
DSAdd OU "OU=Windows 7,OU=FireBolt CBMC Computers,DC=%domainname%,DC=Local"
DSAdd OU "OU=Clients,OU=Windows 7,OU=FireBolt CBMC Computers,DC=%domainname%,DC=Local"
rem Windows XP
rem DSAdd OU "OU=Windows XP,OU=FireBolt CBMC Computers,DC=%domainname%,DC=Local"
rem DSAdd OU "OU=Radar,OU=Windows XP,OU=FireBolt CBMC Computers,DC=%domainname%,DC=Local"