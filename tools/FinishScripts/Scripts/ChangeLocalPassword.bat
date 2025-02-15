@echo off
cls
IF %IP%==1 (set AdminPass=Fireboltbmc1&& GOTO END)
IF %IP%==2 (set AdminPass=Fireboltbmc2&& GOTO END)
IF %IP%==3 (set AdminPass=Fireboltdb1&& GOTO END)
IF %IP%==4 (set AdminPass=Fireboltdb2&& GOTO END)
IF %IP%==6 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==7 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==8 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==9 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==10 (set AdminPass=Fireboltclient%Batt%&& GOTO END)
IF %IP%==13 (set AdminPass=Fireboltics1&& GOTO END)
IF %IP%==14 (set AdminPass=Fireboltics2&& GOTO END)
IF %IP%==20 (set AdminPass=Fireboltdc1&& GOTO END)
IF %IP%==21 (set AdminPass=Fireboltdc2&& GOTO END)
IF %IP%==22 (set AdminPass=Fireboltsep1&& GOTO END)

:END
net user Administrator %AdminPass% /passwordreq:yes
echo New Password for Local Administrator is: %AdminPass%
pause