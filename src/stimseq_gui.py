#pylint: disable=line-too-long
"""_summary_
"""
import argparse
import logging
import os

# Imports for graphical interface
from tkinter import Tk, ttk, filedialog, Frame, Button, Canvas
from datetime import datetime

# Imports for plotting datas
import matplotlib.pyplot as plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import StimSeq Backend
import stimseq


# Const for plotting sequence
PLOT_STYLE = 'bo-'  #blue, dots, contiguous line


class StimSeqGUI(Tk):
    """ Stimseq GUI handling graphical interface used to validate a sequence"""

    __canvas:FigureCanvasTkAgg

    def __init__(self, log_lvl=logging.INFO, **kwargs) -> None:
        #  Init TK
        super().__init__(**kwargs)
        self.protocol("WM_DELETE_WINDOW", self.__quit)
        self.title("Stimseq - Plot sequence")
        self.minsize(width=400, height=300)
        self.withdraw()

        # Prepare drawing area.
        # number_of_rows = Number of column minus 1 because first column is for timestamps
        self.__number_of_rows = len(stimseq.SEQUENCE_COLUMNS) - 1
        self.__figure, self.__axes = plot.subplots(nrows=self.__number_of_rows,constrained_layout=True)
        self.__figure.set_figheight(1.5 * self.__number_of_rows)

        # Init Graphical interface
        self.__init_graphical_interface()

        # Get the sequence file
        self.__sequence_path = self.__get_sequence_file_from_user()

        # Init stimseq backend
        self.__stimseq = stimseq.StimSeq(path_to_sequence=self.__sequence_path,
                                         log_lvl=log_lvl)

        # Plot the sequence
        self.__plot_sequence()

        # Default to false so closing the window won't start the sequence
        self.__run_sequence = False

    def __init_graphical_interface(self) -> None:
        """ Init graphical objects inside the graphical interface
        """

        # Init tk frames, it is the main graphical unit inside the window
        main_frame = Frame(self)
        buttons_frame = Frame(main_frame)
        canvas_frame = Frame(main_frame)

        # Create buttons and pack them into their master frame
        btn_change = Button(master=buttons_frame, text="Change Sequence File", command= self.__btn_change_sequence_file)
        btn_save = Button(master=buttons_frame, text="Save Plot and start sequence", command= self.__btn_save_plot_and_start)
        btn_quit = Button(master=buttons_frame, text="Quit without running sequence", command= self.__btn_exit_no_run)
        btn_change.pack()
        btn_save.pack()
        btn_quit.pack()

        # Init the canvas and pack into its master frame. This is were the plot will be drawn
        scroll_canvas = Canvas(canvas_frame)
        self.__canvas = FigureCanvasTkAgg(figure=self.__figure, master=scroll_canvas)
        cwidg = self.__canvas.get_tk_widget()
        scroll_canvas.create_window(0, 0, anchor='nw', window=cwidg)

        scrx = ttk.Scrollbar(canvas_frame, orient="horizontal", command=scroll_canvas.xview)
        scry = ttk.Scrollbar(canvas_frame, orient="vertical", command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scry.set, xscrollcommand=scrx.set)

        scroll_canvas.grid(row=1, column=0, sticky='news')
        scrx.grid(row=2, column=0, sticky='ew')
        scry.grid(row=1, column=1, sticky='ns')

        canvas_frame.rowconfigure(1, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        wp = cwidg.winfo_reqwidth(),

        scroll_canvas.configure(width=wp, height=cwidg.winfo_reqheight())
        scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))


        # Pack graphical objects together
        buttons_frame.pack()
        canvas_frame.pack()
        main_frame.pack()

    def __quit(self) -> None:
        """ Callable to close GUI Window"""
        self.quit()
        self.destroy()

    def __plot_sequence(self,) -> None:
        """Plot the sequence in the graphical interface and show it to the user

        """

        # Arrange data for easy plot
        plotable_sequence: dict[str, list[int | float | bool]] = {}
        timestamps = []
        for step in self.__stimseq.sequence:
            timestamps.append(step[stimseq.TIMESTAMP])
            for key in stimseq.SEQUENCE_COLUMNS:
                if key == stimseq.TIMESTAMP:
                    continue
                plotable_sequence.setdefault(key, []).append(step[key])

        # Plot the sequence column by column
        for i, (title, values) in enumerate(plotable_sequence.items()):
            self.__axes[i].plot(timestamps, values, PLOT_STYLE)
            self.__axes[i].set_ylabel(title)

        # Set sequence filename as figure Title
        self.__figure.suptitle(f"{os.path.basename(self.__sequence_path)}", fontsize=16)

        self.__canvas.draw()

    def mainloop(self, n=0) -> None:
        """ Show gui
        plot the sequence, and add buttons asking the use what he wants to do

        Args:
            sequence (tuple[dict[str, int  |  float  |  bool]]): The sequence to validate
        """
        # Display the window
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x1 = int(ws*1/4)
        y1 = int(hs*1/3)
        x2 = int(ws*3/4) - x1
        y2 = int(hs*2/3) - y1
        self.geometry(f"{x2}x{y1}+{x1}+{y2}")
        self.wm_deiconify()

        # Wait for user input
        super().mainloop(n=n)

        # Run sequence only if requested
        if self.__run_sequence:
            self.__stimseq.run_sequence()

    def __get_sequence_file_from_user(self) -> None:
        """ Opens a window to ask the user for the sequence file
        """

        path = filedialog.askopenfilename(defaultextension=".csv", initialdir=os.getcwd())
        self.__base_seq_name = os.path.basename(path)
        return path

    def __btn_save_plot_and_start(self) -> None:
        """ Callback to save the plot and run the sequence
        """
        now = datetime.now()

        path = filedialog.asksaveasfilename(initialfile=f"{now.strftime("%Y-%m-%d_%H.%M.%S")}-{self.__base_seq_name}.png",
                                            initialdir=os.getcwd(),
                                            defaultextension="png")
        self.__figure.savefig(path)
        self.__run_sequence = True
        self.__quit()

    def __btn_change_sequence_file(self) -> None:
        """Callback for changing the selected sequence file
        """
        # Get a new sequence file and plot it
        self.__sequence_path = self.__get_sequence_file_from_user()
        self.__plot_sequence()

        # Load new sequence file into stimseq backend
        self.__stimseq.seq_path = self.__sequence_path

    def __btn_exit_no_run(self) -> None:
        """ Callback for quitiing without reunning the sequence
        """
        self.__run_sequence = False
        self.__quit()






# Method to validate a path given through command line
def _file_path(file_path:str) -> str:
    if os.path.isfile(file_path):
        return file_path

    raise argparse.ArgumentTypeError(f"{file_path} is not a valid path")




# Execute when this file is executed directly
if __name__ == "__main__" :

    # Parse command line arguments if any
    parser = argparse.ArgumentParser(prog=f"Stimseq {stimseq.VERSION}",
                                     description=stimseq.DESCRIPTION,
                                     epilog=stimseq.COMPATIBILITY)
    parser.add_argument('--log', dest="log_lvl", type=str,
                        help="The log level desired, log above chosen level will be registered",
                        choices=stimseq.LOG_LEVELS.keys())
    args = parser.parse_args()

    stimseq_gui = StimSeqGUI(log_lvl=stimseq.LOG_LEVELS[args.log_lvl or "DEBUG"])

    stimseq_gui.mainloop()
