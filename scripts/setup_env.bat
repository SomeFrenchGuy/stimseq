@echo off

echo "This will setup the environment for Stimseq."
echo "Previous environment will be replaced"

:start
SET choice=
SET /p choice="Are You sure ? [y,n]:"
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
ECHO "Leaving environment setup without modifications"
PAUSE
EXIT

:yes
IF EXIST .env ECHO Y | RMDIR /s .env
ECHO "Generating Python virtual environment"
python -m venv .env
CALL .\.env\Scripts\activate.bat
pip install -r requirements.txt
ECHO "Python virtual environment generated"


:start_install_driver
SET choice=
SET /p choice="Do you want to install NIDAQmx driver ? [y,n]:"
IF NOT '%choice%'=='' SET choice=%choice:~0,1%
IF '%choice%'=='Y' GOTO install_driver
IF '%choice%'=='y' GOTO install_driver
IF '%choice%'=='N' GOTO no_install_driver
IF '%choice%'=='n' GOTO no_install_driver
IF '%choice%'=='' GOTO no_install_driver
ECHO "%choice%" is not valid
ECHO.
GOTO start_install_driver



:install_driver
ECHO "Installating NIDAQmx Driver"
python -m nidaqmx installdriver
ECHO "Installation of NIDAQmx Driver Completed !"
GOTO end

:no_install_driver
ECHO "Skip installation of NIDAQmx Driver"


:end
ECHO "Environment Setup Completed !"
PAUSE
EXIT


