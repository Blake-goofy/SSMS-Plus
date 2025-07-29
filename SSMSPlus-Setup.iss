[Setup]
AppId={{B8F5E6D2-8C4A-4B5E-9F3A-1D7C8E9B2A4F}
AppName=SSMS Plus
AppVersion=1.0.0
AppVerName=SSMS Plus 1.0.0
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

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "Start SSMS Plus automatically when Windows starts"; GroupDescription: "Startup Options:"; Flags: unchecked

[Files]
Source: "dist\SSMSPlus.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ssmsplus_yellow.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "ssmsplus_red.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "ssmsplus.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\SSMS Plus"; Filename: "{app}\SSMSPlus.exe"; IconFilename: "{app}\ssmsplus.ico"
Name: "{autodesktop}\SSMS Plus"; Filename: "{app}\SSMSPlus.exe"; IconFilename: "{app}\ssmsplus.ico"; Tasks: desktopicon
Name: "{userstartup}\SSMS Plus"; Filename: "{app}\SSMSPlus.exe"; Tasks: startup

[Run]
Filename: "{app}\SSMSPlus.exe"; Description: "{cm:LaunchProgram,SSMS Plus}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check if SSMS is installed (optional check)
  if not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Microsoft SQL Server\150\Tools\ClientSetup') and
     not RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Microsoft SQL Server\160\Tools\ClientSetup') then
  begin
    if MsgBox('SQL Server Management Studio (SSMS) was not detected on this system. SSMS Plus requires SSMS to function properly.' + #13#13 + 
              'Do you want to continue with the installation?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Show a helpful message after installation
    MsgBox('SSMS Plus has been installed successfully!' + #13#13 + 
           'To get started:' + #13 +
           '1. Look for SSMS Plus in your system tray (bottom-right corner)' + #13 +
           '2. Left-click the icon to configure your directories' + #13 +
           '3. Enable "Color tabs by regular expression" in SSMS Options' + #13#13 +
           'For detailed setup instructions, see the README file in the installation folder.', 
           mbInformation, MB_OK);
  end;
end;
