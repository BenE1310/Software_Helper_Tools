@echo off
cls
IF %IP%==1 GOTO BMC
IF %IP%==2 GOTO BMC
IF %IP%==3 GOTO DB
IF %IP%==4 GOTO DB
IF %IP%==6 GOTO Client
IF %IP%==7 GOTO Client
IF %IP%==8 GOTO Client
IF %IP%==9 GOTO Client
IF %IP%==10 GOTO Client
IF %IP%==13 GOTO ICS
IF %IP%==14 GOTO ICS
IF %IP%==20 GOTO DC1
IF %IP%==21 GOTO DC2
IF %IP%==22 GOTO SEP

:Client
@echo Configuring Client Network
netsh interface IP Set Address "BMCTeam" DHCP
Netsh Interface IP Delete DnsServers "BMCTeam" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="BMCTeam" Static 10.11.%Batt%8.%IP% 255.255.255.0 10.11.%Batt%8.254
Netsh Interface IP Add DNS Name="BMCTeam" 10.11.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="BMCTeam" 10.11.%Batt%3.21 Index=2
GOTO END

:BMC 
@echo Configuring BMC + ICS Networks(BMC)
netsh interface IP Set Address "BMCTeam" DHCP
Netsh Interface IP Delete DnsServers "BMCTeam" all
netsh interface IP Set Address "ICSTeam" DHCP
Netsh Interface IP Delete DnsServers "ICSTeam" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="BMCTeam" Static 10.11.%Batt%8.%IP% 255.255.255.0 10.11.%Batt%8.254
Netsh Interface IP Add DNS Name="BMCTeam" 10.11.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="BMCTeam" 10.11.%Batt%3.21 Index=2
Netsh Interface IP Set Address Name="ICSTeam" Static 10.12.%Batt%8.%IP% 255.255.255.0
Netsh Interface IP Add DNS Name="ICSTeam" 10.12.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="ICSTeam" 10.12.%Batt%3.21 Index=2
GOTO END

:DB 
@echo Configuring BMC + ICS Networks(DB)
netsh interface IP Set Address "BMCTeam" DHCP
Netsh Interface IP Delete DnsServers "BMCTeam" all
netsh interface IP Set Address "ICSTeam" DHCP
Netsh Interface IP Delete DnsServers "ICSTeam" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="BMCTeam" Static 10.11.%Batt%8.%IP% 255.255.255.0 10.11.%Batt%8.254
Netsh Interface IP Add DNS Name="BMCTeam" 10.11.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="BMCTeam" 10.11.%Batt%3.21 Index=2
Netsh Interface IP Set Address Name="ICSTeam" Static 10.12.%Batt%8.%IP% 255.255.255.0
Netsh Interface IP Add DNS Name="ICSTeam" 10.12.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="ICSTeam" 10.12.%Batt%3.21 Index=2
GOTO END

:ICS
@echo Configuring ICS Network(ICS)
netsh interface IP Set Address "ICSTeam" DHCP
Netsh Interface IP Delete DnsServers "ICSTeam" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="ICSTeam" Static 10.12.%Batt%8.%IP% 255.255.255.0 10.12.%Batt%8.254
Netsh Interface IP Add DNS Name="ICSTeam" 10.12.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="ICSTeam" 10.12.%Batt%3.21 Index=2
GOTO END

:DC1 
@echo Configuring BMC + ICS Networks(DC1)
netsh interface IP Set Address "BMC" DHCP
Netsh Interface IP Delete DnsServers "BMC" all
netsh interface IP Set Address "ICS" DHCP
Netsh Interface IP Delete DnsServers "ICS" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="BMC" Static 10.11.%Batt%3.%IP% 255.255.255.0 10.11.%Batt%3.254
Netsh Interface IP Add DNS Name="BMC" 127.0.0.1 Index=1
Netsh Interface IP Add DNS Name="BMC" 10.11.%Batt%3.21 Index=2
Netsh Interface IP Set Address Name="ICS" Static 10.12.%Batt%3.%IP% 255.255.255.0
Netsh Interface IP Add DNS Name="ICS" 127.0.0.1 Index=1
Netsh Interface IP Add DNS Name="ICS" 10.12.%Batt%3.21 Index=2
GOTO END

:DC2
@echo Configuring BMC + ICS Networks(DC2)
netsh interface IP Set Address "BMC" DHCP
Netsh Interface IP Delete DnsServers "BMC" all
netsh interface IP Set Address "ICS" DHCP
Netsh Interface IP Delete DnsServers "ICS" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="BMC" Static 10.11.%Batt%3.%IP% 255.255.255.0 10.11.%Batt%3.254
Netsh Interface IP Add DNS Name="BMC" 10.11.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="BMC" 127.0.0.1 Index=2
Netsh Interface IP Set Address Name="ICS" Static 10.12.%Batt%3.%IP% 255.255.255.0
Netsh Interface IP Add DNS Name="ICS" 10.12.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="ICS" 127.0.0.1 Index=2
GOTO END

:SEP 
@echo Configuring BMC + ICS Networks(SEP)
netsh interface IP Set Address "BMC" DHCP
Netsh Interface IP Delete DnsServers "BMC" all
netsh interface IP Set Address "ICS" DHCP
Netsh Interface IP Delete DnsServers "ICS" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="BMC" Static 10.11.%Batt%3.%IP% 255.255.255.0 10.11.%Batt%3.254
Netsh Interface IP Add DNS Name="BMC" 10.11.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="BMC" 10.11.%Batt%3.21 Index=2
Netsh Interface IP Set Address Name="ICS" Static 10.12.%Batt%3.%IP% 255.255.255.0
Netsh Interface IP Add DNS Name="ICS" 10.12.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="ICS" 10.12.%Batt%3.21 Index=2
GOTO END

:END
@echo.
@echo Finished!
GOTO:eof