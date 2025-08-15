@echo off
setlocal

rem --- Admin Configuration ---
set "RUNAS_USER=username"
set "SSMS_EXE=C:\Users\Public\SSMS Plus Admin\SSMSPlus.exe"
rem ---------------------------

if not exist "%SSMS_EXE%" (
    echo SSMS Plus not found at:
    echo   %SSMS_EXE%
    echo Update SSMS_EXE in this script to match your install path, then run again.
    pause
    exit /b 1
)

echo Launching SSMS Plus as %RUNAS_USER% ...
echo If this is your first time running it, you will be prompted once to enter the password.
echo After that, it will not prompt again on this machine.

:launch
runas /savecred /user:%RUNAS_USER% "%SSMS_EXE%"
if errorlevel 1 (
    echo.
    echo Incorrect password or the prompt was cancelled. Try again.
    pause
    goto launch
)

endlocal
