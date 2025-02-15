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
Net Config Server /SRVComment:"BMC Server 1"
GOTO END

:BMC2
Net Config Server /SRVComment:"BMC Server 2"
GOTO END

:DB1
Net Config Server /SRVComment:"Database Server 1"
GOTO END

:DB2
Net Config Server /SRVComment:"Database Server 2"
GOTO END

:Client1
Net Config Server /SRVComment:"Tactical Client"
GOTO END

:Client2
Net Config Server /SRVComment:"Interception Client 1"
GOTO END

:Client3
Net Config Server /SRVComment:"Commander Client"
GOTO END

:Client4
Net Config Server /SRVComment:"Interception Client 2"
GOTO END

:Client5
Net Config Server /SRVComment:"Technical Client"
GOTO END

:ICS1
Net Config Server /SRVComment:"ICS Server 1"
GOTO END

:ICS2
Net Config Server /SRVComment:"ICS Server 2"
GOTO END

:DC1 
Net Config Server /SRVComment:"Domain Control 1"
GOTO END

:DC2
Net Config Server /SRVComment:"Domain Control 2"
GOTO END

:SEP 
Net Config Server /SRVComment:"SEP Server"
GOTO END

:END
@echo Finished!