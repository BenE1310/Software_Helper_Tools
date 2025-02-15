cd $PSScriptRoot
$location = Get-Location
$policyPath = "$location\GPO"

$policyList = "BMC Operational Users Policy",
"BMC Technical Users Policy",
"Certificate Enrollment Policy",
"Screen Saver Policy",
"Windows 10 Administrative Templates Policy",
"Windows 10 Audit Policy",
"Windows 10 Components Policy",
"Windows 10 Local Policy",
"Windows 10 Services Policy",
"Windows 2019 Administrative Templates Policy",
"Windows 2019 Audit Policy",
"Windows 2019 Components Policy",
"Windows 2019 Domain Controller Administrative Templates Policy",
"Windows 2019 Domain Controller Windows Components Policy",
"Windows 2019 Local Policy",
"Windows 2019 Servers Policy",
"Windows 2019 Services Policy",
"Windows EAP Policy",
"Windows Firewall Policy",
"Windows LAPS Policy",
"Windows Policy Password",
"Windows RDP Certificate Policy",
"Disable Auto lock Screen Policy",
"Windows BitLocker Policy",
"DC Local Policy",
"VM VBS Policy",


foreach ($item in $policyList) {
    Import-GPO -BackupGpoName $item -Path $policyPath -Targetname $item
}

