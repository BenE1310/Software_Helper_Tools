@echo off
cls
IF %IP%==1 GOTO CBMC
IF %IP%==2 GOTO CBMC
IF %IP%==3 GOTO DBCBMC
IF %IP%==4 GOTO DBCBMC
IF %IP%==6 GOTO Client
IF %IP%==7 GOTO Client
IF %IP%==8 GOTO Client
IF %IP%==9 GOTO Client
IF %IP%==10 GOTO Client
IF %IP%==35 GOTO Client
IF %IP%==36 GOTO Client
IF %IP%==37 GOTO Client
IF %IP%==38 GOTO Client
IF %IP%==39 GOTO Client
IF %IP%==40 GOTO Client
IF %IP%==41 GOTO Client
IF %IP%==42 GOTO Client
IF %IP%==43 GOTO Client
IF %IP%==44 GOTO Client
IF %IP%==20 GOTO DC1
IF %IP%==21 GOTO DC2
IF %IP%==22 GOTO SEP

:Client
@echo Configuring Client Network
netsh interface IP Set Address "BMCTeam" DHCP
Netsh Interface IP Delete DnsServers "BMCTeam" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="BMCTeam" Static 10.11.%Batt%8.%IP% 255.255.255.0 10.11.%Batt%8.254
Netsh Interface IP Add Address Name="BMCTeam" 10.13.%Batt%8.%IP% 255.255.255.0
Netsh Interface IP Add DNS Name="BMCTeam" 10.11.%Batt%3.20 Index=1
rem Netsh Interface IP Add DNS Name="BMCTeam" 10.11.%Batt%3.21 Index=2
Netsh Interface IP Add DNS Name="BMCTeam" 10.13.%Batt%3.20 Index=2
GOTO END

:CBMC 
@echo Configuring CBMC Networks(BMC/DB)
netsh interface IP Set Address "BMCTeam" DHCP
Netsh Interface IP Delete DnsServers "BMCTeam" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="BMCTeam" Static 10.11.%Batt%8.%IP% 255.255.255.0 10.11.%Batt%8.254
Netsh Interface IP Add DNS Name="BMCTeam" 10.11.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="BMCTeam" 10.11.%Batt%3.21 Index=2
GOTO END

:DBCBMC
@echo Configuring CBMC Networks(DB)
netsh interface IP Set Address "BMCTeam" DHCP
Netsh Interface IP Delete DnsServers "BMCTeam" all
netsh interface IP Set Address "Debrief" DHCP
Netsh Interface IP Delete DnsServers "Debrief" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="BMCTeam" Static 10.11.%Batt%8.%IP% 255.255.255.0 10.11.%Batt%8.254
Netsh Interface IP Add DNS Name="BMCTeam" 10.11.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="BMCTeam" 10.11.%Batt%3.21 Index=2
Netsh Interface IP Set Address Name="Debrief" Static 10.13.%Batt%8.%IP% 255.255.255.0
Netsh Interface IP Add DNS Name="Debrief" 10.13.%Batt%3.20 Index=1
GOTO END

:DC1 
@echo Configuring CBMC Networks(DC1)
netsh interface IP Set Address "BMC" DHCP
Netsh Interface IP Delete DnsServers "BMC" all
netsh interface IP Set Address "Debrief" DHCP
Netsh Interface IP Delete DnsServers "Debrief" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="BMC" Static 10.11.%Batt%3.%IP% 255.255.255.0 10.11.%Batt%3.254
Netsh Interface IP Add DNS Name="BMC" 127.0.0.1 Index=1
Netsh Interface IP Add DNS Name="BMC" 10.11.%Batt%3.21 Index=2
Netsh Interface IP Set Address Name="Debrief" Static 10.13.%Batt%3.%IP% 255.255.255.0
GOTO END

:DC2
@echo Configuring CBMC Networks(DC2)
netsh interface IP Set Address "BMC" DHCP
Netsh Interface IP Delete DnsServers "BMC" all
netsh interface IP Set Address "Debrief" DHCP
Netsh Interface IP Delete DnsServers "Debrief" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="BMC" Static 10.11.%Batt%3.%IP% 255.255.255.0 10.11.%Batt%3.254
Netsh Interface IP Add DNS Name="BMC" 10.11.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="BMC" 127.0.0.1 Index=2
Netsh Interface IP Set Address Name="Debrief" Static 10.13.%Batt%3.%IP% 255.255.255.0
GOTO END


:SEP 
@echo Configuring CBMC Networks(SEP)
netsh interface IP Set Address "BMC" DHCP
Netsh Interface IP Delete DnsServers "BMC" all
netsh interface IP Delete Arpcache
netsh interface IP Set Address "Debrief" DHCP
Netsh Interface IP Delete DnsServers "Debrief" all
netsh interface IP Delete Arpcache
Netsh Interface IP Set Address Name="BMC" Static 10.11.%Batt%3.%IP% 255.255.255.0 10.11.%Batt%3.254
Netsh Interface IP Add DNS Name="BMC" 10.11.%Batt%3.20 Index=1
Netsh Interface IP Add DNS Name="BMC" 10.11.%Batt%3.21 Index=2
Netsh Interface IP Set Address Name="Debrief" Static 10.13.%Batt%3.%IP% 255.255.255.0
GOTO END

:END
@echo.
@echo Finished!
GOTO:eof