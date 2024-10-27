#pylint: disable=line-too-long
"""_summary_
"""
import argparse
import logging
import os
import csv

# Import File Dialog
from tkinter import Tk, filedialog

from time import sleep

import nidaqmx as ni
from nidaqmx.constants import LineGrouping, VoltageUnits

VERSION = "Beta 5"
COMPAT_MODELS = "USB-6001, USB-6002, USB-6003"
DESCRIPTION = "Software to generate stimulation sequences using a NI DAQ"
COMPATIBILITY = f"Compatible models:{COMPAT_MODELS}"

# Const for Logging
LOG_LEVELS = {"DEBUG": logging.DEBUG,
              "INFO": logging.INFO,
              "WARNING": logging.WARNING,
              "ERROR": logging.ERROR,
              "CRITICAL": logging.CRITICAL}
LOG_FILE = "stimseq.log"

#########################
# Const for csv parsing #
#########################

# Columns of the sequence file, in order
# OUTPUT_ADDITION_SECTION
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
]

# Minimum accepted increment between time steps
MIN_TIMESTEP = 50

# Timeout for write operations to the DAQ
WRITE_TIMEOUT = 10

# Type convertions for each column
# OUTPUT_ADDITION_SECTION
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
}

# Regrouping of columns by output type
# - bool = DO
# - float = AO
DO_DATA_KEYS = [key for key in SEQUENCE_COLUMNS if SEQUENCE_TYPES[key] == bool]
AO_DATA_KEYS = [key for key in SEQUENCE_COLUMNS if SEQUENCE_TYPES[key] == float]

# Acceptable range for AO data
AO_RANGE = [-10, 10]

# Name of the DAQ as defined in NI MAX
DAQ_NAME = "Dev1"

# Const for DAQ Wiring
# OUTPUT_ADDITION_SECTION
DAQ_WIRING = [
    VALVES_DO := f"{DAQ_NAME}/port0/line0:7",
    PIEZO_DO := f"{DAQ_NAME}/port1/line0",
    LED_AO := f"{DAQ_NAME}/ao0",
    TTL_DI := f"{DAQ_NAME}/port2/line0",
    HEARBIT_DO := f"{DAQ_NAME}/port1/line1",
]


# Method to check if string contains a number
def _is_number(value:str) -> bool:
    """ Method to check if string contains a number

    Args:
        value (str): input string

    Returns:
        bool: Returns True if string represent a number.
    """
    try:
        float(value)
    except ValueError:
        return False
    return True


class StimSeq():
    """ Stimseq main class handling the logic
    """
    def __init__(
            self,
            path_to_sequence:str,
            log_file:str=os.path.join(os.path.dirname(__file__), LOG_FILE),
            log_lvl=logging.INFO
        ) -> None:

        # Save argyments as attributes
        self.__log_file = log_file
        self.__log_lvl = log_lvl
        self.__sequence:tuple[dict[str, int | float | bool]]

        # Init Logger
        self.__init_logger()

        # Parse the Sequence
        self.seq_path = path_to_sequence

    @property
    def seq_path(self) -> str:
        """ Reader for __seq_path """
        return self.__seq_path

    @seq_path.setter
    def seq_path(self, path_to_sequence:str) -> None:
        """ Setter for __seq_path """
        # Raise error if invalid path
        if not os.path.isfile(path_to_sequence):
            raise argparse.ArgumentTypeError(f"{path_to_sequence} is not a valid path")

        self.__seq_path = path_to_sequence

        # Parse sequence when sequence path is changed
        self._parse_sequence()

    def __init_logger(self) -> None:
        # Create a logger
        self.__logger = logging.getLogger('my_logger')
        self.__logger.setLevel(self.__log_lvl)

        # Create a formatter to define the log format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',)

        # Create a file handler to write logs to a file
        file_handler = logging.FileHandler(self.__log_file)
        file_handler.setLevel(self.__log_lvl)
        file_handler.setFormatter(formatter)

        # Create a stream handler to print logs to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.__log_lvl)
        console_handler.setFormatter(formatter)

        # Add the handlers to the logger
        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(console_handler)

    @property
    def logger(self) -> logging.Logger:
        """ Reader for __logger """
        return self.__logger

    @property
    def log_file(self) -> str:
        """ Reader for __log_file """
        return self.__log_file

    @property
    def log_lvl(self) -> int:
        """ Reader for __log_lvl """
        return self.__log_lvl

    @property
    def sequence(self) -> tuple[dict[str, int | float | bool]]:
        """ Reader for __sequence """
        return self.__sequence

    def __type_convert(self, value:str, column:str) -> bool | int | float:
        """ Method to ensure proper conversion of data from csv"""
        if SEQUENCE_TYPES[column] == bool:
            return bool(int(value))
        return SEQUENCE_TYPES[column](value)

    def _parse_sequence(self) -> None:
        """ Parse the sequence file.
        """
        self.__logger.info("Parsing sequence file: %s", self.__seq_path)

        with open(self.__seq_path, 'r', encoding='utf-8', newline='') as f:
            # Load into a dict reader while skipping line starting with a *
            reader = csv.DictReader(filter(lambda line: not line.startswith('*'), f),
                                    fieldnames=SEQUENCE_COLUMNS, skipinitialspace=True,
                                    restval="MISSING VAL", restkey="Comment")

            # tmp dict to save sequence
            tmp_seq:list[dict[str, int | float | bool]] = []

            # For loop through csv row by row
            for i, row in enumerate(reader):
                self.__logger.debug("Parsing row: %s", row)
                # Skip rows when a column has an invalid value (Empty or not an integer)
                if any(not _is_number(row[col]) for col in SEQUENCE_COLUMNS):
                    self.__logger.warning("Skipped Row %i because an invalid value was found", i)
                    continue

                # Skip line if analog value outside acceptable range is found
                if not all(min(AO_RANGE) <= int(row[key]) <= max(AO_RANGE) for key in AO_DATA_KEYS):
                    self.__logger.warning("Skipped Row %i because Analog Output data is out of range (min: %s, max: %s)",
                                            i, min(AO_RANGE), max(AO_RANGE))
                    continue

                # Check Time Steps Validity
                if tmp_seq:
                    # Compute time increment with previous parsed row
                    time_increment = SEQUENCE_TYPES[TIMESTAMP](row[TIMESTAMP]) - tmp_seq[-1][TIMESTAMP]

                    # Skip rows when time step are incoherent
                    if  time_increment < MIN_TIMESTEP :
                        self.__logger.warning("Skipped Row %i because time increment with previous steps is too small (got: %s, min: %s)",
                                            i, time_increment, MIN_TIMESTEP)
                        continue
                else :
                    # Force 0 if first valid row has a negative Timestep
                    if  SEQUENCE_TYPES[TIMESTAMP](row[TIMESTAMP]) <= 0 :
                        self.__logger.warning("Time step for first row has negative value: forcing zero")
                        row[TIMESTAMP] = '0'

                # Append line to list
                tmp_seq.append({col: self.__type_convert(row[col], col) for col in SEQUENCE_COLUMNS})

            # Save sequence to a tuple in order to prevent editing by mistake
            self.__sequence = tuple(tmp_seq)
            if self.__logger.isEnabledFor(logging.DEBUG):
                for step in self.__sequence:
                    self.__logger.debug("Parsed sequence: %s", step)

    #pylint: disable=too-many-locals
    def run_sequence(self, enable_heartbeat:bool=True) -> None:
        """Execute the sequence from the computer

        Args:
            enable_heartbeat (bool, optional): Enables a heartbeat signal, changing state with every new generated sample. Defaults to True.
        """

        with (
            ni.Task("Digital Outputs") as task_do,
            ni.Task("Trigger") as task_trig,
            ni.Task("Analog Outputs") as task_ao,
        ):
            time_data:list[float] = []
            do_data:list[int] = []
            ao_data:list[float] = []
            heartbit_value = False

            # Prepare data arrangement
            do_data_step_size = len(DO_DATA_KEYS) + (1 if enable_heartbeat else 0)
            ao_data_step_size = len(AO_DATA_KEYS)

            # Prepare sequence data for DAQ Generation
            self.__logger.info("Prepare sequence data for DAQ Generation")
            for i, step in enumerate(self.__sequence):
                time_data.append((step[TIMESTAMP] - self.__sequence[i - 1][TIMESTAMP]) if i else step[TIMESTAMP])

                # Prepare digital output values
                for key in DO_DATA_KEYS:
                    do_data.append(step[key])

                # If heartbit enabled, add heartbit signal to digital output
                # changing from True to False with every time step
                if enable_heartbeat:
                    do_data.append(heartbit_value := not heartbit_value)

                # preapre Analog output Values
                for key in AO_DATA_KEYS:
                    ao_data.append(step[key])
            self.__logger.debug("time_data: %s", time_data)
            self.__logger.debug("do_data: %s", do_data)
            self.__logger.debug("ao_data: %s", ao_data)

            # Compute sequence size
            seq_size = len(time_data)

            # Check all data lists are of the same size
            if not all((seq_size == len(ao_data)/ao_data_step_size, len(do_data)/do_data_step_size)):
                self.__logger.critical("Incoherent size between prepared output data")
                raise ValueError


            self.__logger.info("Init DAQ Channels")
            # Init Digital Output Channels
            # OUTPUT_ADDITION_SECTION
            task_do.do_channels.add_do_chan(lines=VALVES_DO, name_to_assign_to_lines="Valves",
                                            line_grouping=LineGrouping.CHAN_PER_LINE)
            task_do.do_channels.add_do_chan(lines=PIEZO_DO, name_to_assign_to_lines="Piezo",
                                            line_grouping=LineGrouping.CHAN_PER_LINE)

            # Init Analog Output Channels
            # OUTPUT_ADDITION_SECTION
            task_ao.ao_channels.add_ao_voltage_chan(physical_channel=LED_AO, name_to_assign_to_channel="LED",
                                                    min_val=min(AO_RANGE), max_val=min(AO_RANGE), units=VoltageUnits.VOLTS)

            # Add Heartbeat to digital output channels
            if enable_heartbeat:
                task_do.do_channels.add_do_chan(lines=HEARBIT_DO, name_to_assign_to_lines="HeartBeat",
                                                line_grouping=LineGrouping.CHAN_PER_LINE)

            # Init digital input channel for trigger signal
            task_trig.di_channels.add_di_chan(lines=TTL_DI, name_to_assign_to_lines="TTL IN",
                                              line_grouping=LineGrouping.CHAN_PER_LINE)

            # Wait for trigger signal
            self.__logger.info("Waiting for trigger signal on %s", TTL_DI)
            trig = 0
            while trig == 0:
                trig = task_trig.read()
            self.__logger.info("Trigger signal received")

            # Execute sequence
            for i in range(seq_size):
                sleep(time_data[i] / 1000)
                task_do.write(do_data[i*do_data_step_size : i*do_data_step_size + do_data_step_size])
                task_ao.write(ao_data[i*ao_data_step_size : i*ao_data_step_size + ao_data_step_size])
                self.__logger.debug("Sent do: %s", do_data[i*do_data_step_size : i*do_data_step_size + do_data_step_size])
                self.__logger.debug("Sent ao: %s", ao_data[i*ao_data_step_size : i*ao_data_step_size + ao_data_step_size])

            # Reset outputs to 0 for safety reasons
            # The reset occurs after a pause equals to last timesteps
            sleep(time_data[-1] / 1000)
            task_do.write([False,]* do_data_step_size)
            task_ao.write([0,]* ao_data_step_size)
            self.__logger.info("Reseted outputs to O")

            self.__logger.info("Finished sending sequence")

# Method to validate a path given through command line
def _file_path(file_path:str) -> str:
    if os.path.isfile(file_path):
        return file_path

    raise argparse.ArgumentTypeError(f"{file_path} is not a valid path")



# Execute when this file is executed directly
if __name__ == "__main__" :

    # Parse command line arguments if any
    parser = argparse.ArgumentParser(prog=f"Stimseq {VERSION}",
                                     description=DESCRIPTION,
                                     epilog=COMPATIBILITY)
    parser.add_argument('--path', dest="seq_path", type=_file_path,
                        help="The path to the sequence file")
    parser.add_argument('--log', dest="log_lvl", type=str,
                        help="The log level desired, log above chosen level will be registered",
                        choices=LOG_LEVELS.keys())
    parser.add_argument('--disable-heartbeat', dest="disable_heartbeat",
                        help="Used to disable heartbeat signal",
                        action='store_true')
    args = parser.parse_args()


    # Open a File Picker Dialog if no path given through cli
    if not args.seq_path :
        root = Tk()
        root.withdraw()

        # Ask User to select the sequence file
        args.seq_path = filedialog.askopenfilename(defaultextension=".csv",
                                                   initialdir=os.getcwd(),
                                                   filetypes=[(".csv","*.csv")])

    # Init stimseq
    stimseq = StimSeq(path_to_sequence=args.seq_path,
                      log_lvl=LOG_LEVELS[args.log_lvl or "DEBUG"],
                      log_file=os.path.join(os.path.dirname(__file__), LOG_FILE))

    # Run Stimseq
    stimseq.run_sequence(enable_heartbeat=not args.disable_heartbeat)
