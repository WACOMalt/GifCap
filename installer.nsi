!include "MUI2.nsh"

Name "GifCap"
OutFile "GifCap_Installer.exe"
InstallDir "$PROGRAMFILES64\GifCap"
InstallDirRegKey HKCU "Software\bsums.xyz.gifcap" ""
RequestExecutionLevel admin

!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "GifCap" SecGifCap
  SetOutPath "$INSTDIR"
  
  ; Install Files
  File "nsis_build\gifcap.exe"
  File "nsis_build\README.md"
  
  SetOutPath "$INSTDIR\resources"
  File /r "nsis_build\resources\*"
  
  ; Write Uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Registry Keys
  WriteRegStr HKCU "Software\bsums.xyz.gifcap" "" $INSTDIR
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GifCap" "DisplayName" "GifCap"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GifCap" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GifCap" "DisplayIcon" "$INSTDIR\resources\icons\bsums.xyz.gifcap.png"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GifCap" "Publisher" "BSums.xyz"
  
  ; Start Menu Shortcut
  CreateDirectory "$SMPROGRAMS\GifCap"
  CreateShortcut "$SMPROGRAMS\GifCap\GifCap.lnk" "$INSTDIR\gifcap.exe" "" "$INSTDIR\resources\icons\bsums.xyz.gifcap.png" 0
  CreateShortcut "$SMPROGRAMS\GifCap\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\gifcap.exe"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir /r "$INSTDIR\resources"
  RMDir "$INSTDIR"
  
  Delete "$SMPROGRAMS\GifCap\GifCap.lnk"
  Delete "$SMPROGRAMS\GifCap\Uninstall.lnk"
  RMDir "$SMPROGRAMS\GifCap"

  DeleteRegKey HKCU "Software\bsums.xyz.gifcap"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\GifCap"
SectionEnd

Function .onInit
  ${If} ${Silent}
    ; Silent install logic (handled automatically by NSIS /S flag usually, but checking here if needed)
  ${EndIf}
FunctionEnd
