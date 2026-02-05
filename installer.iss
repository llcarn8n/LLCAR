; LLCAR Video Processing Pipeline - Windows Installer Script
; Inno Setup 6.0 or later required
; Download from: https://jrsoftware.org/isdl.php

#define MyAppName "LLCAR Video Processing Pipeline"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "LLCAR Team"
#define MyAppURL "https://github.com/llcarn8n/LLCAR"
#define MyAppExeName "llcar.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{A7B8C9D0-E1F2-4A5B-9C8D-7E6F5A4B3C2D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\LLCAR
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
InfoBeforeFile=README.md
OutputDir=installer_output
OutputBaseFilename=LLCAR_Setup_{#MyAppVersion}
SetupIconFile=
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Main executable and all dependencies
Source: "dist\llcar\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation files
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "CONSOLE.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "MODELS.md"; DestDir: "{app}"; Flags: ignoreversion

; Configuration files
Source: "config.yaml"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env.example"; DestDir: "{app}"; Flags: ignoreversion

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Dirs]
Name: "{app}\input"; Permissions: users-full
Name: "{app}\output"; Permissions: users-full
Name: "{app}\models"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--interactive"
Name: "{group}\{#MyAppName} Help"; Filename: "{app}\README.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--interactive"; Tasks: desktopicon

[Run]
Filename: "{app}\README.md"; Description: "View README"; Flags: postinstall shellexec skipifsilent unchecked
Filename: "{app}\{#MyAppExeName}"; Parameters: "--help"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent unchecked

[Code]
var
  FFmpegPage: TInputOptionWizardPage;
  HFTokenPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  // Create custom page for FFmpeg warning
  FFmpegPage := CreateInputOptionWizardPage(
    wpWelcome,
    'System Requirements',
    'Please ensure FFmpeg is installed',
    'LLCAR requires FFmpeg to process video files. Please ensure FFmpeg is installed and available in your system PATH.' + #13#10 + #13#10 +
    'If you do not have FFmpeg installed:' + #13#10 +
    '1. Download from: https://ffmpeg.org/download.html' + #13#10 +
    '2. Add FFmpeg to your system PATH' + #13#10 +
    '3. Restart this installer' + #13#10 + #13#10 +
    'Check the box below to confirm:',
    False,
    False
  );
  FFmpegPage.Add('I have FFmpeg installed or will install it before using LLCAR');
  FFmpegPage.Values[0] := False;

  // Create custom page for HuggingFace token
  HFTokenPage := CreateInputQueryWizardPage(
    FFmpegPage.ID,
    'HuggingFace Token',
    'Configure your HuggingFace token (Optional)',
    'LLCAR requires a HuggingFace token for speaker diarization.' + #13#10 +
    'You can get a free token at: https://huggingface.co/settings/tokens' + #13#10 + #13#10 +
    'You can configure this later by editing the .env file.'
  );
  HFTokenPage.Add('HuggingFace Token:', False);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if CurPageID = FFmpegPage.ID then
  begin
    if not FFmpegPage.Values[0] then
    begin
      MsgBox('Please confirm that FFmpeg is installed or that you will install it before using LLCAR.', mbInformation, MB_OK);
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvFilePath: String;
  EnvContent: TStringList;
begin
  if CurStep = ssPostInstall then
  begin
    // Create .env file with HuggingFace token if provided
    if HFTokenPage.Values[0] <> '' then
    begin
      EnvFilePath := ExpandConstant('{app}\.env');
      EnvContent := TStringList.Create;
      try
        EnvContent.Add('# LLCAR Environment Configuration');
        EnvContent.Add('# HuggingFace token for speaker diarization');
        EnvContent.Add('HF_TOKEN=' + HFTokenPage.Values[0]);
        EnvContent.SaveToFile(EnvFilePath);
      finally
        EnvContent.Free;
      end;
    end;
  end;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{app}\models"
Type: filesandordirs; Name: "{app}\output"
