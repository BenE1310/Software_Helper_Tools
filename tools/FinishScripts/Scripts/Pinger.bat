@echo off
cls
:PingStart
echo.
echo             ����������������������������������������������������ͻ
echo             �            Select the segment to ping              �
echo             ����������������������������������������������������͹
echo             �  1. Client's                                       �
echo             �  2. BMC Servers                                    �
echo             �  3. ICS Servers                                    �
echo             �  4. DB Servers                                     �
echo             �  5. Domain Control Servers                         �
echo             �  6. SEP Server                                     �
echo             �  ------------------------------------------------  �
echo             �  K. Kill ping                                      �
echo             �  M. Main Menu                                      �
echo             ����������������������������������������������������ͼ
echo.

:PingChoice
set /p PingChoice=Please Choose an Option: 
if '%PingChoice%'=='1' GOTO ClientPing
if '%PingChoice%'=='2' GOTO BMCServersPing
if '%PingChoice%'=='3' GOTO ICSServersPing
if '%PingChoice%'=='4' GOTO DBServersPing
if '%PingChoice%'=='5' GOTO DomainControlPing
if '%PingChoice%'=='6' GOTO SEPPing
if /i '%PingChoice%'=='K' GOTO KillPing
if /i '%PingChoice%'=='M' GOTO:eof
if not '%PingChoice%'=='' echo "%PingChoice%" is not valid, please try again
GOTO PingChoice

:ClientPing
start /min ping 10.11.%Batt%8.6 -t
start /min ping 10.11.%Batt%8.7 -t
start /min ping 10.11.%Batt%8.8 -t
start /min ping 10.11.%Batt%8.9 -t
start /min ping 10.11.%Batt%8.10 -t
GOTO PingStart

:BMCServersPing
start /min ping 10.11.%Batt%8.1 -t
start /min ping 10.11.%Batt%8.2 -t
start /min ping 10.12.%Batt%8.1 -t
start /min ping 10.12.%Batt%8.2 -t
GOTO PingStart

:ICSServersPing
start /min ping 10.12.%Batt%8.13 -t
start /min ping 10.12.%Batt%8.14 -t
GOTO PingStart

:DBServersPing
start /min ping 10.11.%Batt%8.3 -t
start /min ping 10.11.%Batt%8.4 -t
start /min ping 10.12.%Batt%8.3 -t
start /min ping 10.12.%Batt%8.4 -t
GOTO PingStart

:DomainControlPing
start /min ping 10.11.%Batt%3.20 -t
start /min ping 10.11.%Batt%3.21 -t
start /min ping 10.12.%Batt%3.20 -t
start /min ping 10.12.%Batt%3.21 -t
GOTO PingStart

:SEPPing
start /min ping 10.11.%Batt%3.22 -t
start /min ping 10.12.%Batt%3.22 -t
GOTO PingStart

:KillPing
taskkill /im ping.exe /f
GOTO PingStart

pause