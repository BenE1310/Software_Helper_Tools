#Set battery number
# $DomainName = Read-Host -Prompt "Enter the domain name: "
$DomainName = $env:USERDOMAIN

#Firebolt Computers OU
New-ADOrganizationalUnit -Name "Firebolt Computers" -Path "DC=$DomainName,DC=local" -ProtectedFromAccidentalDeletion $false
#Firebolt Users OU
New-ADOrganizationalUnit -Name "Firebolt Users" -Path "DC=$DomainName,DC=local" -ProtectedFromAccidentalDeletion $false

#Servers OU
New-ADOrganizationalUnit -Name "Windows Server 2019" -Path "OU=Firebolt Computers,DC=$DomainName,DC=local" -ProtectedFromAccidentalDeletion $false
#Client OU
New-ADOrganizationalUnit -Name "Windows 10" -Path "OU=Firebolt Computers,DC=$DomainName,DC=local" -ProtectedFromAccidentalDeletion $false

# Operational Servers OU
New-ADOrganizationalUnit -Name "Operational Servers" -Path "OU=Windows Server 2019, OU=Firebolt Computers,DC=$DomainName,DC=local" -ProtectedFromAccidentalDeletion $false
# Security Servers OU
New-ADOrganizationalUnit -Name "Security Servers" -Path "OU=Windows Server 2019, OU=Firebolt Computers,DC=$DomainName,DC=local" -ProtectedFromAccidentalDeletion $false

# Operational Users OU
New-ADOrganizationalUnit -Name "Operational Users" -Path "OU=Firebolt Users,DC=$DomainName,DC=local" -ProtectedFromAccidentalDeletion $false
# Technical Users OU
New-ADOrganizationalUnit -Name "Technical Users" -Path "OU=Firebolt Users,DC=$DomainName,DC=local" -ProtectedFromAccidentalDeletion $false



###Create Users and Groups###

#Operationl Users
New-ADGroup -Name "BMC Operators" -SamAccountName "BMC Operators" -GroupCategory Security -GroupScope Global -DisplayName "BMC Operators" -Path "OU=Operational Users,OU=Firebolt Users,DC=$DomainName,DC=local" -Description "Members of this group are BMC Operators"
#New-ADGroup -Name "Managed Users" -SamAccountName "Managed Users" -GroupCategory Security -GroupScope Global -DisplayName "managed Users" -Path "OU=Operational Users,OU=Firebolt Users,DC=$DomainName,DC=local" -Description "Members of this group can be unlocked and password reset"
New-ADUser -UserPrincipalName ICP1@$DomainName.local -Name ICP1 -Enabled $true -AccountPassword (ConvertTo-SecureString -AsPlainText "Q1w2e3r4" -Force) -ChangePasswordAtLogon $false -PasswordNeverExpires $true -Path "OU=Operational Users,OU=Firebolt Users,DC=$DomainName,DC=local"
New-ADUser -UserPrincipalName ICP2@$DomainName.local -Name ICP2 -Enabled $true -AccountPassword (ConvertTo-SecureString -AsPlainText "Q1w2e3r4" -Force) -ChangePasswordAtLogon $false -PasswordNeverExpires $true -Path "OU=Operational Users,OU=Firebolt Users,DC=$DomainName,DC=local"
New-ADUser -UserPrincipalName ICP3@$DomainName.local -Name ICP3 -Enabled $true -AccountPassword (ConvertTo-SecureString -AsPlainText "Q1w2e3r4" -Force) -ChangePasswordAtLogon $false -PasswordNeverExpires $true -Path "OU=Operational Users,OU=Firebolt Users,DC=$DomainName,DC=local"
New-ADUser -UserPrincipalName ICP4@$DomainName.local -Name ICP4 -Enabled $true -AccountPassword (ConvertTo-SecureString -AsPlainText "Q1w2e3r4" -Force) -ChangePasswordAtLogon $false -PasswordNeverExpires $true -Path "OU=Operational Users,OU=Firebolt Users,DC=$DomainName,DC=local"
New-ADUser -UserPrincipalName Commander@$DomainName.local -Name Commander -Enabled $true -AccountPassword (ConvertTo-SecureString -AsPlainText "Q1w2e3r4" -Force) -ChangePasswordAtLogon $false -PasswordNeverExpires $true -Path "OU=Operational Users,OU=Firebolt Users,DC=$DomainName,DC=local"

Add-ADGroupMember -Identity "BMC Operators" -Members @("ICP1","ICP2","ICP3","ICP4","Commander")

#FBTech 
New-ADGroup -Name "BMC Maintenance" -SamAccountName "BMC Maintenance" -GroupCategory Security -GroupScope Global -DisplayName "BMC Maintenance" -Path "OU=Maintenance Users,OU=Firebolt Users,DC=$DomainName,DC=local" -Description "Members of this group are BMC Technical"
New-ADGroup -Name "Delegated Users" -SamAccountName "Delegated Users" -GroupCategory Security -GroupScope Global -DisplayName "Delegated Users" -Path "OU=Technical Users,OU=Firebolt Users,DC=$DomainName,DC=local" -Description "Members of this group are authorized to perform user management tasks"
New-ADUser -UserPrincipalName FBTech@$DomainName.local -Name FBTech -Enabled $true -AccountPassword (ConvertTo-SecureString -AsPlainText "Q1w2e3r4" -Force) -ChangePasswordAtLogon $false -PasswordNeverExpires $true -Path "OU=Technical Users,OU=Firebolt Users,DC=$DomainName,DC=local"
Add-ADGroupMember -Identity "BMC Maintenance" -Members @("FBTech")
Add-ADGroupMember -Identity "Domain Admins" -Members @("FBTech")
Add-ADGroupMember -Identity "Administrators" -Members @("FBTech")
Add-ADGroupMember -Identity "Enterprise Admins" -Members @("FBTech")
Add-ADGroupMember -Identity "Group Policy Creator Owners" -Members @("FBTech")
Add-ADGroupMember -Identity "Schema Admins" -Members @("FBTech")


#NetAdmin User
New-ADGroup -Name "Network admins" -SamAccountName "Network admins" -GroupCategory Security -GroupScope Global -DisplayName "Network admins" -Path "OU=Technical Users,OU=Firebolt Users,DC=$DomainName,DC=local" -Description "Network administrators for network devices login"
New-ADUser -UserPrincipalName NetAdmin@$DomainName.local -Name NetAdmin -Enabled $true -AccountPassword (ConvertTo-SecureString -AsPlainText "Q1w2e3r4" -Force) -ChangePasswordAtLogon $false -PasswordNeverExpires $true -Path "OU=Technical Users,OU=Firebolt Users,DC=$DomainName,DC=local"
Add-ADGroupMember -Identity "Network admins" -Members @("Netadmin")

