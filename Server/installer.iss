; SYNEX+ 견적 시스템 설치 스크립트
; Inno Setup Script

#define MyAppName "SYNEX+ 견적 시스템"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "SYNEX"
#define MyAppExeName "SYNEX_Quotation.exe"

[Setup]
; 앱 식별자 (GUID)
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\SYNEX_Quotation
DefaultGroupName={#MyAppName}
; 출력 설정
OutputDir=installer_output
OutputBaseFilename=SYNEX_Quotation_Setup
; 압축 설정
Compression=lzma2
SolidCompression=yes
; 권한 설정
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
; UI 설정
WizardStyle=modern
; 언어
ShowLanguageDialog=no

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 바로가기 만들기"; GroupDescription: "추가 아이콘:"
Name: "quicklaunchicon"; Description: "빠른 실행에 바로가기 만들기"; GroupDescription: "추가 아이콘:"; Flags: unchecked

[Files]
; 메인 실행 파일
Source: "dist\SYNEX_Quotation.exe"; DestDir: "{app}"; Flags: ignoreversion
; 데이터 폴더
Source: "dist\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; 시작 메뉴
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName} 제거"; Filename: "{uninstallexe}"
; 바탕화면
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; 빠른 실행
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; 설치 후 실행 옵션
Filename: "{app}\{#MyAppExeName}"; Description: "SYNEX+ 견적 시스템 실행"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 제거 시 데이터 폴더 삭제 (선택적)
Type: filesandordirs; Name: "{app}\data"
