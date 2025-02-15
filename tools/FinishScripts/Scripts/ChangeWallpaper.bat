@echo off
echo Change Wallpaper to Solid Blue
Reg Add "HKEY_CURRENT_USER\Control Panel\Desktop" /v Wallpaper /t REG_SZ /D "" /F
Reg Add "HKEY_CURRENT_USER\Control Panel\Colors" /v Background /t REG_SZ /D "10 59 118" /F
@echo Changes Will Apply after Logoff