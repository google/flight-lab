# Platform Support:
#   This makefile is meant to run on Windows platform only.

TMP=..\\build\\tmp
NUGET=$(TMP)\\nuget.exe
PACKAGES_DIR=.\\packages
SIMCONNECT_SDK_DIR="%ProgramFiles(x86)%\Microsoft Games\Microsoft Flight Simulator X SDK\SDK\Core Utilities Kit\SimConnect SDK"

init: nuget-packages simconnect

build:
	cd ..\protos && $(MAKE) build
	msbuild.bat SimProxy.sln

clean:
	cmd /c if exist "${NUGET}" del $(NUGET)
	cmd /c if exist "${PACKAGES_DIR}" rmdir $(PACKAGES_DIR) /S /Q

# internal rules

$(TMP):
	mkdir $@

$(NUGET): $(TMP)
	certutil -urlcache -split -f "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe" $(NUGET)

nuget-packages: $(NUGET)	
	$(NUGET) install -o $(PACKAGES_DIR)

simconnect:
	copy $(SIMCONNECT_SDK_DIR)\\inc\\simconnect.h ..\\build\\simconnect
	copy $(SIMCONNECT_SDK_DIR)\\lib\\simconnect.lib ..\\build\\simconnect
