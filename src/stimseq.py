"""_summary_
"""
import argparse
import logging
import os
import csv

from tkinter import Tk, filedialog
from time import sleep

import nidaqmx as ni
from nidaqmx.constants import LineGrouping, VoltageUnits, CountDirection, Edge

VERSION = "Beta 3"
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

# Const for csv parsing
MIN_TIMESTEP = 50
TIMESTAMP = "Timestamp"
VALVE1 = "V1"
VALVE2 = "V2"
VALVE3 = "V3"
VALVE4 = "V4"
VALVE5 = "V5"
VALVE6 = "V6"
VALVE7 = "V7"
VALVE8 = "V8"
LED = "LED"
PIEZO = "Piezo"
SEQUENCE_COLUMNS = [
    TIMESTAMP,
    VALVE1,
    VALVE2,
    VALVE3,
    VALVE4,
    VALVE5,
    VALVE6,
    VALVE7,
    VALVE8,
    LED,
    PIEZO,
]
# Type convertions for each column
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


# Const for DAQ
DAQ_NAME = "/Dev1"
VALVES_DO = f"{DAQ_NAME}/port0/line0:7"
PIEZO_DO = f"{DAQ_NAME}/port1/line0"
LED_AO = f"{DAQ_NAME}/ao0"
TTL_INPUT = f"{DAQ_NAME}/PFI0"
WRITE_TIMEOUT = 10

# Method to check if string contains a number
def _is_number(value:str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True


class StimSeq():
    """_summary_
    """
    def __init__(self, path_to_sequence:str, log_file:str=os.path.join(os.path.dirname(__file__), LOG_FILE), log_lvl=logging.INFO) -> None:
        self.__log_file = log_file
        self.__log_lvl = log_lvl
        self.__sequence:tuple[dict[str, int | float | bool]]

        self.__init_logger()

        self.seq_path = path_to_sequence

    def __init_logger(self):
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
    def sequence(self) -> dict[str, tuple[int]]:
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

            # For through csv row by row
            for i, row in enumerate(reader):
                self.__logger.debug("Parsing row: %s", row)
                # Skip rows when a column has an invalid value (Empty or not an integer)
                if any(not _is_number(row[col]) for col in SEQUENCE_COLUMNS):
                    self.__logger.warning("Skipped Row %i because an invalid value was found", i)
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

    def run_sequence(self) -> None:
        """ Execute the sequence from the computer """

        with (
            ni.Task("Digital Outputs") as task_do,
            ni.Task("Trigger") as task_trig,
            ni.Task("Analog Outputs") as task_ao,
        ):
            time_data:list[float] = []
            do_data:list[int] = []
            ao_data:list[float] = []

            # Prepare data arrangement
            do_data_keys = [VALVE1, VALVE2, VALVE3, VALVE4, VALVE5, VALVE6, VALVE7, VALVE8, PIEZO]
            ao_data_keys = [LED]
            do_data_step_size = len(do_data_keys)
            ao_data_step_size = len(ao_data_keys)

            # Prepare sequence data for DAQ Generation
            self.__logger.info("Prepare sequence data for DAQ Generation")
            for i, step in enumerate(self.__sequence):
                print(f"step {i} : {step}")
                time_data.append((step[TIMESTAMP] - self.__sequence[i - 1][TIMESTAMP]) if i else step[TIMESTAMP])
                
                for key in do_data_keys:
                    do_data.append(step[key])
                
                for key in ao_data_keys:
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

            # Init DAQ output channels
            self.__logger.info("Init DAQ output Channels")
            task_do.do_channels.add_do_chan(lines=VALVES_DO, name_to_assign_to_lines="Valves",
                                            line_grouping=LineGrouping.CHAN_PER_LINE)
            task_do.do_channels.add_do_chan(lines=PIEZO_DO, name_to_assign_to_lines="Piezo",
                                            line_grouping=LineGrouping.CHAN_PER_LINE)
            task_ao.ao_channels.add_ao_voltage_chan(physical_channel=LED_AO, name_to_assign_to_channel="LED",
                                                    min_val=0, max_val=10, units=VoltageUnits.VOLTS)
        
            # Init Trigger Channel
            self.__logger.info("Init Trigger Channel")
            trig_chan = task_trig.ci_channels.add_ci_count_edges_chan(counter=f"{DAQ_NAME}/ctr0", edge=Edge.RISING,
                                                                      initial_count=0, count_direction=CountDirection.COUNT_UP)
            trig_chan.ci_count_edges_term = TTL_INPUT
    
            # Wait for trigger signal
            self.__logger.info("Waiting for trigger signal on %s", TTL_INPUT)
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
           
            self.__logger.info("Finished sending sequence")


# Method to validate a path given through command line
def _file_path(file_path:str) -> str:
    if os.path.isfile(file_path):
        return file_path

    raise argparse.ArgumentTypeError(f"{file_path} is not a valid path")

class StimSeqGUI():
    
    def __init__(self):
        pass

    def plot_sequence(self):
        pass

    def save_plot(self):
        pass

    def get_sequence_file(self):
        pass

    def quit(self):
        pass

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
    args = parser.parse_args()


    # Open a File Picker Dialog if no path given through cli
    if not args.seq_path :
        root = Tk()
        root.withdraw()

        args.seq_path = filedialog.askopenfilename(defaultextension=".csv", initialdir=os.getcwd())

    # Init stimseq
    stimseq = StimSeq(path_to_sequence=args.seq_path,
                      log_lvl=LOG_LEVELS[args.log_lvl or "INFO"],
                      log_file=os.path.join(os.path.dirname(__file__), LOG_FILE))

    # Run Stimseq
    stimseq.run_sequence()
