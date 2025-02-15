@echo off
:DCStart
cls
call "%~dp0"\"logo.Bat"
echo                                 [  CBMC %CBMCnum% ]
echo            ษออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
echo            บ               CBMC Domain Manage Tools                 บ
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
if /i '%Choice%'=='CSD' set SN=2&& goto CBMCCreateSecondaryDomain
if /i '%Choice%'=='COU' goto CBMCCreateOrganizationalUnits
if /i '%Choice%'=='CGP' goto CBMCCreateGroupPolicy
if /i '%Choice%'=='IGP' goto CBMCImportGroupPolicy
if /i '%Choice%'=='M' GOTO:eof


rem ######### CBMC CreateSecondaryDomain ##########
:CBMCCreateSecondaryDomain
Choice /C YN /M "Create Secondary Domain for CBMC %Batt%"
goto CBMCCreateSecondaryDomain_%ERRORLEVEL% 
:CBMCCreateSecondaryDomain_1
call "%~dp0"\"CBMCCreateSecondaryDomain.Bat"
:CBMCCreateSecondaryDomain_2
goto DCStart
rem ####### CBMC CreateSecondaryDomain END ########


rem ######### CBMC CreateOrganizationalUnits ##########
:CBMCCreateOrganizationalUnits
Choice /C YN /M "Create OU's for CBMC %Batt%"
goto CBMCCreateOrganizationalUnits_%ERRORLEVEL% 
:CBMCCreateOrganizationalUnits_1
call "%~dp0"\"CBMCCreateOrganizationalUnits.Bat"
:CBMCCreateOrganizationalUnits_2
goto DCStart
rem ####### CBMC CreateOrganizationalUnits END ########


rem ######### CBMC CreateGroupPolicy ##########
:CBMCCreateGroupPolicy
Choice /C YN /M "Create Group Policy for CBMC %Batt%"
goto CBMCCreateGroupPolicy_%ERRORLEVEL% 
:CBMCCreateGroupPolicy_1
call "%~dp0"\"CBMCCreateGroupPolicy.Bat"
:CBMCCreateGroupPolicy_2
goto DCStart
rem ######### END CBMC CreateGroupPolicy ##########


rem ########### CBMC Import Group Policy ###########
:CBMCImportGroupPolicy
echo.
echo This tool will pull the information from the following path: C:\GPO
echo Make sure FB%Batt%Migration.Migtable in this particular directory
echo.
Choice /C YN /M "Import Group Policy for CBMC %Batt%?"
goto CBMCImportGroupPolicy_%ERRORLEVEL% 
:CBMCImportGroupPolicy_1
call "%~dp0"\"ImportGPO.Bat"

:CBMCImportGroupPolicy_2
cls
goto DCStart
rem ######### CBMC Import Group Policy END #########



pause