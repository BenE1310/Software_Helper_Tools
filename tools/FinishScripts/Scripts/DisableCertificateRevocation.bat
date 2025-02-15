@echo off
echo Disable Certificate Revocation
Reg Add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\WinTrust\Trust Providers\Software Publishing" /v State /t REG_DWORD /D 146944 /F
Reg Add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v CertificateRevocation /t REG_DWORD /D 0 /F
@echo Don't Forget to Disable Certificate Revocation again after you join the domain.