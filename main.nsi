Unicode True

!include "MUI2.nsh"
!include "nsDialogs.nsh"

RequestExecutionLevel user

# Variables
InstallDir "C:\ETS2LA"
!define BRANCH "rewrite"
!define GITLAB_URL "https://gitlab.com/ETS2LA/ETS2LA"
!define GITHUB_URL "https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist.git"
!define SOURCEFORGE_URL "https://git.code.sf.net/p/eurotrucksimulator2-laneassist/code"

!define MIRROR_NAME "Aliyun PyPi Mirror"
!define MIRROR_URL "https://mirrors.aliyun.com/pypi/simple/"

# Installer Information
Name "ETS2LA"
BrandingText $(BrandingText)
Icon "img\favicon.ico"
OutFile "ETS2LA-2.0-Windows-Installer.exe"

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

# Directory Page
!define MUI_DIRECTORYPAGE_TEXT_TOP $(DirectoryTitle)
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION $(DirectoryText)
!insertmacro MUI_PAGE_DIRECTORY

# Mirror selection
Page custom SelectMirrorPage SelectMirrorPageLeave

# Shortcuts
Page custom ShortcutSelectionPage ShortcutSelectionPageLeave

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

# Mirror page def
Var MirrorSelection
Var PyPi
Var RadioGitLab
Var RadioGitHub
Var RadioSourceForge
Var PyPiMirrorSelection
Function SelectMirrorPage
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
    # Toggle to enable/disable Aliyun mirror
    ${NSD_CreateCheckBox} 0 80u 100% 12u "${MIRROR_NAME}"
    Pop $PyPiMirrorSelection

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
            ${EndIf}
        ${EndIf}
    ${EndIf}

    ${NSD_GetState} $PyPiMirrorSelection $0
    ${If} $0 == ${BST_CHECKED}
        StrCpy $PyPi "Mirror"
    ${Else}
        StrCpy $PyPi "Pypi"
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
    ExecWait '"$INSTDIR\system\python\python.exe" "$INSTDIR\system\python\get-pip.py"'
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

    DetailPrint $(Cloning)
    DetailPrint $MirrorSelection
    Sleep 1000

    # Clone the repository based on the selected mirror with progress
    ${If} $MirrorSelection == "GitLab"
        ExecWait '"$INSTDIR\system\git\bin\git.exe" clone --progress --depth=20 --branch=${BRANCH} --single-branch ${GITLAB_URL} .'
    ${ElseIf} $MirrorSelection == "GitHub"
        ExecWait '"$INSTDIR\system\git\bin\git.exe" clone --progress --depth=20 --branch=${BRANCH} --single-branch ${GITHUB_URL} .'
    ${ElseIf} $MirrorSelection == "SourceForge"
        ExecWait '"$INSTDIR\system\git\bin\git.exe" clone --progress --depth=20 --branch=${BRANCH} --single-branch ${SOURCEFORGE_URL} .'
    ${EndIf}

    # Install python requirements
    ${If} $PyPi == "Pypi"

        DetailPrint $(PythonRequirements)
        ExecWait '"$INSTDIR\system\python\python.exe" -m pip install --no-warn-script-location --no-cache-dir wheel setuptools poetry requests'
        DetailPrint $(PythonTakesLong)
        ExecWait '"$INSTDIR\system\python\python.exe" -m pip install --no-warn-script-location --no-cache-dir -r "$INSTDIR\app\requirements.txt"'

    ${ElseIf} $PyPi == "Mirror"

        DetailPrint $(PythonRequirements)
        ExecWait '"$INSTDIR\system\python\python.exe" -m pip install --no-warn-script-location --index-url ${MIRROR_URL} --no-cache-dir wheel setuptools poetry requests'
        DetailPrint $(PythonTakesLong)
        ExecWait '"$INSTDIR\system\python\python.exe" -m pip install --no-warn-script-location --index-url ${MIRROR_URL} --no-cache-dir -r "$INSTDIR\app\requirements.txt"'

    ${EndIf}
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
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ETS2LA" "DisplayVersion" "0.2.0"
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ETS2LA" "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\ETS2LA" "NoRepair" 1
SectionEnd

# Variables for shortcut options
Var StartMenuShortcut
Var DesktopShortcut
Var CheckStartMenu
Var CheckDesktop

Function ShortcutSelectionPage
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
    Delete "$INSTDIR\executables\*.*"
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