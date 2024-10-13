import matplotlib.pyplot as plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tkinter import Tk, filedialog, Label, Frame,Button
from time import sleep


def save_plot():
    path = filedialog.asksaveasfilename(defaultextension="png")
    figure.savefig(path)
    _quit()

def _quit():
    root.quit()
    root.destroy() 

# Init TK and plot objects 
root = Tk()
root.protocol("WM_DELETE_WINDOW", _quit)
root.title("Stimseq - Plot sequence")
figure, axes = plot.subplots(nrows=2)

axes[0].scatter([1,4,6,8], [1,2,3,4])
axes[1].scatter([1,4,6,8], [1,2,3,4])


# Init tk frame
frame = Frame(root)

label = Label(text="Message above Plot")
label.config(font=("Courier", 24))
label.pack()

# Add Canvas to Frame
canvas = FigureCanvasTkAgg(figure=figure, master=frame)
canvas.get_tk_widget().pack()
canvas.draw()
frame.pack()

Button(master=frame, text="Button to save & continue", command= save_plot).pack()

root.mainloop()