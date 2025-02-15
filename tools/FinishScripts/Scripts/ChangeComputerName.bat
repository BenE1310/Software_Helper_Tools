@echo off
cls
IF %IP%==1 GOTO BMC1
IF %IP%==2 GOTO BMC2
IF %IP%==3 GOTO DB1
IF %IP%==4 GOTO DB2
IF %IP%==6 GOTO Client1
IF %IP%==7 GOTO Client2
IF %IP%==8 GOTO Client3
IF %IP%==9 GOTO Client4
IF %IP%==10 GOTO Client5
IF %IP%==13 GOTO ICS1
IF %IP%==14 GOTO ICS2
IF %IP%==20 GOTO DC1
IF %IP%==21 GOTO DC2
IF %IP%==22 GOTO SEP



:BMC1
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%8-01"
GOTO END

:BMC2
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%8-02"
GOTO END

:DB1
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%8-03"
GOTO END

:DB2
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%8-04"
GOTO END

:Client1
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%8-06"
GOTO END

:Client2
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%8-07"
GOTO END

:Client3
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%8-08"
GOTO END

:Client4
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%8-09"
GOTO END

:Client5
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%8-10"
GOTO END

:ICS1
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%8-13"
GOTO END

:ICS2
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%8-14"
GOTO END

:DC1 
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%3-20"
GOTO END

:DC2
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%3-21"
GOTO END

:SEP 
WMIC ComputerSystem where Name="%computername%" call Rename Name="FB-%Batt%3-22"
GOTO END

:END
@echo Finished!