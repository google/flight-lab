@ECHO OFF
SETLOCAL enableextensions enabledelayedexpansion

SET VSW="%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"

for /f "usebackq tokens=1* delims=: " %%a in (`!VSW! -latest -requires Microsoft.Component.MSBuild`) do (
    if /i "%%a"=="installationPath" set VSPATH=%%b
    if /i "%%a"=="installationVersion" set VSVER=%%b
)

for /f "tokens=1,2 delims=." %%a in ("!VSVER!") do (
    set VSVER=%%a.0
)
set MSBUILD=!VSPATH!\MSBuild\!VSVER!\Bin\MSBuild.exe


"!MSBUILD!" %1

ENDLOCAL