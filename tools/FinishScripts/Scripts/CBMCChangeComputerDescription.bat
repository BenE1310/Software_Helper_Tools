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

%CBMCnum%

:CBMC1
Net Config Server /SRVComment:"CBMC%CBMCnum% Server 1"
GOTO END

:CBMC2
Net Config Server /SRVComment:"CBMC%CBMCnum% Server 2"
GOTO END

:DB1CBMC
Net Config Server /SRVComment:"CBMC%CBMCnum% Database Server 1"
GOTO END

:DB2CBMC
Net Config Server /SRVComment:"CBMC%CBMCnum% Database Server 2"
GOTO END

:Client1
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 1"
GOTO END

:Client2
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 2"
GOTO END

:Client3
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 3"
GOTO END

:Client4
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 4"
GOTO END

:Client5
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 5"
GOTO END

:Client6
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 6"
GOTO END

:Client7
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 7"
GOTO END

:Client8
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 8"
GOTO END

:Client9
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 9"
GOTO END

:Client10
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 10"
GOTO END

:Client11
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 11"
GOTO END

:Client12
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 12"
GOTO END

:Client13
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 13"
GOTO END

:Client14
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 14"
GOTO END

:Client15
Net Config Server /SRVComment:"CBMC%CBMCnum% Client 15"
GOTO END

:DC1 
Net Config Server /SRVComment:"CBMC%CBMCnum% Domain Control 1"
GOTO END

:DC2
Net Config Server /SRVComment:"CBMC%CBMCnum% Domain Control 2"
GOTO END


:SEP 
Net Config Server /SRVComment:"CBMC%CBMCnum% SEP Server"
GOTO END

:END
@echo Finished!