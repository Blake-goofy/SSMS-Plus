[Setup]
AppId={{B8F5E6D2-8C4A-4B5E-9F3A-1D7C8E9B2A4F}
AppName=SSMS Plus
AppVersion=1.1.3
AppVerName=SSMS Plus 1.1.3
AppPublisher=Blake-goofy
AppPublisherURL=https://github.com/Blake-goofy/ssmsplus
AppSupportURL=https://github.com/Blake-goofy/ssmsplus/issues
AppUpdatesURL=https://github.com/Blake-goofy/ssmsplus/releases
DefaultDirName={autopf}\SSMS Plus
DisableProgramGroupPage=yes
LicenseFile=
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=SSMSPlus-Setup
SetupIconFile=ssmsplus_yellow.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\SSMSPlus.exe
; Update-related settings
VersionInfoVersion=1.1.3.0
VersionInfoCompany=Blake-goofy
VersionInfoDescription=SSMS Plus - Enhanced SQL Server Management Studio Experience
VersionInfoCopyright=Copyright (C) 2025 Blake-goofy
; Allow updates to overwrite existing installation
AllowNoIcons=yes
CreateUninstallRegKey=yes
UninstallDisplayName=SSMS Plus

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "Start SSMS Plus automatically when Windows starts"; GroupDescription: "Startup Options:"

[Files]
Source: "dist\SSMSPlus.exe"; DestDir: "{app}"; Flags: ignoreversion signonce
Source: "ssmsplus_yellow.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "ssmsplus_red.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\SSMS Plus"; Filename: "{app}\SSMSPlus.exe"
Name: "{autodesktop}\SSMS Plus"; Filename: "{app}\SSMSPlus.exe"; Tasks: desktopicon
Name: "{userstartup}\SSMS Plus"; Filename: "{app}\SSMSPlus.exe"; Tasks: startup
; Add uninstaller to programs menu
Name: "{autoprograms}\Uninstall SSMS Plus"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\SSMSPlus.exe"; Description: "{cm:LaunchProgram,SSMS Plus}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Stop the application before uninstalling
Filename: "{cmd}"; Parameters: "/C taskkill /F /IM SSMSPlus.exe"; Flags: runhidden; RunOnceId: "StopSSMSPlus"

[UninstallDelete]
; Clean up user settings (optional - you might want to preserve these)
; Type: files; Name: "{userappdata}\SSMSPlus\*"
; Type: dirifempty; Name: "{userappdata}\SSMSPlus"

[Code]
function InitializeSetup(): Boolean;
var
  OldVersion: String;
  IsUpdate: Boolean;
  ExitCode: Integer;
  RetryCount: Integer;
begin
  Result := True;
  
  // Check if this is an update installation
  IsUpdate := RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{B8F5E6D2-8C4A-4B5E-9F3A-1D7C8E9B2A4F}_is1', 'DisplayVersion', OldVersion);
  
  if IsUpdate then
  begin
    Log('Detected existing installation: ' + OldVersion);
    // Try to stop the running application before update (with retries)
    RetryCount := 0;
    while (RetryCount < 5) do
    begin
      // First try gentle termination
      if RetryCount = 0 then
        Exec('taskkill', '/IM SSMSPlus.exe', '', SW_HIDE, ewWaitUntilTerminated, ExitCode)
      else
        // Then use force
        Exec('taskkill', '/F /IM SSMSPlus.exe', '', SW_HIDE, ewWaitUntilTerminated, ExitCode);
      
      Sleep(2000); // Wait 2 seconds between attempts
      
      // Check if process is still running
      if not Exec('tasklist', '/FI "IMAGENAME eq SSMSPlus.exe" | find /I "SSMSPlus.exe"', '', SW_HIDE, ewWaitUntilTerminated, ExitCode) then
        break; // Process not found, we're good
        
      RetryCount := RetryCount + 1;
    end;
    
    // If we still can't close it after retries, warn the user
    if RetryCount >= 5 then
    begin
      if MsgBox('SSMS Plus is still running and needs to be closed for the update to proceed.' + #13#13 + 
                'Please close SSMS Plus manually and click "Retry", or click "Cancel" to abort the installation.', 
                mbError, MB_RETRYCANCEL) = IDCANCEL then
      begin
        Result := False;
        Exit;
      end;
    end;
  end;
  
  // Check if SSMS is installed (optional check)
  if not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Microsoft SQL Server\150\Tools\ClientSetup') and
     not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Microsoft SQL Server\160\Tools\ClientSetup') and
     not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Microsoft SQL Server\170\Tools\ClientSetup') then
  begin
    if MsgBox('SQL Server Management Studio (SSMS) was not detected on this system. SSMS Plus requires SSMS to function properly.' + #13#13 + 
              'Do you want to continue with the installation?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;

function InitializeUninstall(): Boolean;
var
  ExitCode: Integer;
begin
  Result := True;
  // Stop the application before uninstalling
  Exec('taskkill', '/F /IM SSMSPlus.exe', '', SW_HIDE, ewWaitUntilTerminated, ExitCode);
  
  // Ask user if they want to keep settings
  if MsgBox('Do you want to keep your SSMS Plus settings and configuration?' + #13#13 + 
            'Choose "Yes" to preserve your settings for future installations.' + #13 +
            'Choose "No" to completely remove all SSMS Plus data.', 
            mbConfirmation, MB_YESNO) = IDNO then
  begin
    // User wants to remove all data - this would be handled in UninstallDelete section
    RegWriteStringValue(HKEY_CURRENT_USER, 'Software\SSMS Plus\Uninstall', 'RemoveAllData', 'true');
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  IsUpdate: Boolean;
  OldVersion: String;
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    IsUpdate := RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{B8F5E6D2-8C4A-4B5E-9F3A-1D7C8E9B2A4F}_is1', 'DisplayVersion', OldVersion);
    
    if IsUpdate then
    begin
      // Show update success message
      MsgBox('SSMS Plus has been updated successfully!' + #13#13 + 
             'Updated from version ' + OldVersion + ' to 1.1.3' + #13#13 +
             'The application will start automatically.', 
             mbInformation, MB_OK);
             
      // Auto-start the application after update
      Exec(ExpandConstant('{app}\SSMSPlus.exe'), '', '', SW_SHOW, ewNoWait, ResultCode);
    end
    else
    begin
      // Show first-time installation message
      MsgBox('SSMS Plus has been installed successfully!' + #13#13 + 
             'To get started:' + #13 +
             '1. Look for SSMS Plus in your system tray (bottom-right corner)' + #13 +
             '2. Left-click the icon to configure your directories' + #13 +
             '3. Enable "Color tabs by regular expression" in SSMS Options' + #13#13 +
             'For detailed setup instructions, see the README file in the installation folder.', 
             mbInformation, MB_OK);
    end;
  end;
end;
