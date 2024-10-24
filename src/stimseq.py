"""_summary_
"""
import argparse
import logging
import os
import csv

# Imports for graphical interface
from tkinter import Tk, ttk, filedialog, filedialog, Frame, Button, Canvas
from time import sleep
from datetime import datetime

# Imports for plotting datas
import matplotlib.pyplot as plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import nidaqmx as ni
from nidaqmx.constants import LineGrouping, VoltageUnits

VERSION = "Beta 4"
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

# Const for plotting sequence
PLOT_STYLE = 'bo-'  #blue, dots, contiguous line

# Const for DAQ
DAQ_NAME = "Dev1"
VALVES_DO = f"{DAQ_NAME}/port0/line0:7"
PIEZO_DO = f"{DAQ_NAME}/port1/line0"
LED_AO = f"{DAQ_NAME}/ao0"
TTL_DI = f"{DAQ_NAME}/port2/line0"
WRITE_TIMEOUT = 10

# Method to check if string contains a number
def _is_number(value:str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True


class StimSeq():
    """ Stimseq main class handling the logic
    """
    def __init__(self, path_to_sequence:str, log_file:str=os.path.join(os.path.dirname(__file__), LOG_FILE), log_lvl=logging.INFO) -> None:
        self.__log_file = log_file
        self.__log_lvl = log_lvl
        self.__sequence:tuple[dict[str, int | float | bool]]

        self.__init_logger()

        self.seq_path = path_to_sequence

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
            

            # Init DAQ channels
            self.__logger.info("Init DAQ Channels")
            task_do.do_channels.add_do_chan(lines=VALVES_DO, name_to_assign_to_lines="Valves",
                                            line_grouping=LineGrouping.CHAN_PER_LINE)
            task_do.do_channels.add_do_chan(lines=PIEZO_DO, name_to_assign_to_lines="Piezo",
                                            line_grouping=LineGrouping.CHAN_PER_LINE)
            task_trig.di_channels.add_di_chan(lines=TTL_DI, name_to_assign_to_lines="TTL IN",
                                              line_grouping=LineGrouping.CHAN_PER_LINE)
            task_ao.ao_channels.add_ao_voltage_chan(physical_channel=LED_AO, name_to_assign_to_channel="LED",
                                                    min_val=0, max_val=10, units=VoltageUnits.VOLTS)
    
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
           
            self.__logger.info("Finished sending sequence")


class StimSeqGUI():
    """ Stimseq GUI handling graphical interface used to validate a sequence"""

    __base_seq_name:str

    def __init__(self,) -> None:
        #  Init TK
        self.__root = Tk()
        self.__root.protocol("WM_DELETE_WINDOW", self.__quit)
        self.__root.title("Stimseq - Plot sequence")
        self.__root.minsize(width=400, height=300)
        self.__root.withdraw()

        # Prepare drawing area. 
        # number_of_rows = Number of column minus 1 because first column is for timestamps
        self.__number_of_rows = len(SEQUENCE_COLUMNS) - 1
        self.__figure, self.__axes = plot.subplots(nrows=self.__number_of_rows,constrained_layout=True)
        self.__figure.set_figheight(1.5 * self.__number_of_rows)

        # Init tk frames, it is the main graphical unit inside the window
        self.__main_frame = Frame(self.__root)
        self.__buttons_frame = Frame(self.__main_frame)
        self.__canvas_frame = Frame(self.__main_frame)

        # Create buttons and pack them into their master frame
        self.__btn_save = Button(master=self.__buttons_frame, text="Save Plot and start sequence", command= self.__save_plot_and_run)
        self.__btn_quit = Button(master=self.__buttons_frame, text="Quit without running sequence", command= self.__quit)
        self.__btn_save.pack()
        self.__btn_quit.pack()

        # Init the canvas and pack into its master frame. This is were the plot will be drawn
        self.__scroll_canvas = Canvas(self.__canvas_frame)
        self.__canvas = FigureCanvasTkAgg(figure=self.__figure, master=self.__scroll_canvas)
        self.__cwidg = self.__canvas.get_tk_widget()
        self.__scroll_canvas.create_window(0, 0, anchor='nw', window=self.__cwidg)

        self.__scrx = ttk.Scrollbar(self.__canvas_frame, orient="horizontal", command=self.__scroll_canvas.xview)
        self.__scry = ttk.Scrollbar(self.__canvas_frame, orient="vertical", command=self.__scroll_canvas.yview)
        self.__scroll_canvas.configure(yscrollcommand=self.__scry.set, xscrollcommand=self.__scrx.set)

        self.__scroll_canvas.grid(row=1, column=0, sticky='news')
        self.__scrx.grid(row=2, column=0, sticky='ew')
        self.__scry.grid(row=1, column=1, sticky='ns')

        self.__canvas_frame.rowconfigure(1, weight=1)
        self.__canvas_frame.columnconfigure(0, weight=1)

        wi = self.__figure.get_figwidth()
        wp = self.__cwidg.winfo_reqwidth(),

        self.__scroll_canvas.configure(width=wp, height=self.__cwidg.winfo_reqheight())
        self.__scroll_canvas.configure(scrollregion=self.__scroll_canvas.bbox("all"))


        # Pack graphical objects together
        self.__buttons_frame.pack()
        self.__canvas_frame.pack()
        self.__main_frame.pack()



        # Default to false so closing the window won't start the sequence
        self.__sequence_validated = False
        
    def __quit(self) -> None:
        """ Callable to close GUI Window"""
        self.__root.quit()
        self.__root.destroy()

    def __plot_sequence(self, sequence: tuple[dict[str, int | float | bool]]) -> None:
        """Plot the sequence in the graphical interface and show it to the user

        Args:
            sequence (tuple[dict[str, int  |  float  |  bool]]): The sequence to plot
        """

        # Arrange data for plotting it
        plotable_sequence: dict[str, list[int | float | bool]] = {}
        timestamps = []
        for step in sequence:
            timestamps.append(step[TIMESTAMP])
            for key in SEQUENCE_COLUMNS:
                if key == TIMESTAMP:
                    continue
                plotable_sequence.setdefault(key, []).append(step[key])
        
        for i, (title, values) in enumerate(plotable_sequence.items()):
            self.__axes[i].plot(timestamps, values, PLOT_STYLE)
            self.__axes[i].set_ylabel(title)

        self.__canvas.draw()
        
    def show_gui(self, sequence: tuple[dict[str, int | float | bool]]) -> None:
        """ Show gui
        plot the sequence, and add buttons asking the use what he wants to do

        Args:
            sequence (tuple[dict[str, int  |  float  |  bool]]): The sequence to validate
        """
        # Plot the sequence
        self.__plot_sequence(sequence=sequence)

        # Display the window
        ws = self.__root.winfo_screenwidth()
        hs = self.__root.winfo_screenheight()
        x1 = int(ws*1/4)
        y1 = int(hs*1/3)
        x2 = int(ws*3/4) - x1
        y2 = int(hs*2/3) - y1
        self.__root.geometry(f"{x2}x{y1}+{x1}+{y2}")
        self.__root.wm_deiconify()

        # Wait for user input
        self.__root.mainloop()

        return self.__sequence_validated

    def __save_plot_and_run(self) -> None:
        """ Save the 
        """
        now = datetime.now()

        path = filedialog.asksaveasfilename(initialfile=f"{now.strftime("%Y-%m-%d_%H.%M.%S")}-{self.__base_seq_name}.png",
                                            initialdir=os.getcwd(),
                                            defaultextension="png")
        self.__figure.savefig(path)
        self.__sequence_validated = True
        self.__quit()

    def get_sequence_file_from_user(self) -> None:
        """ Opens a window to ask the user for the sequence file
        """

        path = filedialog.askopenfilename(defaultextension=".csv", initialdir=os.getcwd())
        self.__base_seq_name = os.path.basename(path)
        return path

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
    args = parser.parse_args()

    stimseq_gui = StimSeqGUI()

    # Open a File Picker Dialog if no path given through cli
    if not args.seq_path :
        args.seq_path = stimseq_gui.get_sequence_file_from_user()

    # Init stimseq
    stimseq = StimSeq(path_to_sequence=args.seq_path,
                      log_lvl=LOG_LEVELS[args.log_lvl or "DEBUG"],
                      log_file=os.path.join(os.path.dirname(__file__), LOG_FILE))
    
    # Run sequence if user clicked the save & run button
    if stimseq_gui.show_gui(sequence=stimseq.sequence):
        # Run Stimseq
        stimseq.run_sequence()
