#
# Windows PowerShell script for AD DS Deployment
#
$domainname = Read-Host -Prompt "Enter the full domain name(including TLD - .com\.local\etc): "
$netbiosname = Read-Host -Prompt "Enter your Net Bios name (just the domain name with no TLD or any dots): "

Import-Module ADDSDeployment
Install-ADDSForest `
-CreateDnsDelegation:$false `
-DatabasePath "C:\Windows\NTDS" `
-DomainMode "WinThreshold" `
-DomainName $domainname `
-DomainNetbiosName $netbiosname.ToUpper() `
-ForestMode "WinThreshold" `
-InstallDns:$true `
-LogPath "C:\Windows\NTDS" `
-NoRebootOnCompletion:$false `
-SysvolPath "C:\Windows\SYSVOL" `
-Force:$true

