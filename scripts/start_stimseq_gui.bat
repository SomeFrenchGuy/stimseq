@echo off

CALL .\.env\Scripts\activate.bat
python .\stimseq_gui.py --log INFO

PAUSE
EXIT