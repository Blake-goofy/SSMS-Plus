[Setup]
AppId={{B8F5E6D2-8C4A-4B5E-9F3A-1D7C8E9B2A4F}
AppName=SSMS Plus
AppVersion=1.2.0
AppVerName=SSMS Plus 1.2.0
AppPublisher=Blake-goofy
AppPublisherURL=https://github.com/Blake-goofy/ssmsplus
AppSupportURL=https://github.com/Blake-goofy/ssmsplus/issues
AppUpdatesURL=https://github.com/Blake-goofy/ssmsplus/releases
DefaultDirName={localappdata}\Programs\SSMS Plus
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
VersionInfoVersion=1.2.0.0
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
Name: "admininstall"; Description: "Install admin version (allows running as different user)"; GroupDescription: "Admin Installation:"
Name: "adminstartup"; Description: "Start admin version automatically when Windows starts"; GroupDescription: "Admin Installation:"
Name: "ssmslauncher"; Description: "Install SSMS Admin launcher (runs regular SSMS as different user)"; GroupDescription: "Bonus Tools:"

[Files]
Source: "dist\SSMSPlus.exe"; DestDir: "{app}"; Flags: ignoreversion signonce
Source: "ssmsplus_yellow.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "ssmsplus_red.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "SSMS Plus Admin.bat"; DestDir: "{app}"; Flags: ignoreversion; Tasks: admininstall
Source: "SSMS Admin.bat"; DestDir: "{app}"; Flags: ignoreversion; Tasks: ssmslauncher
; Admin installation files - use public location accessible by all users
Source: "dist\SSMSPlus.exe"; DestDir: "C:\Users\Public\SSMS Plus Admin"; Flags: ignoreversion signonce; Tasks: admininstall
Source: "ssmsplus_yellow.ico"; DestDir: "C:\Users\Public\SSMS Plus Admin"; Flags: ignoreversion; Tasks: admininstall
Source: "ssmsplus_red.ico"; DestDir: "C:\Users\Public\SSMS Plus Admin"; Flags: ignoreversion; Tasks: admininstall
Source: "README.md"; DestDir: "C:\Users\Public\SSMS Plus Admin"; Flags: ignoreversion; Tasks: admininstall
Source: "SSMS Plus Admin.bat"; DestDir: "C:\Users\Public\SSMS Plus Admin"; Flags: ignoreversion; Tasks: admininstall

[Icons]
Name: "{autoprograms}\SSMS Plus"; Filename: "{app}\SSMSPlus.exe"; IconFilename: "{app}\ssmsplus_yellow.ico"
Name: "{autodesktop}\SSMS Plus"; Filename: "{app}\SSMSPlus.exe"; IconFilename: "{app}\ssmsplus_yellow.ico"; Tasks: desktopicon
Name: "{userstartup}\SSMS Plus"; Filename: "{app}\SSMSPlus.exe"; Tasks: startup
; Admin installation shortcuts - use user locations instead of common
Name: "{autoprograms}\SSMS Plus Admin"; Filename: "C:\Users\Public\SSMS Plus Admin\SSMSPlus.exe"; IconFilename: "C:\Users\Public\SSMS Plus Admin\ssmsplus_yellow.ico"; Tasks: admininstall
Name: "{autodesktop}\SSMS Plus Admin"; Filename: "C:\Users\Public\SSMS Plus Admin\SSMSPlus.exe"; IconFilename: "C:\Users\Public\SSMS Plus Admin\ssmsplus_yellow.ico"; Tasks: admininstall and adminstartup
Name: "{userstartup}\SSMS Plus Admin"; Filename: "{app}\SSMS Plus Admin.bat"; IconFilename: "{app}\ssmsplus_yellow.ico"; Tasks: admininstall and adminstartup
; SSMS Admin launcher shortcut
Name: "{autoprograms}\SSMS Admin Launcher"; Filename: "{app}\SSMS Admin.bat"; IconFilename: "{app}\ssmsplus_red.ico"; Tasks: ssmslauncher
Name: "{autodesktop}\SSMS Admin Launcher"; Filename: "{app}\SSMS Admin.bat"; IconFilename: "{app}\ssmsplus_red.ico"; Tasks: ssmslauncher
; Add uninstaller to programs menu
Name: "{autoprograms}\Uninstall SSMS Plus"; Filename: "{uninstallexe}"

[Run]
; Always show launch checkbox for regular version
Filename: "{app}\SSMSPlus.exe"; Description: "{cm:LaunchProgram,SSMS Plus}"; Flags: nowait postinstall
; Launch admin version via batch file (with runas) if it was installed - checked by default
Filename: "{app}\SSMS Plus Admin.bat"; Description: "Launch SSMS Plus Admin (as different user)"; Flags: nowait postinstall; Tasks: admininstall

[UninstallRun]
; Stop the application before uninstalling
Filename: "{cmd}"; Parameters: "/C taskkill /F /IM SSMSPlus.exe"; Flags: runhidden; RunOnceId: "StopSSMSPlus"

[UninstallDelete]
; Clean up user settings (optional - you might want to preserve these)
; Type: files; Name: "{userappdata}\SSMSPlus\*"
; Type: dirifempty; Name: "{userappdata}\SSMSPlus"

[Code]
var
  UsernameInputPage: TInputQueryWizardPage;
  TargetUsername: String;
  SSMSExePath: String;

function FindSSMSExe(): String;
var
  Paths: array of String;
  i: Integer;
begin
  Result := '';
  
  // SSMS Plus is built for SSMS 21 - prioritize SSMS 21 paths only
  // Older versions may not work correctly due to UI/API changes
  SetArrayLength(Paths, 2);
  Paths[0] := 'C:\Program Files\Microsoft SQL Server Management Studio 21\Common7\IDE\Ssms.exe';
  Paths[1] := 'C:\Program Files (x86)\Microsoft SQL Server Management Studio 21\Common7\IDE\Ssms.exe';
  
  for i := 0 to GetArrayLength(Paths) - 1 do
  begin
    if FileExists(Paths[i]) then
    begin
      Result := Paths[i];
      Log('Found SSMS 21 at: ' + Result);
      break;
    end;
  end;
  
  if Result = '' then
  begin
    Log('WARNING: SSMS 21 not found. SSMS Plus is designed for SSMS 21 and may not work correctly with older versions.');
    // Fallback to older versions but with warning
    SetArrayLength(Paths, 7);
    Paths[0] := 'C:\Program Files\Microsoft SQL Server Management Studio 20\Common7\IDE\Ssms.exe';
    Paths[1] := 'C:\Program Files (x86)\Microsoft SQL Server Management Studio 20\Common7\IDE\Ssms.exe';
    Paths[2] := 'C:\Program Files\Microsoft SQL Server Management Studio 19\Common7\IDE\Ssms.exe';
    Paths[3] := 'C:\Program Files (x86)\Microsoft SQL Server Management Studio 19\Common7\IDE\Ssms.exe';
    Paths[4] := 'C:\Program Files (x86)\Microsoft SQL Server Management Studio 18\Common7\IDE\Ssms.exe';  
    Paths[5] := 'C:\Program Files (x86)\Microsoft SQL Server\150\Tools\Binn\ManagementStudio\Ssms.exe';
    Paths[6] := 'C:\Program Files (x86)\Microsoft SQL Server\140\Tools\Binn\ManagementStudio\Ssms.exe';
    
    for i := 0 to GetArrayLength(Paths) - 1 do
    begin
      if FileExists(Paths[i]) then
      begin
        Result := Paths[i];
        Log('Found older SSMS at: ' + Result + ' (compatibility not guaranteed)');
        break;
      end;
    end;
  end;
  
  if Result = '' then
    Log('No SSMS installation found in common paths. SSMS Plus requires SSMS 21 for optimal compatibility.');
end;

procedure InitializeWizard();
begin
  // Find SSMS executable path
  SSMSExePath := FindSSMSExe();
  
  // Create username input page only if admin installation is available
  UsernameInputPage := CreateInputQueryPage(wpSelectTasks,
    'Admin Installation Settings', 'Specify the username for admin installations',
    'Enter the username that will be used for the admin installation batch files. ' +
    'This username will be substituted in the batch files for "runas" commands.');
  
  UsernameInputPage.Add('Username:', False);
  UsernameInputPage.Values[0] := 'JASCOPRODUCTS\'; // default value with domain prefix
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  
  // Skip username page if admin tasks are not selected
  if PageID = UsernameInputPage.ID then
    Result := not (WizardIsTaskSelected('admininstall') or WizardIsTaskSelected('ssmslauncher'));
end;

function StringReplace(S, OldPattern, NewPattern: String): String;
var
  P: Integer;
begin
  Result := S;
  P := Pos(OldPattern, Result);
  while P > 0 do
  begin
    Delete(Result, P, Length(OldPattern));
    Insert(NewPattern, Result, P);
    P := Pos(OldPattern, Result);
  end;
end;

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
  BatchFile: String;
  Lines: TArrayOfString;
  i: Integer;
  Line: String;
begin
  // Simple logging only - let the [Run] section handle launching
  Log('CurStepChanged: CurStep = ' + IntToStr(Ord(CurStep)));
  
  if CurStep = ssPostInstall then
  begin
    // Get the username from the input page
    if WizardIsTaskSelected('admininstall') or WizardIsTaskSelected('ssmslauncher') then
      TargetUsername := UsernameInputPage.Values[0];
    
    // Process SSMS Plus Admin batch file
    if WizardIsTaskSelected('admininstall') then
    begin
      BatchFile := ExpandConstant('{app}\SSMS Plus Admin.bat');
      if LoadStringsFromFile(BatchFile, Lines) then
      begin
        for i := 0 to GetArrayLength(Lines) - 1 do
        begin
          Line := Lines[i];
          Line := StringReplace(Line, 'username', TargetUsername);
          if SSMSExePath <> '' then
            Line := StringReplace(Line, 'C:\Program Files (x86)\Microsoft SQL Server Management Studio 19\Common7\IDE\Ssms.exe', SSMSExePath);
          Lines[i] := Line;
        end;
        SaveStringsToFile(BatchFile, Lines, False);
        Log('Updated SSMS Plus Admin.bat with username: ' + TargetUsername);
      end;
    end;
    
    // Process SSMS Admin launcher batch file
    if WizardIsTaskSelected('ssmslauncher') then
    begin
      BatchFile := ExpandConstant('{app}\SSMS Admin.bat');
      if LoadStringsFromFile(BatchFile, Lines) then
      begin
        for i := 0 to GetArrayLength(Lines) - 1 do
        begin
          Line := Lines[i];
          Line := StringReplace(Line, 'username', TargetUsername);
          if SSMSExePath <> '' then
            Line := StringReplace(Line, 'C:\Program Files (x86)\Microsoft SQL Server Management Studio 19\Common7\IDE\Ssms.exe', SSMSExePath);
          Lines[i] := Line;
        end;
        SaveStringsToFile(BatchFile, Lines, False);
        Log('Updated SSMS Admin.bat with username: ' + TargetUsername);
      end;
    end;
  end;
  
  if CurStep = ssDone then
    Log('CurStepChanged: Installation complete');
end;
