@ECHO OFF
cls
:begin
ECHO Setup
regedit /s data\settings.reg
ECHO Starting controller...
python main.py %1
GOTO begin
