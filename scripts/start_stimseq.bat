@echo off

CALL .\.env\Scripts\activate.bat
python .\stimseq.py --log INFO

PAUSE
EXIT