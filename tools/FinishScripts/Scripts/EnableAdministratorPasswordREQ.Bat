@echo off
echo Enable Administrator Password REQ
Set /P Pass="Select Password For Administrator:"
net user Administrator %Pass% /passwordreq:yes