[Setup]
AppId={{0A1B2C3D-4E5F-6789-ABCD-0123456789AB}}
AppName=Deney Uygulamasi
AppVersion=1.0.6
VersionInfoVersion=1.0.6
DefaultDirName={userappdata}\DeneyUygulamasi
DefaultGroupName=Deney Uygulamasi
OutputBaseFilename=DeneyUygulamasi-Setup-1.0.6
OutputDir=output
CloseApplications=yes
RestartApplications=no
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
; SetupIconFile=icon.ico   ; varsa aç

[Files]
Source: "dist\DeneyUygulamasi\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Deney Uygulamasi"; Filename: "{app}\DeneyUygulamasi.exe"
Name: "{autodesktop}\Deney Uygulamasi"; Filename: "{app}\DeneyUygulamasi.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Masaüstü kısayolu oluştur"; GroupDescription: "Ekstra seçenekler:"

[Run]
Filename: "{app}\DeneyUygulamasi.exe"; Description: "Kurulumdan sonra çalıştır"; Flags: nowait postinstall skipifsilent