@echo off
:PingStart
cls
echo.
echo             ษออออออออออออออออออออออออออออออออออออออออออออออออออออป
echo             บ            Select the segment to ping              บ
echo             ฬออออออออออออออออออออออออออออออออออออออออออออออออออออน
echo             บ  1. Client's                                       บ
echo             บ  2. CBMC Servers                                   บ
echo             บ  4. DB Servers                                     บ
echo             บ  5. Domain Control Servers                         บ
echo             บ  6. SEP Server                                     บ
echo             บ  ------------------------------------------------  บ
echo             บ  K. Kill ping                                      บ
echo             บ  M. Main Menu                                      บ
echo             ศออออออออออออออออออออออออออออออออออออออออออออออออออออผ
echo.

:PingChoice
set /p PingChoice=Please Choose an Option: 
if '%PingChoice%'=='1' GOTO ClientPing
if '%PingChoice%'=='2' GOTO BMCServersPing
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
start /min ping 10.11.%Batt%8.35 -t
start /min ping 10.11.%Batt%8.36 -t
start /min ping 10.11.%Batt%8.37 -t
start /min ping 10.11.%Batt%8.38 -t
start /min ping 10.11.%Batt%8.39 -t
start /min ping 10.11.%Batt%8.40 -t
start /min ping 10.11.%Batt%8.41 -t
start /min ping 10.11.%Batt%8.42 -t
start /min ping 10.11.%Batt%8.43 -t
start /min ping 10.11.%Batt%8.44 -t
start /min ping 10.11.%Batt%8.45 -t
GOTO PingStart

:BMCServersPing
start /min ping 10.11.%Batt%8.1 -t
start /min ping 10.11.%Batt%8.2 -t
GOTO PingStart


:DBServersPing
start /min ping 10.11.%Batt%8.3 -t
start /min ping 10.11.%Batt%8.4 -t
GOTO PingStart

:DomainControlPing
start /min ping 10.11.%Batt%3.20 -t
start /min ping 10.11.%Batt%3.21 -t
GOTO PingStart

:SEPPing
start /min ping 10.11.%Batt%3.22 -t
GOTO PingStart

:KillPing
taskkill /im ping.exe /f
GOTO PingStart

pause