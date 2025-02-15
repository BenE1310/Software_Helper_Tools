# CA Installation
Install-WindowsFeature -Name ADCS-Cert-Authority -IncludeManagementTools

# CA Configuration
Install-AdcsCertificationAuthority `
-CAType EnterpriseRootCA `
-CryptoProviderName "RSA#Microsoft Software Storage Provider" `
-HashAlgorithmName SHA256 `
-KeyLength 2048 `
-ValidityPeriod Years `
-ValidityPeriodUnits 5 `
-Force 