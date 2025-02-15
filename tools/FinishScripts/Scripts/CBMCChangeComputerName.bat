@echo off
cls
if /i %Batt% EQU 8 (set CBMCnum=1)
if /i %Batt% EQU 9 (set CBMCnum=2)
IF %IP%==1 GOTO CBMC1
IF %IP%==2 GOTO CBMC2
IF %IP%==3 GOTO DB1CBMC
IF %IP%==4 GOTO DB2CBMC
IF %IP%==6 GOTO Client1
IF %IP%==7 GOTO Client2
IF %IP%==8 GOTO Client3
IF %IP%==9 GOTO Client4
IF %IP%==10 GOTO Client5
IF %IP%==35 GOTO Client6
IF %IP%==36 GOTO Client7
IF %IP%==37 GOTO Client8
IF %IP%==38 GOTO Client9
IF %IP%==39 GOTO Client10
IF %IP%==40 GOTO Client11
IF %IP%==41 GOTO Client12
IF %IP%==42 GOTO Client13
IF %IP%==43 GOTO Client14
IF %IP%==44 GOTO Client15
IF %IP%==20 GOTO DC1
IF %IP%==21 GOTO DC2
IF %IP%==22 GOTO SEP



:CBMC1
WMIC ComputerSystem where Name="%computername%" call Rename Name="BMC1-CBMC%CBMCnum%"
GOTO END

:CBMC2
WMIC ComputerSystem where Name="%computername%" call Rename Name="BMC2-CBMC%CBMCnum%"
GOTO END

:DB1CBMC
WMIC ComputerSystem where Name="%computername%" call Rename Name="DB1-CBMC%CBMCnum%"
GOTO END

:DB2CBMC
WMIC ComputerSystem where Name="%computername%" call Rename Name="DB2-CBMC%CBMCnum%"
GOTO END

:Client1
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client1-CBMC%CBMCnum%"
GOTO END

:Client2
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client2-CBMC%CBMCnum%"
GOTO END

:Client3
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client3-CBMC%CBMCnum%"
GOTO END

:Client4
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client4-CBMC%CBMCnum%"
GOTO END

:Client5
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client5-CBMC%CBMCnum%"
GOTO END

:Client6
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client6-CBMC%CBMCnum%"
GOTO END

:Client7
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client7-CBMC%CBMCnum%"
GOTO END

:Client8
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client8-CBMC%CBMCnum%"
GOTO END

:Client9
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client9-CBMC%CBMCnum%"
GOTO END

:Client10
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client10-CBMC%CBMCnum%"
GOTO END

:Client11
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client11-CBMC%CBMCnum%"
GOTO END

:Client12
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client12-CBMC%CBMCnum%"
GOTO END

:Client13
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client13-CBMC%CBMCnum%"
GOTO END

:Client14
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client14-CBMC%CBMCnum%"
GOTO END

:Client15
WMIC ComputerSystem where Name="%computername%" call Rename Name="Client15-CBMC%CBMCnum%"
GOTO END

:DC1 
WMIC ComputerSystem where Name="%computername%" call Rename Name="DC1-CBMC%CBMCnum%"
GOTO END

:DC2
WMIC ComputerSystem where Name="%computername%" call Rename Name="DC2-CBMC%CBMCnum%"
GOTO END


:SEP 
WMIC ComputerSystem where Name="%computername%" call Rename Name="SEP-CBMC%CBMCnum%"
GOTO END

:END
@echo Finished!