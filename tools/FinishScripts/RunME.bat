@echo off
rem mode con:cols=79 lines=40
mode con:lines=40
title FireBolt Configuration Tools
@setlocal enableextensions enabledelayedexpansion
@cd /d "%~dp0"
:Check_Permissions
echo Administrative permissions required. Detecting permissions...
echo.
net session >nul 2>&1
   if %errorLevel% == 0 (
echo Success: Administrative permissions confirmed.
cls
goto logo
) else (
echo Error: Logged in as: %userdomain%\%username%
echo        Please Login with Administrative permissions And
echo        Right Click the file ฏ Run as administrator
echo.
    )
pause
exit

:logo
:BatteryNumber
call "%~dp0"\"Scripts"\"Logo.Bat"
echo.
echo            ษออออออออออออออออออหออออออออออออออออออป
echo            บ      CBMC        บ      Battery     บ 
echo            ฬออออออออออออออออออฮออออออออออออออออออน
echo            บ  8. CBMC 1       บ   1. Battery 1   บ
echo            บ  9. CBMC 2       บ   2. Battery 2   บ 
echo            บ                  บ   3. Battery 3   บ 
echo            บ                  บ   4. Battery 4   บ                  
echo            บ                  บ   5. Battery 5   บ                  
echo            บ                  บ   6. Battery 6   บ
echo            ศออออออออออออออออออสออออออออออออออออออผ
echo.
set /p BN=Please Choose an Option: 
if /i %BN% EQU VSIL (set Batt=8)&& (set BN=08)&& goto VSILStart
echo %BN%| findstr /r "^[1-9][0-9]*$">nul
set BN_Error=false
if errorlevel 1 set BN_Error=true
if /i %BN% GEQ 10 set BN_Error=true
if /i %BN% EQU 7 set BN_Error=true
if "%BN_Error%"=="true" (
	cls
	goto BatteryNumber
)
if /i %BN% LEQ 6 if /i %BN% LEQ 9 (set Batt=%BN%)&& (set BN=0%BN%)&& goto Start 
if /i %BN% GEQ 8 if /i %BN% LEQ 9 (set Batt=%BN%)&& (set BN=0%BN%)&& goto CStart
rem for 0UserInput use %BN%
rem echo BN = %BN%
rem for UserInput use %Batt%
rem echo Batt = %Batt%

:Start
cls
call "%~dp0"\"Scripts"\"Logo.Bat"
echo                              [  Battery %Batt% Menu  ]
echo    ษอออออออออออออออออออออออหอออออออออออออออออออออออหออออออออออออออออออออออออป
echo    บ    Primary Servers    บ    Backup Servers     บ        Clients         บ
echo    ฬอออออออออออออออออออออออฮอออออออออออออออออออออออฮออออออออออออออออออออออออน
echo    บ   1. BMC 1            บ   2. BMC 2            บ     6. Client 1        บ
echo    บ   3. DB  1            บ   4. DB 2             บ     7. Client 2        บ
echo    บ  13. ICS 1            บ  14. ICS 2            บ     8. Client 3        บ
echo    บ  20. AD1              บ  21. AD2              บ     9. Client 4        บ
echo    บ                       บ                       บ    10. Client 5        บ
echo    ศอออออออออออออออออออออออสอออออออออออออออออออออออสออออออออออออออออออออออออผ
echo    ษอออออออออออออออออออออออออออออออออออหออออออออออออออออออออออออออออออออออออป
echo    บ           Tools                   บ  Domain Manage for Battery %Batt%       บ
echo    ฬอออออออออออออออออออออออออออออออออออฮออออออออออออออออออออออออออออออออออออน
echo    บ  JD. Join Domain                  บ  DM. Domain Manage Tools           บ
echo    ศอออออออออออออออออออออออออออออออออออสออออออออออออออออออออออออออออออออออออผ
echo     B. Back to main menu
echo     E. Exit
echo.
goto Choice


:CStart
if /i %Batt% EQU 8 (set CBMCnum=1)
if /i %Batt% EQU 9 (set CBMCnum=2)
cls
call "%~dp0"\"Scripts"\"Logo.Bat"
echo                                [  CBMC %CBMCnum% Menu  ]
echo    ษอออออออออออออออออออออออออออออออออออหออออออออออออออออออออออออออออออออออออป
echo    บ          Primary Servers          บ          Backup Servers            บ
echo    ฬอออออออออออออออออออออออออออออออออออฮออออออออออออออออออออออออออออออออออออน
echo    บ     1. CBMC 1                     บ     2. CBMC 2                      บ
echo    บ     3. DataBase 1                 บ     4. DataBase 2                  บ
echo    บ                                   บ    21. Domain Control 2            บ
echo    ศอออออออออออออออออออออออออออออออออออสออออออออออออออออออออออออออออออออออออผ
echo    ษออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
echo    บ                                Clients                                 บ
echo    ฬอออออออออออออออออออออออหอออออออออออออออออออออออหออออออออออออออออออออออออน
echo    บ     6. Client 1       บ    35. Client 6       บ    40. Client 11       บ
echo    บ     7. Client 2       บ    36. Client 7       บ    41. Client 12       บ
echo    บ     8. Client 3       บ    37. Client 8       บ    42. Client 13       บ
echo    บ     9. Client 4       บ    38. Client 9       บ    43. Client 14       บ
echo    บ    10. Client 5       บ    39. Client 10      บ    44. Client 15       บ
echo    ศอออออออออออออออออออออออสอออออออออออออออออออออออสออออออออออออออออออออออออผ
echo    ษอออออออออออออออออออออออออออออออออออหออออออออออออออออออออออออออออออออออออป
echo    บ           Tools                   บ  Domain Manage for CBMC %CBMCnum%          บ
echo    ฬอออออออออออออออออออออออออออออออออออฮออออออออออออออออออออออออออออออออออออน
echo    บ  JD. Join Domain                  บ  DM. Domain Manage Tools           บ
echo    ศอออออออออออออออออออออออออออออออออออสออออออออออออออออออออออออออออออออออออผ
echo     B. Back to main menu
echo     E. Exit
echo.
goto ChoiceCBMC

:VSILStart
cls
call "%~dp0"\"Scripts"\"Logo.Bat"
echo                                 [  VSIL Menu  ]
echo    ษอออออออออออออออออออออออหอออออออออออออออออออออออหออออออออออออออออออออออออป
echo    บ    Primary Servers    บ    Backup Servers     บ        Clients         บ
echo    ฬอออออออออออออออออออออออฮอออออออออออออออออออออออฮออออออออออออออออออออออออน
echo    บ  1. VSIL CBMC 1       บ  2. VSIL CBMC 2       บ     6. Client 1        บ
echo    บ  3. DataBase 1        บ 21. Domain Control 2  บ     7. Client 2        บ
echo    บ                       บ     and SEP           บ     8. Client 3        บ
echo    บ                       บ                       บ     9. Client 4        บ
echo    บ                       บ                       บ    10. Client 5        บ
echo    ศอออออออออออออออออออออออสอออออออออออออออออออออออสออออออออออออออออออออออออผ
echo    ษอออออออออออออออออออออออออออออออออออหออออออออออออออออออออออออออออออออออออป
echo    บ           Tools                   บ  Domain Manage for VSIL            บ
echo    ฬอออออออออออออออออออออออออออออออออออฮออออออออออออออออออออออออออออออออออออน
echo    บ  JD. VSIL Join Domain             บ  DM. Domain Manage Tools           บ
echo    ศอออออออออออออออออออออออออออออออออออสออออออออออออออออออออออออออออออออออออผ
echo     B. Back to main menu
echo     E. Exit
echo.
goto ChoiceVSIL


:Choice
set IP=1
set /p Choice=Please Choose an Option: 
if '%Choice%'=='1' set SN=1&& goto BMCServer
if '%Choice%'=='2' set SN=2&& goto BMCServer
if '%Choice%'=='3' set SN=1&& goto DatabaseServer
if '%Choice%'=='4' set SN=2&& goto DatabaseServer
if '%Choice%'=='6' set SN=1&& goto Client
if '%Choice%'=='7' set SN=2&& goto Client
if '%Choice%'=='8' set SN=3&& goto Client
if '%Choice%'=='9' set SN=4&& goto Client
if '%Choice%'=='10' set SN=5&& goto Client
if '%Choice%'=='13' set SN=1&& goto ICSServer
if '%Choice%'=='14' set SN=2&& goto ICSServer
if '%Choice%'=='20' set SN=1&& goto DomainControl
if '%Choice%'=='21' set SN=2&& goto DomainControl
if '%Choice%'=='22' goto SEPServer
if /i '%Choice%'=='PT' goto PingTesting
if /i '%Choice%'=='CDB' goto CreateDB
if /i '%Choice%'=='JD' goto JoinDomain
if /i '%Choice%'=='DM' goto BMCDomainManage
if /i '%Choice%'=='B' cls&& goto logo
if /i '%Choice%'=='E' exit
if not '%Choice%'=='' ECHO "%Choice%" is not valid, please try again
goto Choice

:ChoiceCBMC
set IP=1
set /p Choice=Please Choose an Option: 
if '%Choice%'=='1' set SN=1&& goto CBMCServer
if '%Choice%'=='2' set SN=2&& goto CBMCServer
if '%Choice%'=='3' set SN=1&& goto CBMCDatabaseServer
if '%Choice%'=='4' set SN=2&& goto CBMCDatabaseServer
if '%Choice%'=='6' set SN=1&& goto CBMCClient
if '%Choice%'=='7' set SN=2&& goto CBMCClient
if '%Choice%'=='8' set SN=3&& goto CBMCClient
if '%Choice%'=='9' set SN=4&& goto CBMCClient
if '%Choice%'=='10' set SN=5&& goto CBMCClient
if '%Choice%'=='35' set SN=6&& goto CBMCClient
if '%Choice%'=='36' set SN=7&& goto CBMCClient
if '%Choice%'=='37' set SN=8&& goto CBMCClient
if '%Choice%'=='38' set SN=9&& goto CBMCClient
if '%Choice%'=='39' set SN=10&& goto CBMCClient
if '%Choice%'=='40' set SN=11&& goto CBMCClient
if '%Choice%'=='41' set SN=12&& goto CBMCClient
if '%Choice%'=='42' set SN=13&& goto CBMCClient
if '%Choice%'=='43' set SN=14&& goto CBMCClient
if '%Choice%'=='44' set SN=15&& goto CBMCClient
if '%Choice%'=='21' set SN=2&& goto CBMCDomainControl
if '%Choice%'=='22' goto CBMCSEPServer
if /i '%Choice%'=='PT' goto CBMCPingTesting
if /i '%Choice%'=='CDB' goto CBMCCreateDB
if /i '%Choice%'=='JD' goto CBMCJoinDomain
if /i '%Choice%'=='DM' goto CBMCDomainManage
if /i '%Choice%'=='B' cls&& goto logo
if /i '%Choice%'=='E' exit
if not '%Choice%'=='' ECHO "%Choice%" is not valid, please try again
goto ChoiceCBMC

:ChoiceVSIL
set IP=1
set /p Choice=Please Choose an Option: 
if '%Choice%'=='1' set SN=1&& goto VSILBMCServer
if '%Choice%'=='2' set SN=2&& goto VSILBMCServer
if '%Choice%'=='3' set SN=1&& goto VSILDatabaseServer
if '%Choice%'=='4' set SN=2&& goto VSILDatabaseServer
if '%Choice%'=='6' set SN=1&& goto VSILClient
if '%Choice%'=='7' set SN=2&& goto VSILClient
if '%Choice%'=='8' set SN=3&& goto VSILClient
if '%Choice%'=='9' set SN=4&& goto VSILClient
if '%Choice%'=='10' set SN=5&& goto VSILClient
if '%Choice%'=='21' set SN=2&& goto VSILDomainControl
if /i '%Choice%'=='CDB' goto VSILCreateDB
if /i '%Choice%'=='JD' goto VSILJoinDomain
if /i '%Choice%'=='DM' goto VSILDomainManage
if /i '%Choice%'=='B' cls&& goto logo
if /i '%Choice%'=='E' exit
if not '%Choice%'=='' ECHO "%Choice%" is not valid, please try again
goto ChoiceVSIL

rem ###### Client Configuration ######
:Client
set IP=%Choice%
Choice /C YN /M "Apply Configuration for Client %SN%, Are you sure?" 
goto Client_%ERRORLEVEL% 

:Client_1 
call "%~dp0"\"Scripts"\"ChangeLocalPassword.Bat"
call "%~dp0"\"Scripts"\"ChangeFirewallStatetoOFF.Bat"
call "%~dp0"\"Scripts"\"ChangeTimeZoneToSingapore.Bat"
call "%~dp0"\"Scripts"\"ChangeLogsSize.Bat"
call "%~dp0"\"Scripts"\"ChangePowerConfig.Bat"
call "%~dp0"\"Scripts"\"ChangeWallpaper.Bat"
call "%~dp0"\"Scripts"\"DisableCertificateRevocation.Bat"
call "%~dp0"\"Scripts"\"DisableRemoteAssistance.Bat"
call "%~dp0"\"Scripts"\"DisableSystemProtection.Bat"
call "%~dp0"\"Scripts"\"DisableWindowsUpdate.Bat"
call "%~dp0"\"Scripts"\"EnableWPFFontCache.Bat"
call "%~dp0"\"Scripts"\"DeleteClientAccount.Bat"
call "%~dp0"\"Scripts"\"ChangeComputerDescription.Bat"
call "%~dp0"\"Scripts"\"DisableClientFeatures.Bat"
call "%~dp0"\"Scripts"\"ChangeComputerName.Bat"
call "%~dp0"\"Scripts"\"NetworkConfig.Bat"
call "%~dp0"\"Scripts"\"AutoInstallClient.Bat"
shutdown.exe /r /t 20
goto Start

:Client_2
cls
goto Start
rem #### Client Configuration END ####



rem #### BMC Server Configuration ####
:BMCServer
set IP=%Choice%
Choice /C YN /M "Apply Configuration for BMC Server %SN%, Are you sure?"
goto BMCServer_%ERRORLEVEL% 

:BMCServer_1 
call "%~dp0"\"Scripts"\"ChangeLocalPassword.Bat"
call "%~dp0"\"Scripts"\"AllowRemoteDesktop.Bat"
call "%~dp0"\"Scripts"\"ChangeFirewallStatetoOFF.Bat"
call "%~dp0"\"Scripts"\"RouteAddOperationalServers.Bat"
call "%~dp0"\"Scripts"\"ChangeTimeZoneToUTC.Bat"
call "%~dp0"\"Scripts"\"DisableCertificateRevocation.Bat"
call "%~dp0"\"Scripts"\"DisableWindowsUpdate.Bat"
call "%~dp0"\"Scripts"\"ChangeComputerDescription.Bat"
call "%~dp0"\"Scripts"\"NetworkConfig.Bat"
call "%~dp0"\"Scripts"\"AutoInstallServerBMC.Bat"
call "%~dp0"\"Scripts"\"ChangeComputerName.Bat"
shutdown.exe /r /t 00
goto Start

:BMCServer_2
cls
goto Start
rem ##################### BMC Server Configuration END #####################



rem #### ICS Server Configuration ####
:ICSServer
set IP=%Choice%
Choice /C YN /M "Apply Configuration for ICS Server %SN%, Are you sure?"
goto ICSServer_%ERRORLEVEL% 

:ICSServer_1 
call "%~dp0"\"Scripts"\"ChangeLocalPassword.Bat"
call "%~dp0"\"Scripts"\"AllowRemoteDesktop.Bat"
call "%~dp0"\"Scripts"\"ChangeFirewallStatetoOFF.Bat"
call "%~dp0"\"Scripts"\"ChangeTimeZoneToUTC.Bat"
call "%~dp0"\"Scripts"\"DisableCertificateRevocation.Bat"
call "%~dp0"\"Scripts"\"DisableWindowsUpdate.Bat"
call "%~dp0"\"Scripts"\"ChangeComputerDescription.Bat"
call "%~dp0"\"Scripts"\"NetworkConfig.Bat"
call "%~dp0"\"Scripts"\"AutoInstallServerICS.Bat"
call "%~dp0"\"Scripts"\"ChangeComputerName.Bat"
shutdown.exe /r /t 00
goto Start

:ICSServer_2
cls
goto Start
rem ##################### ICS Server Configuration END #####################



rem #################### DataBase Server Configuration #####################
:DatabaseServer
set IP=%Choice%
Choice /C YN /M "Apply Configuration for Database Server %SN%, Are you sure?"
goto DatabaseServer_%ERRORLEVEL% 

:DatabaseServer_1 
call "%~dp0"\"Scripts"\"ChangeLocalPassword.Bat"
call "%~dp0"\"Scripts"\"AllowRemoteDesktop.Bat"
call "%~dp0"\"Scripts"\"ChangeFirewallStatetoOFF.Bat"
call "%~dp0"\"Scripts"\"RouteAddOperationalServers.Bat"
call "%~dp0"\"Scripts"\"ChangeTimeZoneToUTC.Bat"
call "%~dp0"\"Scripts"\"DisableCertificateRevocation.Bat"
call "%~dp0"\"Scripts"\"DisableWindowsUpdate.Bat"
call "%~dp0"\"Scripts"\"ChangeComputerDescription.Bat"
call "%~dp0"\"Scripts"\"NetworkConfig.Bat"
call "%~dp0"\"Scripts"\"AutoInstallServerDB.Bat"
call "%~dp0"\"Scripts"\"ChangeComputerName.Bat"
call "%~dp0"\"Scripts"\"UpdateDBCName.Bat"
shutdown.exe /r /t 00
goto Start

:DatabaseServer_2
cls
goto Start
rem ################## DataBase Server Configuration END ###################



rem ################# Domain Control Server Configuration ##################
:DomainControl
set IP=%Choice%
Choice /C YN /M "Apply Configuration for Domain Control Server %SN%, Are you sure?"
goto DomainControl_%ERRORLEVEL% 

:DomainControl_1 
call "%~dp0"\"Scripts"\"ChangeLocalPassword.Bat"
rem call "%~dp0"\"Scripts"\"EnableAdministratorPasswordREQ.Bat"
call "%~dp0"\"Scripts"\"AllowRemoteDesktop.Bat"
call "%~dp0"\"Scripts"\"ChangeFirewallStatetoOFF.Bat"
call "%~dp0"\"Scripts"\"RouteAddSeurityServers.Bat"
call "%~dp0"\"Scripts"\"ChangeTimeZoneToUTC.Bat"
call "%~dp0"\"Scripts"\"DisableCertificateRevocation.Bat"
call "%~dp0"\"Scripts"\"DisableWindowsUpdate.Bat"
call "%~dp0"\"Scripts"\"ChangeComputerDescription.Bat"
call "%~dp0"\"Scripts"\"NetworkConfig.Bat"
call "%~dp0"\"Scripts"\"AutoInstallServerDC.Bat"
call "%~dp0"\"Scripts"\"ChangeComputerName.Bat"
shutdown.exe /r /t 00
goto Start

:DomainControl_2
cls
goto Start
rem ################ Domain Control Server Configuration END ###############



rem #### SEP Server Configuration ####
:SEPServer
set IP=%Choice%
Choice /C YN /M "Apply Configuration for SEP Server, Are you sure?"
goto SEPServer_%ERRORLEVEL% 

:SEPServer_1 
call "%~dp0"\"Scripts"\"ChangeLocalPassword.Bat"
call "%~dp0"\"Scripts"\"AllowRemoteDesktop.Bat"
call "%~dp0"\"Scripts"\"ChangeFirewallStatetoOFF.Bat"
call "%~dp0"\"Scripts"\"RouteAddSeurityServers.Bat"
call "%~dp0"\"Scripts"\"ChangeTimeZoneToUTC.Bat"
call "%~dp0"\"Scripts"\"DisableCertificateRevocation.Bat"
call "%~dp0"\"Scripts"\"DisableWindowsUpdate.Bat"
call "%~dp0"\"Scripts"\"ChangeComputerDescription.Bat"
call "%~dp0"\"Scripts"\"NetworkConfig.Bat"
call "%~dp0"\"Scripts"\"AutoInstallServerSEC.Bat"
call "%~dp0"\"Scripts"\"ChangeComputerName.Bat"
shutdown.exe /r /t 00
goto Start

:SEPServer_2
cls
goto Start
rem ##################### SEP Server Configuration END #####################



rem ########## Join Domain ###########
:JoinDomain
call "%~dp0"\"Scripts"\"JoinDomain.Bat"
goto Start
rem ######## Join Domain END #########



rem ########### Ping Testing ###########
:PingTesting
call "%~dp0"\"Scripts"\"Pinger.Bat"
goto Start
rem ######### Ping Testing END #########



rem ########### Create Database ###########
:CreateDB
Choice /C YN /M "Create Databases for Battery %Batt%?"
goto CreateDB_%ERRORLEVEL% 
:CreateDB_1
call "%~dp0"\"Scripts"\"CreateDatabase.Bat"
:CreateDB_2
cls
goto Start
rem ######### Create Database END #########



rem ########### BMC Domain Manage ###########
:BMCDomainManage
call "%~dp0"\"Scripts"\"BMCDomainManage.Bat"
goto Start
rem ######### BMC Domain Manage END #########



rem ############## CBMC ############## CBMC ############## CBMC ############## CBMC ############## CBMC ############## CBMC ##############
rem ############## CBMC ############## CBMC ############## CBMC ############## CBMC ############## CBMC ############## CBMC ##############
rem ############## CBMC ############## CBMC ############## CBMC ############## CBMC ############## CBMC ############## CBMC ##############
rem ############## CBMC ############## CBMC ############## CBMC ############## CBMC ############## CBMC ############## CBMC ##############
rem ############## CBMC ############## CBMC ############## CBMC ############## CBMC ############## CBMC ############## CBMC ##############


rem ###### CBMC Client Configuration ######
:CBMCClient
set IP=%Choice%
Choice /C YN /M "Apply Configuration for CBMC Client %SN%, Are you sure?" 
goto CBMCClient_%ERRORLEVEL% 

:CBMCClient_1
call "%~dp0"\"Scripts"\"CBMCChangeLocalPassword.Bat"
call "%~dp0"\"Scripts"\"ChangeFirewallStatetoOFF.Bat"
call "%~dp0"\"Scripts"\"ChangeTimeZoneToSingapore.Bat"
call "%~dp0"\"Scripts"\"ChangeLogsSize.Bat"
call "%~dp0"\"Scripts"\"ChangePowerConfig.Bat"
call "%~dp0"\"Scripts"\"ChangeWallpaper.Bat"
call "%~dp0"\"Scripts"\"DisableCertificateRevocation.Bat"
call "%~dp0"\"Scripts"\"DisableRemoteAssistance.Bat"
call "%~dp0"\"Scripts"\"DisableSystemProtection.Bat"
call "%~dp0"\"Scripts"\"DisableWindowsUpdate.Bat"
call "%~dp0"\"Scripts"\"EnableWPFFontCache.Bat"
call "%~dp0"\"Scripts"\"DeleteClientAccount.Bat"
call "%~dp0"\"Scripts"\"CBMCChangeComputerDescription.Bat"
call "%~dp0"\"Scripts"\"CBMCDisableClientFeatures.Bat"
call "%~dp0"\"Scripts"\"CBMCChangeComputerName.Bat"
call "%~dp0"\"Scripts"\"CBMCNetworkConfig.Bat"
call "%~dp0"\"Scripts"\"AutoInstallClient.Bat"
shutdown.exe /r /t 20
goto:CStart 

:CBMCClient_2
cls
goto CStart
rem #### CBMC Client Configuration END ####



rem #### CBMC Server Configuration ####
:CBMCServer
set IP=%Choice%
Choice /C YN /M "Apply Configuration for CBMC Server %SN%, Are you sure?"
goto CBMCServer_%ERRORLEVEL% 

:CBMCServer_1 
call "%~dp0"\"Scripts"\"CBMCChangeLocalPassword.Bat"
call "%~dp0"\"Scripts"\"AllowRemoteDesktop.Bat"
call "%~dp0"\"Scripts"\"ChangeFirewallStatetoOFF.Bat"
call "%~dp0"\"Scripts"\"ChangeTimeZoneToUTC.Bat"
call "%~dp0"\"Scripts"\"DisableCertificateRevocation.Bat"
call "%~dp0"\"Scripts"\"DisableWindowsUpdate.Bat"
call "%~dp0"\"Scripts"\"CBMCChangeComputerDescription.Bat"
call "%~dp0"\"Scripts"\"CBMCNetworkConfig.Bat"
call "%~dp0"\"Scripts"\"CBMCRouteAddOperationalServers.Bat"
call "%~dp0"\"Scripts"\"AutoInstallServerCBMC.Bat"
call "%~dp0"\"Scripts"\"CBMCChangeComputerName.Bat"
shutdown.exe /r /t 00
goto:CStart 

:CBMCServer_2
cls
goto CStart
rem ##################### CBMC Server Configuration END #####################



rem #################### CBMC DataBase Server Configuration #####################
:CBMCDatabaseServer
set IP=%Choice%
Choice /C YN /M "Apply Configuration for CBMC Database Server %SN%, Are you sure?"
goto CBMCDatabaseServer_%ERRORLEVEL% 

:CBMCDatabaseServer_1 
call "%~dp0"\"Scripts"\"CBMCChangeLocalPassword.Bat"
call "%~dp0"\"Scripts"\"AllowRemoteDesktop.Bat"
call "%~dp0"\"Scripts"\"ChangeFirewallStatetoOFF.Bat"
call "%~dp0"\"Scripts"\"ChangeTimeZoneToUTC.Bat"
call "%~dp0"\"Scripts"\"DisableCertificateRevocation.Bat"
call "%~dp0"\"Scripts"\"DisableWindowsUpdate.Bat"
call "%~dp0"\"Scripts"\"CBMCChangeComputerDescription.Bat"
call "%~dp0"\"Scripts"\"CBMCNetworkConfig.Bat"
call "%~dp0"\"Scripts"\"AutoInstallServerCBMCDB.Bat"
call "%~dp0"\"Scripts"\"CBMCChangeComputerName.Bat"
call "%~dp0"\"Scripts"\"UpdateDBCName.Bat"
shutdown.exe /r /t 00
goto:CStart 

:CBMCDatabaseServer_2
cls
goto CStart
rem ################## CBMC DataBase Server Configuration END ###################



rem ################# CBMC Domain Control Server Configuration ##################
:CBMCDomainControl
set IP=%Choice%
Choice /C YN /M "Apply Configuration for CBMC Domain Control Server %SN%, Are you sure?"
goto CBMCDomainControl_%ERRORLEVEL% 

:CBMCDomainControl_1 
call "%~dp0"\"Scripts"\"CBMCChangeLocalPassword.Bat"
rem call "%~dp0"\"Scripts"\"EnableAdministratorPasswordREQ.Bat"
call "%~dp0"\"Scripts"\"AllowRemoteDesktop.Bat"
call "%~dp0"\"Scripts"\"ChangeFirewallStatetoOFF.Bat"
call "%~dp0"\"Scripts"\"ChangeTimeZoneToUTC.Bat"
call "%~dp0"\"Scripts"\"DisableCertificateRevocation.Bat"
call "%~dp0"\"Scripts"\"DisableWindowsUpdate.Bat"
call "%~dp0"\"Scripts"\"CBMCChangeComputerDescription.Bat"
call "%~dp0"\"Scripts"\"CBMCNetworkConfig.Bat"
call "%~dp0"\"Scripts"\"AutoInstallServerCBMCDC.Bat"
call "%~dp0"\"Scripts"\"CBMCChangeComputerName.Bat"
shutdown.exe /r /t 00
goto:CStart 

:CBMCDomainControl_2
cls
goto CStart
rem ################ CBMC Domain Control Server Configuration END ###############



rem #### CBMC SEP Server Configuration ####
:CBMCSEPServer
set IP=%Choice%
Choice /C YN /M "Apply Configuration for CBMC SEP Server, Are you sure?"
goto CBMCSEPServer_%ERRORLEVEL% 

:CBMCSEPServer_1 
call "%~dp0"\"Scripts"\"CBMCChangeLocalPassword.Bat"
call "%~dp0"\"Scripts"\"AllowRemoteDesktop.Bat"
call "%~dp0"\"Scripts"\"ChangeFirewallStatetoOFF.Bat"
call "%~dp0"\"Scripts"\"ChangeTimeZoneToUTC.Bat"
call "%~dp0"\"Scripts"\"DisableCertificateRevocation.Bat"
call "%~dp0"\"Scripts"\"DisableWindowsUpdate.Bat"
call "%~dp0"\"Scripts"\"CBMCChangeComputerDescription.Bat"
call "%~dp0"\"Scripts"\"CBMCNetworkConfig.Bat"
call "%~dp0"\"Scripts"\"AutoInstallServerSEC.Bat"
call "%~dp0"\"Scripts"\"CBMCChangeComputerName.Bat"
shutdown.exe /r /t 00
goto:CStart 

:CBMCSEPServer_2
cls
goto CStart
rem ##################### CBMC SEP Server Configuration END #####################



rem ########## CBMC Join Domain ###########
:CBMCJoinDomain
call "%~dp0"\"Scripts"\"CBMCJoinDomain.Bat"
goto CStart
rem ######## CBMC Join Domain END #########


rem ########### CBMC Ping Testing ###########
:CBMCPingTesting
call "%~dp0"\"Scripts"\"CBMCPinger.Bat"
goto CStart
rem ######### CBMC Ping Testing END #########


rem ########### CBMC Create Database ###########
:CBMCCreateDB
Choice /C YN /M "Create Databases for CBMC?"
goto CBMCCreateDB_%ERRORLEVEL% 
:CBMCCreateDB_1
call "%~dp0"\"Scripts"\"CBMCCreateDatabase.Bat"

:CBMCCreateDB_2
cls
goto CStart
rem ######### CBMC Create Database END #########


rem ########### CBMC Domain Manage ###########
:CBMCDomainManage
call "%~dp0"\"Scripts"\"CBMCDomainManage.Bat"
goto CStart
rem ######### CBMC Domain Manage END #########


rem ####################### END CBMC #####################

pause
:UserError
pause
exit