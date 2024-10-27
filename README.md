# StimSeq

This repo is destined to hold code and documentation for a the Stimseq Project.

Its purpose is to allow the generation of stimulation sequence using a NIDAQ USB-6001.

This NIDAQ USB model being one of the simplest, this code can probably be used with other NIDAQ USB models with little to no modification. One must still stay carefull and read the appropriate documentation when doing so. This statement is without any engagement from the author in case of issues encoutered while using this software on any other device.

## Configuration

### Expected DAQ Configuration

StimSeq expects the following DAQ configuration:

- Device named "Dev1" in NI MAX software
- Valves connected on P0.1 to P0.7
- LED connected on AO0
- PIEZO connected on P1.0
- TTL Input on P2.0
- HeartBeat output on P1.1

### Sequence file

A template can be found in the release in this repo under the name : [sequence_template.csv](/doc/sequence_template.csv)

## Adding an output

StimSeq can easily be modified to include new outputs. One must be carefull to read the [DAQ documentation](https://www.ni.com/docs/en-US/bundle/usb-6001-specs/resource/374369a.pdf) when doing so.

To add an output the following process must be followed:

- Add a column to the `.csv` sequence file **before** the `comment` column
- Append to `SEQUENCE_COLUMNS` a new column identifier using this syntax: `IDENTIFIER := "Name",`
- Append to `SEQUENCE_TYPES` the type of data using this syntax: `IDENTIFIER : type,` (`bool` for DO, `float` for AO)
- Append to `DAQ_WIRING` the output wiring informations using this syntax `OUTPUT_ID := f"{DAQ_NAME}/output_location"`
- Add channels in method `run_sequence()` according to the type of output (AO or DO)

All the part of the code needing modification for this are marked with a `OUTPUT_ADDITION_SECTION` comment.

### Example

For example, if we wanted to add an analog output on `ao1` for a motor we would do the following:

- Append `MOTOR := "Motor",` to `SEQUENCE_COLUMNS`
- Append `MOTOR: float,` to `SEQUENCE_TYPES`
- Append `MOTOR_AO := f"{DAQ_NAME}/ao1,"` to `DAQ_WIRING`
- Add a new line with `task_ao.ao_channels.add_ao_voltage_chan(...)` to the channels initialization in `run_sequence()`

This would look like this (`(...)` is used to show code missing from the example):

```python
#(...)

SEQUENCE_COLUMNS = [
    TIMESTAMP := "Timestamp",
    VALVE1 := "V1",
    VALVE2 := "V2",
    VALVE3 := "V3",
    VALVE4 := "V4",
    VALVE5 := "V5",
    VALVE6 := "V6",
    VALVE7 := "V7",
    VALVE8 := "V8",
    LED := "LED",
    PIEZO := "Piezo",
    MOTOR := "Motor",
]
#(...)

SEQUENCE_TYPES = {
    TIMESTAMP: int,
    VALVE1: bool,
    VALVE2: bool,
    VALVE3: bool,
    VALVE4: bool,
    VALVE5: bool,
    VALVE6: bool,
    VALVE7: bool,
    VALVE8: bool,
    LED: float,
    PIEZO: bool,
    MOTOR: float,
}
#(...)

# Name of the DAQ as defined in NI MAX
DAQ_NAME = "Dev1"

# Const for DAQ Wiring
DAQ_WIRING = [
    VALVES_DO := f"{DAQ_NAME}/port0/line0:7",
    PIEZO_DO := f"{DAQ_NAME}/port1/line0",
    LED_AO := f"{DAQ_NAME}/ao0",
    TTL_DI := f"{DAQ_NAME}/port2/line0",
    HEARBIT_DO := f"{DAQ_NAME}/port1/line1",
    MOTOR_AO := f"{DAQ_NAME}/ao1",
]
#(...)

class StimSeq():
    #(...)
    def run_sequence(self, enable_heartbeat:bool=True) -> None:
    #(...)
            task_ao.ao_channels.add_ao_voltage_chan(physical_channel=LED_AO, name_to_assign_to_channel="LED",
                                                    min_val=min(AO_RANGE), max_val=min(AO_RANGE), units=VoltageUnits.VOLTS)
            task_ao.ao_channels.add_ao_voltage_chan(physical_channel=MOTOR_AO, name_to_assign_to_channel="MOTOR",
                                                    min_val=min(AO_RANGE), max_val=min(AO_RANGE), units=VoltageUnits.VOLTS)
```

## Installing StimSeq

- Download latest release on the right of this page.
- Extract the archive to where you want pipreq to be installed
- Run the script `setup_env.bat` to setup The environment for StimSeq

## Running StimSeq GUI

StimSeq Graphical User Interface (GUI) will plot the selected sequence. It allows the user to change file, save the plot and run the sequence, or quit without running the sequence.

To run StimSeq with a GUI, multiple options are possible.

### From batch file

- Double click on `start_stimseq_gui.bat`
- Select the sequence file from the popup Window
- A GUI appears with a plot showwing the selected sequence
- Click on `Save Plot and start sequence` to Run the sequence

### From PowerShell

After opening a shell and going to the installation directory of StimSeq :

```batch
.\.env\Scripts\Activate.ps1
python .\stimseq_gui.py --log INFO
```

You can also use `python .\stimseq_gui.py --help` to display more informations on usage.

### From a Python Script

```python
from stimseq_gui import StimSeqGUI

stimseq_gui = StimSeqGUI()

stimseq_gui.mainloop()
```

## Running StimSeq without the GUI

To run StimSeq without the GUI, multiple options are possible.

***Note:** The sequence selected will be exectued without plotting it or asking for confirmation*

### From batch file

- Double click on `start_stimseq_gui.bat`
- Select the sequence file from the popup Window

### From PowerShell 

After opening a shell and going to the installation directory of StimSeq :

```batch
.\.env\Scripts\Activate.ps1
python .\stimseq.py --path <path_to_sequence_file> --log INFO
```

You can also use `python .\stimseq.py --help` to display more informations on usage.

### From a Python Script

```python
from stimseq import StimSeq

stimseq = StimSeq(path_to_sequence=".\sequence.csv")

stimseq.run_sequence()
```

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
