set BatchFolder=%~dp0
echo %BatchFolder%

set PATH=%PATH%;%BatchFolder%system-check\resources\sap\nwrfcsdk\lib
set SAPNWRFC_HOME=%BatchFolder%system-check\resources\sap\nwrfcsdk\lib
set SNC_LIB=%SNC_LIB_64%
cd system-check
system-check.exe