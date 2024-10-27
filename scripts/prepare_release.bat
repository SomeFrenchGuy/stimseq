@echo off

echo "Make sure to have update the Version name in stimseq.py before continuing"

:start
SET choice=
SET /p choice="do you want to continue ? [y,n]:"
IF NOT '%choice%'=='' SET choice=%choice:~0,1%
IF '%choice%'=='Y' GOTO yes
IF '%choice%'=='y' GOTO yes
IF '%choice%'=='N' GOTO no
IF '%choice%'=='n' GOTO no
IF '%choice%'=='' GOTO no
ECHO "%choice%" is not valid
ECHO.
GOTO start

:no
ECHO "Exiting without modifications"
PAUSE
EXIT

:yes
IF EXIST bin ECHO Y | RMDIR /s bin
ECHO "Copying file"
COPY setup_env.bat ..\bin\setup_env.bat
COPY start_stimseq_gui.bat ..\bin\start_stimseq_gui.bat
COPY start_stimseq_no_gui.bat ..\bin\start_stimseq_no_gui.bat
COPY ..\src\stimseq.py ..\bin\stimseq.py
COPY ..\src\stimseq_gui.py ..\bin\stimseq_gui.py
COPY ..\requirements.txt ..\bin\requirements.txt
COPY ..\doc ..\bin\doc

ECHO "Release preparation finished"
ECHO "Do not forget to generate README.pdf"
ECHO "Use stimseq-<version>.zip for archive generation"

PAUSE
EXIT