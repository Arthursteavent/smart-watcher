[Setup]
AppName=Smart Scanner Watcher
AppVersion=1.0
DefaultDirName={userappdata}\SmartScannerWatcher
DefaultGroupName=Smart Scanner Watcher
OutputDir=.\installer
OutputBaseFilename=SmartWatcher_Installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
Name: "startup"; Description: "Start Smart Watcher automatically when Windows starts"; GroupDescription: "Auto-start:"

[Files]
Source: "dist\Watcher\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Smart Scanner Watcher"; Filename: "{app}\Watcher.exe"
Name: "{commondesktop}\Smart Scanner Watcher"; Filename: "{app}\Watcher.exe"; Tasks: desktopicon
Name: "{userstartup}\Smart Scanner Watcher"; Filename: "{app}\Watcher.exe"; Tasks: startup

[Run]
Filename: "{app}\Watcher.exe"; Description: "Launch Smart Scanner Watcher"; Flags: nowait postinstall skipifsilent
