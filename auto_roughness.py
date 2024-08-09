import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from tkinter import *
from tkinter import filedialog

from PIL import Image, ImageTk
Image.MAX_IMAGE_PIXELS = None

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def get_roughness(df):
    def ra(x, y):
        return 1/len(x) * np.sum(y)
    
    def rq(x, y):
        return (1/len(x) * np.sum(y**2))**0.5
    
    x = df.iloc[:,0]
    y = df.iloc[:,1]

    zeros = np.argwhere(y==0)
    x = np.delete(x, zeros)
    y = np.delete(y, zeros)

    m, b = np.polyfit(x, y, 1)
    y_s = y - (m*x+b)

    try:
        scale = float(input_scale.get(1.0, "end-1c"))
    except:
        print("No scale input!")

    print(scale)

    fig = Figure()
    axs = fig.add_subplot(111)
    
    axs.scatter(x, y, s=1)
    axs.plot(x, m*x+b, color='red')

    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.draw()
    canvas.get_tk_widget().grid()

    return ra(x, np.abs(y_s))/scale, rq(x, y_s)/scale


def upload_file():
    path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
    
    try:
        data = pd.read_csv(path, header=1)
    except:
        print("There's something wrong with your csv file")
    
    ra, rq = get_roughness(data)

    Label(frame_text, text=f'Ra = {ra:.3f} thou').grid()
    Label(frame_text, text=f'Rq = {rq:.3f} thou').grid()





root = Tk()
root.title('Surface Roughness Measure Tool MK')

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

frame_text = Frame(root, width=200, height=200)
frame_text.grid(row=0, column=0, padx=10, pady=5)

frame_plot = Frame(root, width=200, height=200)
frame_plot.grid(row=0, column=1, padx=10, pady=5)


text_scale = Label(frame_text, text='Input scale (pixels/thou)')
text_scale.grid()

input_scale = Text(frame_text, height=1, width=5)
input_scale.grid(row=text_scale.grid_info()['row'], column=text_scale.grid_info()['column']+1)

button_file = Button(frame_text, text="Upload File", command=upload_file)
button_file.grid()

root.mainloop()