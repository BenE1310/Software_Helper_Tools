@echo off
echo Change Power Config
PowerCFG.Exe -SetActive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
PowerCFG.Exe -X Monitor-TimeOut-DC 0
PowerCFG.Exe -X Monitor-TimeOut-AC 0
PowerCFG.Exe -X -Disk-TimeOut-Ac 0
PowerCFG.Exe -X -Disk-TimeOut-Dc 0
PowerCFG.Exe -X -Standby-TimeOut-Ac 0
PowerCFG.Exe -X -Standby-TimeOut-Dc 0
PowerCFG.Exe -X -Hibernate-TimeOut-Ac 0
PowerCFG.Exe -X -Hibernate-TimeOut-Dc 0
PowerCFG.Exe -H Off