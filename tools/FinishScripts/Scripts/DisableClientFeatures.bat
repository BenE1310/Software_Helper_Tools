@echo off
echo Disable Client Features
Dism /Online /Disable-Feature /FeatureName:WindowsGadgetPlatform /NoRestart
Dism /Online /Disable-Feature /FeatureName:TabletPCOC /NoRestart
Dism /Online /Disable-Feature /FeatureName:Printing-Foundation-InternetPrinting-Client /NoRestart
Dism /Online /Disable-Feature /FeatureName:FaxServicesClientPackage /NoRestart
Dism /Online /Disable-Feature /FeatureName:MediaCenter /NoRestart
Dism /Online /Disable-Feature /FeatureName:OpticalMediaDisc /NoRestart