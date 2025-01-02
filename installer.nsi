Unicode True

; Load and configure language presets
LoadLanguageFile "${NSISDIR}\Contrib\Language files\English.nlf"
LoadLanguageFile "${NSISDIR}\Contrib\Language files\SimpChinese.nlf"

; Load language strings
!include "languages\\en.nsh"
!include "languages\\zh_CN.nsh"

; Set the default installation directory
InstallDir "C:\LaneAssist"

; Customize the welcome page
!define MUI_WELCOMEPAGE_TITLE $(WelcomeTitle)
!define MUI_WELCOMEPAGE_TEXT $(WelcomeText)

; Customize the finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\run.bat"
!define MUI_FINISHPAGE_RUN_TEXT $(FinishRunText)

; Icons
!define MUI_ICON "icon/favicon.ico"
!define MUI_UNICON "icon/favicon.ico"

; Include the MUI
!include "MUI2.nsh"

; Set the name of the installer
Outfile "ETS2LA-Installer.exe"

; Set the name of the application
Name "ETS2LA"
BrandingText "wiki.tumppi066.fi"

; Set the icon
Icon "icon/favicon.ico"

; Set the page sequence
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH


; Start the sections
Section "Python" SEC01
    ; Check if Python is installed
    DetailPrint $(SEC01_CheckIfPythonInstalled)
    ClearErrors
    nsExec::ExecToStack 'CMD /C python --version'
    Pop $0 ; status
    Pop $1 ; output
    StrCmp $0 "error" PythonNotInstalled
        ; Python is installed, check the version
        StrCpy $2 $1 4 7 ; get the version number (e.g., "3.11")
        StrCpy $3 $2 1 ; get the major version number (e.g., "3")
        StrCpy $4 $2 3 2 ; get the minor version number (e.g., "11")
        StrCmp $3 3 CheckMinorVersion ; compare the major version number to 3
            ; The major version number is less than 3, Python 3.12 or over is not installed
            Goto PythonNotInstalled
        CheckMinorVersion:
            StrCmp $4 12 PythonTooNew PythonInstalled ; compare the minor version number to 12
        PythonTooNew:
            MessageBox MB_OK $(SEC01_PythonVersionTooNew)
            Quit
        PythonInstalled:
            Goto End

    PythonNotInstalled:
        ; Define the Python installer file
        Var /GLOBAL PythonInstaller
        StrCpy $PythonInstaller "python-3.11.8-amd64.exe"

        DetailPrint $(SEC01_DownloadingPythonInstaller)
        ; Download the Python installer
        inetc::get /SILENT /PROGRESS "https://www.python.org/ftp/python/3.11.8/$PythonInstaller" "$TEMP/$PythonInstaller" /END

        ; Run the Python installer
        ExecWait '"$TEMP/$PythonInstaller" InstallAllUsers=1 PrependPath=1 Include_test=0'

        ; Delete the Python installer
        Delete "$TEMP/$PythonInstaller"

        MessageBox MB_OK $(SEC01_PythonInstalledSuccessfully)
        Quit
    End:
SectionEnd

Section "Git" SEC02
    ; Check if Git is installed
    DetailPrint $(SEC02_CheckIfGitInstalled)
    ClearErrors
    nsExec::ExecToStack 'CMD /C git --version'
    Pop $0 ; status
    Pop $1 ; output
    StrCmp $0 "1" GitNotInstalled
        Goto End
    GitNotInstalled:
        ; Define the Git installer file
        Var /GLOBAL GitInstaller
        StrCpy $GitInstaller "Git-2.44.0-64-bit.exe"

        ; Download the Git installer
        DetailPrint $(SEC02_DownloadingGitInstaller)
        inetc::get /SILENT /PROGRESS "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe" "$TEMP/$GitInstaller" /END

        ; Run the Git installer
        ExecWait '"$TEMP/$GitInstaller" /LOADINF="git.inf" /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /NOICONS /COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"'

        ; Delete the Git installer
        Delete "$TEMP/$GitInstaller"

        MessageBox MB_OK $(SEC02_GitInstalledSuccessfully)
        Quit
    End:
SectionEnd

Section "MainSection" SEC03
    ; Git clone the Lane Assist repository
    DetailPrint $(SEC03_DownloadLALibrary)
    
    ExecWait 'cmd /c "git clone https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist.git $INSTDIR\app"'

    DetailPrint $(SEC03_CreatingPythonVenv)
    ; Create a venv in the INSTDIR/venv dir
    nsExec::ExecToStack 'python -m venv "$INSTDIR"/venv'
    Pop $0 ; status
    StrCmp $0 "error" VenvCreationFailed
        Goto VenvCreationSuccess
    VenvCreationFailed:
        MessageBox MB_OK $(SEC03_FailedToCreateVenv)
    VenvCreationSuccess:
        DetailPrint $(SEC03_InstallingRequirements)
        
        ; Write the requirements.bat file
        FileOpen $0 "$INSTDIR\requirements.bat" "w"
        FileWrite $0 '@echo off$\r$\n'
        FileWrite $0 'call "$INSTDIR\venv\Scripts\activate" $\r$\n'
        FileWrite $0 'pip install -r "$INSTDIR\app\requirements.txt" $\r$\n'
        FileClose $0

        ; Execute the batch file
        ExecWait 'cmd /c "$INSTDIR\requirements.bat"'

        ; Write the run.bat file
        FileOpen $0 "$INSTDIR\run.bat" "w"
        FileWrite $0 'cmd /k "cd $INSTDIR/venv/Scripts & .\activate & cd $INSTDIR/app & $INSTDIR/venv/Scripts/python main.py & pause & exit" & exit'
        FileClose $0
        ; Write the update.bat file
        FileOpen $0 "$INSTDIR\update.bat" "w"
        FileWrite $0 'cmd /k "cd $INSTDIR/venv/Scripts & .\activate & cd $INSTDIR/app & git stash & git pull & exit" & pause'
        FileClose $0
        ; Write the activate.bat file
        FileOpen $0 "$INSTDIR\activate.bat" "w"
        FileWrite $0 'cmd /k"cd "$INSTDIR/venv/Scripts" & .\activate.bat & cd $INSTDIR"'
        FileClose $0

        MessageBox MB_OK $(SEC03_LAInstallationCompleted)

    ; Create Start Menu shortcuts
    CreateDirectory $SMPROGRAMS\ETS2LA
    CreateShortCut "$SMPROGRAMS\ETS2LA\ETS2LA.lnk" "$INSTDIR\run.bat" "" "$INSTDIR\app\assets\favicon.ico"
    CreateShortCut "$SMPROGRAMS\ETS2LA\Uninstall ETS2LA.lnk" "$INSTDIR\uninstall.exe"

    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    ; Remove the Start Menu shortcuts
    Delete "$SMPROGRAMS\ETS2LA\ETS2LA.lnk"
    Delete "$SMPROGRAMS\ETS2LA\Uninstall ETS2LA.lnk"
    RMDir "$SMPROGRAMS\ETS2LA"

    ; Remove the installation directory
    ExecWait 'cmd.exe /C rd /S /Q "$INSTDIR"'
SectionEnd
