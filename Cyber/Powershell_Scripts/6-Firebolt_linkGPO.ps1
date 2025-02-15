
#first, you need to put the policies in the path : C:\GPO


# $DomainName = Read-Host -Prompt "Enter the domain name: "
$DomainName = $env:USERDOMAIN

#List of Targets
$fireboltMain = "dc=$DomainName,dc=local"
$Domain_Controllers = "OU=Domain Controllers,dc=$DomainName,dc=local"
$Windows_2019_Servers = "OU=Windows Server 2019,OU=Firebolt Computers,DC=$DomainName,DC=local"
$Windows_10_Clients = "OU=Windows 10,OU=Firebolt Computers,DC=$DomainName,DC=local"
$FireboltComputers = "OU=Firebolt Computers,dc=$DomainName,dc=local"
$BMC_Operational_Users = "OU=Operational Users,OU=Firebolt Users,DC=$DomainName,DC=local"
$BMC_Technical_Users = "OU=Technical Users,OU=Firebolt Users,DC=$DomainName,DC=local"


#Domain Controllers
New-GPLink -Name "Windows 2019 Domain Controller Windows Components Policy" -Target $Domain_Controllers -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows 2019 Domain Controller Administrative Templates Policy" -Target $Domain_Controllers -LinkEnabled Yes -Enforced No

#Firebolt Computers
New-GPLink -Name "Certificate Enrollment Policy" -Target $FireboltComputers -LinkEnabled Yes -Enforced No
New-GPLink -Name "LAPS Installation Policy" -Target $FireboltComputers -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows LAPS Policy" -Target $FireboltComputers -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows RDP Certificate Policy" -Target $FireboltComputers -LinkEnabled Yes -Enforced No

#Windows Server 2019
New-GPLink -Name "Windows 2019 Local Policy" -Target $Windows_2019_Servers -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows 2019 Audit Policy" -Target $Windows_2019_Servers -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows 2019 Servers Policy" -Target $Windows_2019_Servers -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows 2019 Components Policy" -Target $Windows_2019_Servers -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows 2019 Administrative Templates Policy" -Target $Windows_2019_Servers -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows 2019 Services Policy" -Target $Windows_2019_Servers -LinkEnabled Yes -Enforced No
# New-GPLink -Name "Windows EAP Policy" -Target $Windows_2019_Servers -LinkEnabled Yes -Enforced No

#Windows 10 Clients
New-GPLink -Name "Windows 10 Audit Policy" -Target $Windows_10_Clients -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows 10 Local Policy" -Target $Windows_10_Clients -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows 10 Services Policy" -Target $Windows_10_Clients -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows 10 Components Policy" -Target $Windows_10_Clients -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows 10 Administrative Templates Policy" -Target $Windows_10_Clients -LinkEnabled Yes -Enforced No
# New-GPLink -Name "Windows EAP Policy" -Target $Windows_10_Clients -LinkEnabled Yes -Enforced No
# New-GPLink -Name "Windows 10 Disable Auto Lock Screen Policy" -Target $Windows_10_Clients -LinkEnabled Yes -Enforced No



#BMC Users
New-GPLink -Name "BMC Technical Users Policy" -Target $BMC_Technical_Users -LinkEnabled Yes -Enforced No
New-GPLink -Name "BMC Operational Users Policy" -Target $BMC_Operational_Users -LinkEnabled Yes -Enforced No

#Firebolt main
New-GPLink -Name "Windows Policy Password" -Target $fireboltMain -LinkEnabled Yes -Enforced No
New-GPLink -Name "Windows Firewall Policy" -Target $fireboltMain -LinkEnabled Yes -Enforced No
