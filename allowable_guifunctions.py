from allowable_math import *
from tkinter import *

import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog

    

def get_alls():
# print all allowables for currently selected property; works for both sorted and unsorted
    try:
        return [data_select.get_allowable(chosen_quantity.get(), all_types=True), data_select.get_ps(chosen_quantity.get()), 
                np.mean(data_select.df[chosen_quantity.get()]), np.std(data_select.df[chosen_quantity.get()])]
    except: 
        return [dataset.get_allowable(chosen_quantity.get(), all_types=True), dataset.get_ps(chosen_quantity.get()),
                np.mean(dataset.df[chosen_quantity.get()]), np.std(dataset.df[chosen_quantity.get()])]

    


def display(frame_plots, frame_text, c=None, r=None, *args):
# display distribution plots with calculated allowable for currently selected property in sorted or unsorted dataset; takes in frame input and grid column/row input
    # fig, axs = plt.subplots()
    fig = Figure()
    axs = fig.add_subplot(111)

    q = chosen_quantity.get()

    try:
        data_select.plot_dists(q, ax=axs)
    except:
        dataset.plot_dists(q, ax=axs)


    canvas = FigureCanvasTkAgg(fig, master=frame_plots)   
    canvas.draw() 
    
    if c or r is None:
        canvas.get_tk_widget().grid() 
    else:
        canvas.get_tk_widget().grid(column=c, row=r)

    allowables, ps, mean, stdev = get_alls()
    allowable_norm, allowable_weib, allowable_gamma = allowables
    p_norm, p_weib, p_gamma = ps
    

    Label(frame_text, text=f'Mean: {mean:.2f}; StDev: {stdev:.2f}').grid()
    Label(frame_text, text=f'Normal method: {allowable_norm:.3f}, p = {p_norm:.2f}').grid()
    Label(frame_text, text=f'Weibull (ish) method: {allowable_weib:.3f}, p = {p_weib:.2f}').grid()
    Label(frame_text, text=f'Gamma method: {allowable_gamma:.3f}, p = {p_gamma:.2f}').grid()


def plot_temp(frame):
    # fig, axs = plt.subplots()
    fig = Figure()
    axs = fig.add_subplot(111)

    q = chosen_quantity.get()

    try:
        data_select.plot_temperature(q, ax=axs)
    except:
        dataset.plot_temperature(q, ax=axs)

    canvas2 = FigureCanvasTkAgg(fig, master=frame)
    canvas2.draw()

    canvas2.get_tk_widget().grid()


def get_files(frame_browse, frame_selections, frame_plots, frame_text):
# INPUTS:
    # frame_browse: frame for browse file button, opened file text, choose quantity button, and new sort button
    # frame_selections: frame for selected quantities and options

# open file from file explorer, prints path
    global path
    path = filedialog.askopenfilename(initialdir = r'/', title = "Select a File", filetypes = (("Excel files", "*.xlsx*"), ("all files", "*.*")))

    label_file_explorer = Label(frame_browse, fg = "blue")
    label_file_explorer.configure(text="File Opened: "+path)

# opens excel file as subset class from allowable_math
    global dataset
    dataset = subset(pd.read_excel(path)[pd.read_excel(path)['MC'].notna()])

# creates variable, tracer, and dropdown menu for quantity you want to analyze
    global chosen_quantity
    chosen_quantity = StringVar()
    chosen_quantity.set("Choose Quantity")
    chosen_quantity.trace_add("write", lambda a, b, c: display(frame_plots, frame_text))
    drop = OptionMenu(frame_browse, chosen_quantity, *dataset.headers).grid()

# temperature curve
    button_temp = Button(frame_browse, text="Plot Temperature Curve", command = lambda: plot_temp(frame_text)).grid()

# creates button for initiating a new sort
    button_sort = Button(frame_browse, text = "New Sort", command = lambda: select(frame_selections)).grid()

# sorting 
    def select(frame):
        def get_sort(*args):
            def get_sort_var(*args):
            # sort data
                # convert value you are sorting by (ie RT) to flaot if it is numeric; else keep as string
                sv = sort_var.get()
                try:
                    sv = float(sv)
                except:
                    sv = sv

                # create variable for sorted data; if data has already been sorted, further sort the sorted data; else sort original data
                global data_select 
                try:
                    data_select = data_select.sort(sort_by.get(), sv)
                except:
                    data_select = dataset.sort(sort_by.get(), sv)
            
        # get column you are sorting by (ie Temperature) and the options in that column
            sort_var = StringVar()
            sort_var.set("Sort Variable")
            sort_var.trace_add("write", get_sort_var)

            # dropdown for options
            drop_sv = OptionMenu(frame, sort_var, *list(set(dataset.df[sort_by.get()]))).grid()

    # begin sort
        sort_by = StringVar()
        sort_by.set('Sort By')
        sort_by.trace_add("write", get_sort)

        # dropdown for quantities
        drop_s = OptionMenu(frame, sort_by, *dataset.headers).grid()
