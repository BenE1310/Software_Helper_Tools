# Instaal Radius 
Install-WindowsFeature NPAS -IncludeManagementTools

# Configure Environment

$battnum = Read-Host -Prompt  "Enter battery number (1,2,3,4,21)" 
$Mode = Read-Host -Prompt "Is this VSIL\CIWS battery? (Yes\No)"

# Import NPS Policies

Import-NpsConfiguration -Path "C:\Temp\$battnum.xml"

# Script Var

$sharesec = "Q1w2e3r4"
$vendor = "Cisco"
$adminadd = "10.11.13.254"
$adminp2p = "3.3.3.1"
$corebmcadd = "3.3.3.2"
$bmcadd = "10.11.18.254"
$bmcp2padd = "1.1.1.2"
$icsadd = "10.12.18.254"
$icsp2padd = "2.2.2.1"
$cbmcadd = "10.11.218.254"

# CBMC VSIL\CIWS 

if ($battnum -eq "21" -and $Mode -eq "Yes") {
   Write-Output "Configure NPS for VSIL\CIWS CBMC, Please wait for completion"

   # CBMC Switch Client (VSIL)
   New-NpsRadiusClient `
      -Name "CBMC*" `
      -Address = "$cbmcadd" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"
   
   # CBMC P2P Client (VSIL)
   New-NpsRadiusClient `
      -Name "CBMC_*" `
      -Address "4.4.4.1" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor" 

    # Core CBMC Client (VSIL)
    New-NpsRadiusClient `
       -Name "Core*" `
       -Address "4.4.4.2" `
       -AuthAttributeRequired $false `
       -SharedSecret "$sharesec" `
       -VendorName "$vendor"

# CBMC Operational Configuration

} elseif ($battnum -eq "21" -and $Mode -eq "No") {
   Write-Output "Configure NPS for operational CBMC, Please wait for completion."

   # CBMC Switch Client (Operational)
   New-NpsRadiusClient `
      -Name "CBMC*" `
      -Address = "$cbmcadd" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"

# Battery1 Operational Configuration

} elseif ($battnum -eq "1" -and $Mode -eq "Yes") {
   Write-Output "Configure NPS for Batter 1"
   
   # BMC1 Configuration (Operational)
   New-NpsRadiusClient `
      -Name "BMC*" `
      -Address "10.11.18.254" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"
 
   # ICS1 Configuration (Operational)
   New-NpsRadiusClient `
      -Name "ICS*" `
      -Address "10.12.18.254" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor" 

# Batter2 Operational Configuration

} elseif ($battnum -eq "2" -and $Mode -eq "No") {
   Write-Output "Configure NPS for Batter 2"

   # BMC2 Configuration (Operational)
   New-NpsRadiusClient `
      -Name "BMC*" `
      -Address "10.11.28.254" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"
   
   # ICS2 Configuration (Operational)
   New-NpsRadiusClient `
      -Name "ICS*" `
      -Address "10.12.28.254" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"

# Battery3 operational configuration

} elseif ($battnum -eq "3" -and $Mode -eq "No") {
   Write-Output "Configure NPS for Batter 3"

   # BMC3 Configuration (Operational)
   New-NpsRadiusClient `
      -Name "BMC*" `
      -Address "10.11.38.254" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"

   # ICS3 Configuration (Operational)
   New-NpsRadiusClient `
      -Name "ICS*" `
      -Address "10.12.28.254" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"

# Battery4 operational configuration

} elseif ($battnum -eq "4" -and $Mode -eq "No") {
    Write-Output "Configure NPS for Batter 4"

    # BMC4 Configuration (Operational)
    New-NpsRadiusClient `
      -Name "BMC*" `
      -Address "10.11.48.254" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"

    # ICS4 Configuration (Operational)
    New-NpsRadiusClient `
      -Name "ICS*" `
      -Address "10.12.28.254" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"

# VSIL batteries Configuration

} elseif ($battnum -ne "21" -and $Mode -eq "Yes") {
   Write-Output "Configure NPS for VSIL batteries"

   # BMC Switch client (VSIL)
   New-NpsRadiusClient `
      -Name "BMC*" `
      -Address "$bmcadd" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor" `
  
   # BMC P2P client (VSIL)
   New-NpsRadiusClient `
      -Name "BMC_*" `
      -Address "$bmcp2padd" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"
      
   # ICS Switch Client (VSIL)
   New-NpsRadiusClient `
      -Name "ICS*" `
      -Address "10.12.18.254" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"
    
   # ICS P2P client (VSIL)
   New-NpsRadiusClient `
      -Name "ICS_*" `
      -Address "$icsp2padd" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"
      
   # Admin Switch client (VSIL)
   New-NpsRadiusClient `
      -Name "Admin*" `
      -Address "$adminadd" `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor" 

   # Admin P2P client (VSIL)
   New-NpsRadiusClient `
      -Name "Admin_*" `
      -Address "$adminp2p" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"

   # Core Switch Client (VSIL)
   New-NpsRadiusClient `
      -Name "Core*" `
      -Address "$corebmcadd" `
      -AuthAttributeRequired $false `
      -SharedSecret "$sharesec" `
      -VendorName "$vendor"
}
        
      