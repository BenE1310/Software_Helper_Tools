Import-Module ServerManager

Install-WindowsFeature -Name AD-Domain-Services -IncludeAllSubFeature
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools
