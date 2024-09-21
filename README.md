# StimSeq

This repo is destined to hold code and documentation for a project made for a team of researcher at the CNRS of Paris Saclay.

Its purpose is to allow the generation of stimulation sequence using a NIDAQ USB-6001

## Installing StimSeq

- Download latest release on the right of this page.
- Extract the archive to where you want pipreq to be installed
- Run the script `setup_env.bat` to setup The environment for StimSeq

## Running StimSeq

To run stimseq, multiple options are possible.

### From batch file

- Double click on `start_stimseq.bat`
- Select the sequence file from the popup Window

### From PowerShell

After opening a shell and going to the installation directory of StimSeq :

```batch
.\.env\Scripts\Activate.ps1
python .\stimseq.py --path <path_to_sequence_file>
```

You can also use `python .\stimseq.py --help` to display more informations on usage.

### From a Python Script

```python
from stimseq import StimSeq

stimseq = StimSeq(path_to_sequence=".\sequence.csv")

stimseq.run_sequence()
```

### Expected DAQ Configuration

StimSeq expects the following DAQ configuration:

- Device named "Dev1" in NI MAX software
- Valves connected on P0.1 to P0.7
- LED connected on AO0
- PIEZO connected on P1.0
- TTL Input on P2.0

### Sequence file

A template can be found in the release in this repo under the name : [sequence_template.csv](/doc/sequence_template.csv)

## Development Environment

### Windows

- Install Git
- Clone this git repo
- Install Python 3.12 or above

To setup the Python environment you must run the following commands from the directory where the repo is cloned. Using PowerShell.

```bat
python -m venv .env
.\.env\Scripts\Activate.ps1
pip install -r requirements.txt
python -m nidaqmx installdriver
```

### Ubuntu 22.04

- Install Git
- Clone this git repo
- Install Python 3.12 or above

To setup the Python environment you must run the following commands from the directory where the repo is cloned. Using the terminal.

```bash
python -m venv .env
./.env/Scripts/activate
pip install -r requirements.txt
python -m nidaqmx installdriver
```

### Requirement file

The file `requirements.txt` contains the information needed to setup the Python environment for this project. It is generated by running the command `pip freeze > requirements.txt` after activating the virtual environment. Note that the file generated this way will contain every single python package installed with `pip` even those not used by the project, so one should always review the generated file.

## Ressources

### External Documentation

- [NIdaqmx python package](https://nidaqmx-python.readthedocs.io/en/stable/#installation) 
- [Using NI-DAQmx in Text Based Programming Environments](https://www.ni.com/en/support/documentation/supplemental/21/using-ni-daqmx-in-text-based-programming-environments.html)
- [USB-6001 Specifications](https://www.ni.com/docs/en-US/bundle/usb-6001-specs/resource/374369a.pdf)
- [TCS SP8 MP Multiphoton Microscope](https://www.leica-microsystems.com/products/confocal-microscopes/p/leica-tcs-sp8-mp/downloads/)
- [AOD Scope Vitro](https://karthalasystem.com/aodscope-vitro/)
- [Valvelink](https://autom8.com/wp-content/uploads/2016/07/ValveLink.pdf)
- [LEICA Triggerbox](https://downloads.leica-microsystems.com/TCS%20SP5/Application%20Note/Triggering_Guide-AppLetter.EN.pdf)
- [SDG 1032X](https://static.eleshop.nl/mage/media/downloads/SDG1000X_UserManual_UM0201X-E01A1.pdf)
- [LED Driver Thorlab LEDD1B](https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=2616&pn=LEDD1B#3018)
- [ValveLink 8.2 pinout](/doc/ValveLink8.2%20pinout.pdf)

### Requirements

- [NI driver](https://www.ni.com/docs/fr-FR/bundle/ni-platform-on-linux-desktop/page/installing-ni-products-ubuntu.html)
- [git](https://git-scm.com/downloads)
- [python 3.12](https://www.python.org/downloads/)