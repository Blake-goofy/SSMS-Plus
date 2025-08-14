[Setup]
AppId={{B8F5E6D2-8C4A-4B5E-9F3A-1D7C8E9B2A4F}
AppName=SSMS Plus
AppVersion=1.1.5
AppVerName=SSMS Plus 1.1.5
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
VersionInfoVersion=1.1.5.0
VersionInfoCompany=Blake-goofy
VersionInfoDescription=SSMS Plus - Enhanced SQL Server Management Studio Experience
VersionInfoCopyright=Copyright (C) 2025 Blake-goofy
; Allow updates to overwrite existing installation
AllowNoIcons=yes
CreateUninstallRegKey=yes
UninstallDisplayName=SSMS Plus
DisableFinishedPage=no

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
; Always show launch checkbox - checked by default for convenience
Filename: "{app}\SSMSPlus.exe"; Description: "{cm:LaunchProgram,SSMS Plus}"; Flags: nowait postinstall

[UninstallRun]
; Stop the application before uninstalling
Filename: "{cmd}"; Parameters: "/C taskkill /F /IM SSMSPlus.exe"; Flags: runhidden; RunOnceId: "StopSSMSPlus"

[UninstallDelete]
; Clean up user settings (optional - you might want to preserve these)
; Type: files; Name: "{userappdata}\SSMSPlus\*"
; Type: dirifempty; Name: "{userappdata}\SSMSPlus"

[Code]
function BoolToStr(Value: Boolean): String;
begin
  if Value then
    Result := 'True'
  else
    Result := 'False';
end;

function InitializeSetup(): Boolean;
var
  ExitCode: Integer;
begin
  Result := True;
  
  // Always try to stop any running SSMS Plus process before installation
  // This works for both fresh installs and updates
  Log('InitializeSetup: Attempting to terminate any running SSMSPlus processes');
  Exec('taskkill', '/F /IM SSMSPlus.exe', '', SW_HIDE, ewWaitUntilTerminated, ExitCode);
  Log('InitializeSetup: taskkill result = ' + IntToStr(ExitCode));
  
  // Give a moment for the process to fully terminate
  Sleep(1000);
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
  ExitCode: Integer;
begin
  // Simple logging only - let the [Run] section handle launching
  Log('CurStepChanged: CurStep = ' + IntToStr(Ord(CurStep)));
  
  if CurStep = ssDone then
    Log('CurStepChanged: Installation complete');
end;
