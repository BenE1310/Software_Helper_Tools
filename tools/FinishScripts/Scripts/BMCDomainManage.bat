@echo off
:DStart
cls
call "%~dp0"\"logo.Bat"
echo                                [  Battery %Batt% ]
echo            ษออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
echo            บ                BMC Domain Manage Tools                 บ
echo            ฬออออออออออออออออออออออออออออออออออออออออออออออออออออออออน
echo            บ  CSD. Create Secondary Domain                          บ
echo            บ  COU. Create Organizational Units                      บ
echo            บ  CGP. Create Group Policy                              บ
echo            บ  IGP. Import Group Policy                              บ
echo            บ ------------------------------------------------------ บ
echo            บ    M. Main Menu                                        บ
echo            ศออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
echo.
set /p Choice=Please Choose an Option: 
if /i '%Choice%'=='CSD' set SN=2&& goto CreateSecondaryDomain
if /i '%Choice%'=='COU' goto CreateOrganizationalUnits
if /i '%Choice%'=='CGP' goto CreateGroupPolicy
if /i '%Choice%'=='IGP' goto ImportGroupPolicy
if /i '%Choice%'=='M' GOTO:eof


rem ######### CreateSecondaryDomain ##########
:CreateSecondaryDomain
Choice /C YN /M "Create Secondary Domain for battery %Batt%"
goto CreateSecondaryDomain_%ERRORLEVEL% 
:CreateSecondaryDomain_1
call "%~dp0"\"CreateSecondaryDomain.Bat"
:CreateSecondaryDomain_2
goto DStart
rem ####### CreateSecondaryDomain END ########


rem ######### CreateOrganizationalUnits ##########
:CreateOrganizationalUnits
Choice /C YN /M "Create OU's for battery %Batt%"
goto CreateOrganizationalUnits_%ERRORLEVEL% 
:CreateOrganizationalUnits_1
call "%~dp0"\"CreateOrganizationalUnits.Bat"
:CreateOrganizationalUnits_2
goto DStart
rem ####### CreateOrganizationalUnits END ########


rem ######### CreateGroupPolicy ##########
:CreateGroupPolicy
Choice /C YN /M "Create Group Policy for battery %Batt%"
goto CreateGroupPolicy_%ERRORLEVEL% 
:CreateGroupPolicy_1
call "%~dp0"\"CreateGroupPolicy.Bat"
:CreateGroupPolicy_2
goto DStart
rem ######### END CreateGroupPolicy ##########


rem ########### Import Group Policy ###########
:ImportGroupPolicy
echo.
echo This tool will pull the information from the following path: C:\GPO
echo Make sure FB%Batt%Migration.Migtable in this particular directory
echo.
Choice /C YN /M "Import Group Policy for Battery %Batt%?"
goto ImportGroupPolicy_%ERRORLEVEL% 
:ImportGroupPolicy_1
call "%~dp0"\"ImportGPO.Bat"

:ImportGroupPolicy_2
cls
goto DStart
rem ######### Import Group Policy END #########



pause