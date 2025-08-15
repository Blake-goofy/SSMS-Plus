@echo off
setlocal enabledelayedexpansion

rem =============================================================
rem SSMS Admin Launcher
rem Launches SQL Server Management Studio as a different user
rem =============================================================

rem --- Admin Configuration (replaced by installer) ---
set "RUNAS_USER={ADMIN_USERNAME}"
rem ---------------------------------------------------

echo SSMS Admin Launcher
echo ===================
echo.

rem Auto-detect SSMS installation - prioritize SSMS 21 (recommended)
set "SSMS_EXE="
set "SSMS_VERSION="

rem Check for SSMS 21 first (optimal compatibility)
if exist "C:\Program Files\Microsoft SQL Server Management Studio 21\Common7\IDE\Ssms.exe" (
    set "SSMS_EXE=C:\Program Files\Microsoft SQL Server Management Studio 21\Common7\IDE\Ssms.exe"
    set "SSMS_VERSION=21"
    goto :found
)
if exist "C:\Program Files (x86)\Microsoft SQL Server Management Studio 21\Common7\IDE\Ssms.exe" (
    set "SSMS_EXE=C:\Program Files (x86)\Microsoft SQL Server Management Studio 21\Common7\IDE\Ssms.exe"
    set "SSMS_VERSION=21"
    goto :found
)

echo WARNING: SSMS 21 not found. Searching for older versions...
echo NOTE: This tool works best with SSMS 21. Older versions may have compatibility issues.
echo.

rem Fallback to older versions (compatibility not guaranteed)
for %%v in (20 19 18) do (
    if exist "C:\Program Files (x86)\Microsoft SQL Server Management Studio %%v\Common7\IDE\Ssms.exe" (
        set "SSMS_EXE=C:\Program Files (x86)\Microsoft SQL Server Management Studio %%v\Common7\IDE\Ssms.exe"
        set "SSMS_VERSION=%%v"
        goto :found
    )
    if exist "C:\Program Files\Microsoft SQL Server Management Studio %%v\Common7\IDE\Ssms.exe" (
        set "SSMS_EXE=C:\Program Files\Microsoft SQL Server Management Studio %%v\Common7\IDE\Ssms.exe"
        set "SSMS_VERSION=%%v"
        goto :found
    )
    if exist "C:\Program Files (x86)\Microsoft SQL Server Management Studio %%v\Release\Common7\IDE\Ssms.exe" (
        set "SSMS_EXE=C:\Program Files (x86)\Microsoft SQL Server Management Studio %%v\Release\Common7\IDE\Ssms.exe"
        set "SSMS_VERSION=%%v"
        goto :found
    )
    if exist "C:\Program Files\Microsoft SQL Server Management Studio %%v\Release\Common7\IDE\Ssms.exe" (
        set "SSMS_EXE=C:\Program Files\Microsoft SQL Server Management Studio %%v\Release\Common7\IDE\Ssms.exe"
        set "SSMS_VERSION=%%v"
        goto :found
    )
)

rem Check legacy SQL Server installation paths
for %%v in (150 140 130 120 110 100) do (
    if exist "C:\Program Files (x86)\Microsoft SQL Server\%%v\Tools\Binn\ManagementStudio\Ssms.exe" (
        set "SSMS_EXE=C:\Program Files (x86)\Microsoft SQL Server\%%v\Tools\Binn\ManagementStudio\Ssms.exe"
        goto :found
    )
    if exist "C:\Program Files\Microsoft SQL Server\%%v\Tools\Binn\ManagementStudio\Ssms.exe" (
        set "SSMS_EXE=C:\Program Files\Microsoft SQL Server\%%v\Tools\Binn\ManagementStudio\Ssms.exe"
        goto :found
    )
)

rem If not found, show error
echo ERROR: SQL Server Management Studio not found!
echo.
echo Searched the following locations:
echo   - C:\Program Files\Microsoft SQL Server Management Studio [18-21]\Common7\IDE\Ssms.exe
echo   - C:\Program Files\Microsoft SQL Server Management Studio [18-21]\Release\Common7\IDE\Ssms.exe
echo   - C:\Program Files (x86)\Microsoft SQL Server Management Studio [18-21]\Common7\IDE\Ssms.exe
echo   - C:\Program Files (x86)\Microsoft SQL Server Management Studio [18-21]\Release\Common7\IDE\Ssms.exe
echo   - C:\Program Files\Microsoft SQL Server\[100-150]\Tools\Binn\ManagementStudio\Ssms.exe
echo   - C:\Program Files (x86)\Microsoft SQL Server\[100-150]\Tools\Binn\ManagementStudio\Ssms.exe
echo.
echo Please install SQL Server Management Studio or update this script with the correct path.
pause
exit /b 1

:found
echo Found SSMS at: !SSMS_EXE!
if defined SSMS_VERSION (
    if "!SSMS_VERSION!"=="21" (
        echo Version: SSMS !SSMS_VERSION! (Optimal compatibility)
    ) else (
        echo Version: SSMS !SSMS_VERSION! (Compatibility not guaranteed - SSMS 21 recommended)
    )
) else (
    echo Version: Legacy SQL Server installation (Compatibility not guaranteed)
)
echo.
echo Launching SSMS as: %RUNAS_USER%
echo.
echo NOTE: If this is your first time running as this user, you will be
echo       prompted to enter the password. After that, Windows will remember
echo       the credentials on this machine (using /savecred).
echo.

:launch
runas /savecred /user:%RUNAS_USER% "\"!SSMS_EXE!\""
if errorlevel 1 (
    echo.
    echo Failed to launch SSMS. This could be due to:
    echo   - Incorrect password
    echo   - User cancelled the prompt
    echo   - Account doesn't have permission to run SSMS
    echo.
    set /p retry="Try again? (Y/N): "
    if /i "!retry!"=="Y" goto launch
)

echo.
echo Done.
endlocal
