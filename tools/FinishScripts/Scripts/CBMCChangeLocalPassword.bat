@echo off
cls
IF %IP%==1 (set AdminPass=Fireboltcbmc1&& GOTO END)
IF %IP%==2 (set AdminPass=Fireboltcbmc2&& GOTO END)
IF %IP%==3 (set AdminPass=Fireboltdb1&& GOTO END)
IF %IP%==4 (set AdminPass=Fireboltdb2&& GOTO END)
IF %IP%==6 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==7 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==8 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==9 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==10 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==35 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==36 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==37 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==38 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==39 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==40 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==41 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==42 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==43 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==44 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==20 (set AdminPass=Fireboltdc1&& GOTO END)
IF %IP%==21 (set AdminPass=Fireboltdc2&& GOTO END)
IF %IP%==22 (set AdminPass=Fireboltsep1&& GOTO END)

:END
net user Administrator %AdminPass% /passwordreq:yes
echo New Password for Local Administrator is: %AdminPass%
pause