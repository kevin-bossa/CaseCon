; CaseCon Installer Script for Inno Setup
; This script creates a professional installer for the CaseCon application

#define MyAppName "CaseCon"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Name"
#define MyAppURL "https://github.com/yourusername/casecon"
#define MyAppExeName "CaseCon.exe"
#define MyAppDescription "Text Case Converter with Global Hotkeys"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{12345678-1234-1234-1234-123456789ABC}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=output
OutputBaseFilename=CaseCon_Setup_v{#MyAppVersion}
SetupIconFile=installer_files\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

; Modern installer appearance
WizardImageFile=
WizardSmallImageFile=

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1
Name: "startup"; Description: "Start {#MyAppName} automatically when Windows starts"; GroupDescription: "Startup Options:"; Flags: unchecked

[Files]
; Main executable
Source: "installer_files\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Icon file
Source: "installer_files\icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; Additional files (if they exist)
Source: "installer_files\README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "installer_files\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; Add to startup if user selected the option
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "CaseCon"; ValueData: """{app}\{#MyAppExeName}"""; Tasks: startup

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{userappdata}\CaseCon\*"
Type: dirifempty; Name: "{userappdata}\CaseCon"

[UninstallRun]
; Remove from startup registry when uninstalling
Filename: "reg"; Parameters: "delete ""HKCU\Software\Microsoft\Windows\CurrentVersion\Run"" /v ""CaseCon"" /f"; Flags: runhidden; RunOnceId: "RemoveStartup"

[Code]
// Custom code for advanced installer behavior

// Check if .NET Framework is installed (if needed in future)
function IsDotNetDetected(version: string; service: cardinal): boolean;
var
    key: string;
    install, release, serviceCount: cardinal;
    check: boolean;
begin
    // .NET Framework version check code would go here if needed
    result := true; // For now, assume it's available
end;

// Custom uninstall confirmation
function InitializeUninstall(): Boolean;
begin
  Result := True;
  if MsgBox('This will remove CaseCon and all its settings. Continue?', mbConfirmation, MB_YESNO) = IDNO then
    Result := False;
end;

// Check if application is running before install
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  // Try to terminate CaseCon if it's running
  Exec('taskkill', '/f /im CaseCon.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := '';
end;

// Post-install actions
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Could add post-install tasks here
  end;
end;

// Custom finish page
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
  begin
    // Custom actions on finish page
  end;
end;