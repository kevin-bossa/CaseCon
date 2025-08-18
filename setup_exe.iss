[Setup]
AppName=CaseCon
AppVersion=1.0
AppVerName=CaseCon 1.0
AppPublisher=Your Name
DefaultDirName={autopf}\CaseCon
DefaultGroupName=CaseCon
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=CaseCon_Setup_v1.0
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\CaseCon.exe
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startmenu"; Description: "Create Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startup"; Description: "Start CaseCon automatically when Windows starts"; GroupDescription: "Startup Options:"

[Files]
Source: "dist\CaseCon.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\CaseCon"; Filename: "{app}\CaseCon.exe"; IconFilename: "{app}\icon.ico"; Tasks: startmenu
Name: "{autodesktop}\CaseCon"; Filename: "{app}\CaseCon.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "CaseCon"; ValueData: "{app}\CaseCon.exe"; Tasks: startup

[Run]
Filename: "{app}\CaseCon.exe"; Description: "{cm:LaunchProgram,CaseCon}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "reg"; Parameters: "delete ""HKCU\Software\Microsoft\Windows\CurrentVersion\Run"" /v ""CaseCon"" /f"; Flags: runhidden