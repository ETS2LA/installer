Unicode True

!include "MUI2.nsh"
!include "nsDialogs.nsh"

RequestExecutionLevel user

# Variables
InstallDir "C:\ETS2LA"
!define BRANCH "main"
!define GITLAB_URL "https://gitlab.com/ETS2LA/ETS2LA"
!define GITHUB_URL "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist.git"
!define SOURCEFORGE_URL "https://git.code.sf.net/p/eurotrucksimulator2-laneassist/code"
!define CNB_URL "https://cnb.cool/ETS2LA-CN/Euro-Truck-Simulator-2-Lane-Assist.git"


# Installer Information
Name "ETS2LA"
BrandingText $(BrandingText)
Icon "img\favicon.ico"
OutFile "ETS2LA-Windows-Installer.exe"

# MUI Setup
!define MUI_ICON "img\favicon.ico"
!define MUI_UNICON "img\favicon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "img\header.bmp2"
!define MUI_HEADERIMAGE_UNBITMAP "img\header.bmp2"
!include "MUI2.nsh"

# Welcome Page
!define MUI_WELCOMEPAGE_TITLE $(WelcomeTitle)
!define MUI_WELCOMEPAGE_TEXT $(WelcomeText)
!define MUI_WELCOMEFINISHPAGE_BITMAP "img\welcome.bmp2"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP "img\welcome.bmp2"
!insertmacro MUI_PAGE_WELCOME

# License Page
!define MUI_LICENSEPAGE_TEXT_BOTTOM $(LicenseText)
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"

# Scam page
Page custom ScamWarningPage ScamWarningPageLeave
Var Dialog
Var ScamCheckbox
Var ScamState

# Directory Page
!define MUI_DIRECTORYPAGE_TEXT_TOP $(DirectoryTitle)
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION $(DirectoryText)
!define MUI_PAGE_CUSTOMFUNCTION_LEAVE DirPageLeave
!insertmacro MUI_PAGE_DIRECTORY

# Mirror selection
Page custom SelectMirrorPage SelectMirrorPageLeave
Var MirrorSelection
Var PyPi
Var RadioGitLab
Var RadioGitHub
Var RadioSourceForge
Var RadioCNB
Var PyPiMirrorSelection
Var pip_mirror_opts

# Shortcuts
Page custom ShortcutSelectionPage ShortcutSelectionPageLeave
Var StartMenuShortcut
Var DesktopShortcut
Var CheckStartMenu
Var CheckDesktop

# Installation Page
!insertmacro MUI_PAGE_INSTFILES

# Finish Page
!define MUI_FINISHPAGE_TITLE $(FinishTitle)
!define MUI_FINISHPAGE_TEXT $(FinishText)

!define MUI_FINISHPAGE_SHOWREADME "https://ets2la.com"
!define MUI_FINISHPAGE_SHOWREADME_TEXT $(WebsiteText)
!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED

!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT $(LaunchText)
!define MUI_FINISHPAGE_RUN_FUNCTION LaunchETS2LA

!insertmacro MUI_PAGE_FINISH

# Block if directory not empty
Function DirPageLeave
    IfFileExists "$INSTDIR\*.*" 0 dirEmpty
        MessageBox MB_ICONSTOP|MB_OK $(DirectoryNotEmpty)
        Abort
    dirEmpty:
FunctionEnd

# Mirror page def
Function SelectMirrorPage
    !insertmacro MUI_HEADER_TEXT $(MirrorHeader) $(MirrorHeaderDescription)
    nsDialogs::Create 1018
    Pop $0
    ${If} $0 == error
        Abort
    ${EndIf}

    # Create a label
    ${NSD_CreateLabel} 0 0 100% 24u $(MirrorTitle)
    Pop $0

    # Create radio buttons for mirrors
    ${NSD_CreateRadioButton} 0 30u 100% 12u "GitLab"
    Pop $RadioGitLab
    ${NSD_CreateRadioButton} 0 45u 100% 12u "GitHub"
    Pop $RadioGitHub
    ${NSD_CreateRadioButton} 0 60u 100% 12u "SourceForge"
    Pop $RadioSourceForge
    ${NSD_CreateRadioButton} 0 75u 100% 12u "CNB"
    Pop $RadioCNB
    # Create a label for PyPi mirror selection
    ${NSD_CreateLabel} 0 95u 100% 12u "PyPi Mirror:"
    Pop $0
    # Create a ComboBox for PyPi mirrors
    ${NSD_CreateComboBox} 0 110u 100% 12u ""
    Pop $PyPiMirrorSelection
    ${NSD_CB_AddString} $PyPiMirrorSelection "Default (pypi.org)"
    ${NSD_CB_AddString} $PyPiMirrorSelection "Aliyun"
    ${NSD_CB_AddString} $PyPiMirrorSelection "USTC (China)"
    SendMessage $PyPiMirrorSelection ${CB_SETCURSEL} 0 0

    # Set default selection (GitLab)
    ${NSD_SetState} $RadioGitLab ${BST_CHECKED}

    # Show the dialog
    nsDialogs::Show
FunctionEnd

Function SelectMirrorPageLeave
    ${NSD_GetState} $RadioGitLab $0
    ${If} $0 == ${BST_CHECKED}
        StrCpy $MirrorSelection "GitLab"
    ${Else}
        ${NSD_GetState} $RadioGitHub $0
        ${If} $0 == ${BST_CHECKED}
            StrCpy $MirrorSelection "GitHub"
        ${Else}
            ${NSD_GetState} $RadioSourceForge $0
            ${If} $0 == ${BST_CHECKED}
                StrCpy $MirrorSelection "SourceForge"
            ${Else}
                ${NSD_GetState} $RadioCNB $0
                ${If} $0 == ${BST_CHECKED}
                    StrCpy $MirrorSelection "CNB"
                ${EndIf}
            ${EndIf}
        ${EndIf}
    ${EndIf}

    SendMessage $PyPiMirrorSelection ${CB_GETCURSEL} 0 0 $PyPi
FunctionEnd

# Scam page def
Function ScamWarningPage
    !insertmacro MUI_HEADER_TEXT $(ScamWarningHeader) $(ScamWarningHeaderDescription)
    nsDialogs::Create 1018
    Pop $Dialog
    ${If} $Dialog == error
        Abort
    ${EndIf}

    # Create a label with warning text
    ${NSD_CreateLabel} 0 0 100% 60u $(ScamWarningTitle)
    Pop $0

    # Create checkbox that must be checked
    ${NSD_CreateCheckBox} 0 70u 100% 20u $(ScamWarningCheckbox)
    Pop $ScamCheckbox

    # Show the page
    nsDialogs::Show
FunctionEnd

Function ScamWarningPageLeave
    ${NSD_GetState} $ScamCheckbox $ScamState
    ${If} $ScamState != ${BST_CHECKED}
        MessageBox MB_ICONEXCLAMATION $(ScamWarningNotChecked)
        Abort
    ${EndIf}
FunctionEnd

# Shortcut page def
Function ShortcutSelectionPage
    !insertmacro MUI_HEADER_TEXT $(ShortcutHeader) $(ShortcutHeaderDescription)
    nsDialogs::Create 1018
    Pop $0
    ${If} $0 == error
        Abort
    ${EndIf}

    # Create a label
    ${NSD_CreateLabel} 0 0 100% 24u $(ShortcutSelectionTitle)
    Pop $0

    # Create checkboxes for shortcuts
    ${NSD_CreateCheckBox} 0 30u 100% 12u $(CreateStartMenuShortcut)
    Pop $CheckStartMenu
    ${NSD_CreateCheckBox} 0 50u 100% 12u $(CreateDesktopShortcut)
    Pop $CheckDesktop

    # Set default states (checked by default)
    ${NSD_SetState} $CheckStartMenu ${BST_CHECKED}
    ${NSD_SetState} $CheckDesktop ${BST_UNCHECKED}

    # Show the dialog
    nsDialogs::Show
FunctionEnd

Function ShortcutSelectionPageLeave
    ${NSD_GetState} $CheckStartMenu $0
    ${If} $0 == ${BST_CHECKED}
        StrCpy $StartMenuShortcut "1"
    ${Else}
        StrCpy $StartMenuShortcut "0"
    ${EndIf}

    ${NSD_GetState} $CheckDesktop $0
    ${If} $0 == ${BST_CHECKED}
        StrCpy $DesktopShortcut "1"
    ${Else}
        StrCpy $DesktopShortcut "0"
    ${EndIf}
FunctionEnd

Section "Python" SEC01
    # Copy python
    SetOutPath "$INSTDIR\system\python"
    File /r "3rd-party\python\*.*"
    File /r "3rd-party\python\*"

    # Copy tkinter
    File /r "3rd-party\tkinter-standalone-main\3.12\python_embedded\*"

    # Install pip
    DetailPrint $(InstallingPip)
    nsExec::ExecToLog '"$INSTDIR\system\python\python.exe" "$INSTDIR\system\python\get-pip.py"'
    Pop $0
    ${If} $0 != 0
        MessageBox MB_ICONSTOP|MB_OK $(PipInstallError)
        Abort $(PipInstallError)
    ${EndIf}
SectionEnd

Section "Git" SEC02
    # Set output path for Git
    SetOutPath "$INSTDIR\system\git"
    File /r "3rd-party\git-for-windows\*.*"
    File /r "3rd-party\git-for-windows\*"
SectionEnd

Section "Download" SEC03
    # Set the output path for the app directory
    SetOutPath "$INSTDIR\app"

    DetailPrint "$(Cloning) $MirrorSelection"
    Sleep 1000

    # Clone the repository based on the selected mirror with progress
    ${If} $MirrorSelection == "GitLab"
        nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${GITLAB_URL} .'
    ${ElseIf} $MirrorSelection == "GitHub"
        nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${GITHUB_URL} .'
    ${ElseIf} $MirrorSelection == "SourceForge"
        nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${SOURCEFORGE_URL} .'
    ${ElseIf} $MirrorSelection == "CNB"
        nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${CNB_URL} .'
    ${EndIf}

    # Check if git clone was successful
    Pop $0
    ${If} $0 != 0
        MessageBox MB_ICONSTOP|MB_OK $(GitCloneError)
        DetailPrint $(GitCloneFailed)
        # Try another mirror automatically
        ${If} $MirrorSelection == "GitLab"
            DetailPrint $(TryingAnotherMirror)
            DetailPrint "GitHub"
            nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${GITHUB_URL} .' $0
            Pop $0
            ${If} $0 != 0
                DetailPrint $(TryingAnotherMirror)
                DetailPrint "SourceForge"
                nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${SOURCEFORGE_URL} .' $0
                Pop $0
                ${If} $0 != 0
                    DetailPrint $(TryingAnotherMirror)
                    DetailPrint "CNB"
                    nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${CNB_URL} .' $0
                    Pop $0
                    ${If} $0 != 0
                        MessageBox MB_ICONSTOP|MB_OK $(AllMirrorsFailed)
                        Abort $(InstallationAborted)
                    ${EndIf}
                ${EndIf}
            ${EndIf}
        ${ElseIf} $MirrorSelection == "GitHub"
            DetailPrint $(TryingAnotherMirror)
            DetailPrint "GitLab"
            nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${GITLAB_URL} .' $0
            Pop $0
            ${If} $0 != 0
                DetailPrint $(TryingAnotherMirror)
                DetailPrint "SourceForge"
                nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${SOURCEFORGE_URL} .' $0
                Pop $0
                ${If} $0 != 0
                    DetailPrint $(TryingAnotherMirror)
                    DetailPrint "CNB"
                    nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${CNB_URL} .' $0
                    Pop $0
                    ${If} $0 != 0
                        MessageBox MB_ICONSTOP|MB_OK $(AllMirrorsFailed)
                        Abort $(InstallationAborted)
                    ${EndIf}
                ${EndIf}
            ${EndIf}
        ${ElseIf} $MirrorSelection == "SourceForge"
            DetailPrint $(TryingAnotherMirror)
            DetailPrint "GitLab"
            nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${GITLAB_URL} .' $0
            Pop $0
            ${If} $0 != 0
                DetailPrint $(TryingAnotherMirror)
                DetailPrint "GitHub"
                nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${GITHUB_URL} .' $0
                Pop $0
                ${If} $0 != 0
                    DetailPrint $(TryingAnotherMirror)
                    DetailPrint "CNB"
                    nsExec::ExecToLog '"$INSTDIR\system\git\bin\git.exe" clone --quiet --depth=20 --branch=${BRANCH} --single-branch ${CNB_URL} .' $0
                    Pop $0
                    ${If} $0 != 0
                        MessageBox MB_ICONSTOP|MB_OK $(AllMirrorsFailed)
                        Abort $(InstallationAborted)
                    ${EndIf}
                ${EndIf}
            ${EndIf}
        ${EndIf}
    ${EndIf}

    # Verify that the repository was cloned successfully by checking README and requirements
    ${If} ${FileExists} "$INSTDIR\app\README.md"
    ${AndIf} ${FileExists} "$INSTDIR\app\requirements.txt"
        DetailPrint $(GitCloneSuccess)
    ${Else}
        MessageBox MB_ICONSTOP|MB_OK $(IncompleteRepo)
        Abort $(InstallationAborted)
    ${EndIf}

    # Install python requirements
    StrCpy $pip_mirror_opts ""
    ${If} $PyPi == "1" # Aliyun
        StrCpy $pip_mirror_opts '--index-url https://mirrors.aliyun.com/pypi/simple/'
    ${ElseIf} $PyPi == "2" # USTC
        StrCpy $pip_mirror_opts '--index-url https://mirrors.ustc.edu.cn/pypi/simple'
    ${EndIf}

    DetailPrint $(PythonRequirements)
    nsExec::ExecToLog '"$INSTDIR\system\python\python.exe" -m pip install --verbose --no-warn-script-location $pip_mirror_opts --no-cache-dir wheel setuptools poetry requests'
    DetailPrint $(PythonTakesLong)
    nsExec::ExecToLog '"$INSTDIR\system\python\python.exe" -m pip install --verbose --no-warn-script-location $pip_mirror_opts --no-cache-dir -r "$INSTDIR\app\requirements.txt"'
SectionEnd

Section "Executables" SEC04
    SetOutPath "$INSTDIR"
    File /r "executables\*.*"
    File /r "executables\*"

    SetOutPath "$INSTDIR\system"
    File /r "img\favicon.ico"

    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ETS2LA" "DisplayName" "ETS2LA"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ETS2LA" "UninstallString" "$INSTDIR\ETS2LA-Uninstaller.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ETS2LA" "InstallLocation" "$INSTDIR"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ETS2LA" "DisplayIcon" "$INSTDIR\system\favicon.ico"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ETS2LA" "Publisher" "ETS2LA Team"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ETS2LA" "DisplayVersion" "0.3.0"
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ETS2LA" "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ETS2LA" "NoRepair" 1
SectionEnd

Section "Create Shortcuts" SEC05
    # Create Start Menu shortcut
    ${If} $StartMenuShortcut == "1"
        CreateDirectory "$SMPROGRAMS\ETS2LA"
        CreateShortCut "$SMPROGRAMS\ETS2LA\ETS2LA.lnk" "$INSTDIR\start.bat" "" "$INSTDIR\system\favicon.ico"
    ${EndIf}

    # Create Desktop shortcut
    ${If} $DesktopShortcut == "1"
        CreateShortCut "$DESKTOP\ETS2LA.lnk" "$INSTDIR\start.bat" "" "$INSTDIR\system\favicon.ico"
    ${EndIf}
SectionEnd

Function LaunchETS2LA
    Exec '"$INSTDIR\start.bat"'
FunctionEnd

Section "Copy Uninstaller" SEC06
    WriteUninstaller "$INSTDIR\ETS2LA-Uninstaller.exe"
SectionEnd

# Uninstaller Section
Section "Uninstall"
    # Remove installed files
    Delete "$INSTDIR\start.bat"
    Delete "$INSTDIR\app\*.*"
    Delete "$INSTDIR\system\python\*.*"
    Delete "$INSTDIR\system\git\*.*"
    Delete "$INSTDIR\*.*"

    # Remove directories
    RMDir /r "$INSTDIR\app"
    RMDir /r "$INSTDIR\system\python"
    RMDir /r "$INSTDIR\system\git"
    RMDir /r "$INSTDIR\system"
    RMDir /r "$INSTDIR\executables"
    RMDir /r "$INSTDIR"

    # Remove uninstaller
    Delete "$INSTDIR\ETS2LA-Uninstaller.exe"

    # Remove registry entries
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ETS2LA"

    # Remove Start Menu shortcut
    Delete "$SMPROGRAMS\ETS2LA\ETS2LA.lnk"
    RMDir "$SMPROGRAMS\ETS2LA"

    # Remove Desktop shortcut
    Delete "$DESKTOP\ETS2LA.lnk"

    DetailPrint "Uninstallation complete."
SectionEnd

!include "languages.nsh"
