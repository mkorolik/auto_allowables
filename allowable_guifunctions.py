from allowable_math import *
from tkinter import *

import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog

    

def get_all_allows():
# print all allowables for currently selected property; works for both sorted and unsorted
    try:
        data_select.get_allowable(chosen_quantity.get(), all_types=True)
    except: 
        dataset.get_allowable(chosen_quantity.get(), all_types=True)
    


def display(frame_plots, frame_text, c=None, r=None, *args):
# display distribution plots with calculated allowable for currently selected property in sorted or unsorted dataset; takes in frame input and grid column/row input
    fig, axs = plt.subplots()

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

    allowables_text = 'allowable numbers will go here :)'
    Label(frame_text, text=allowables_text).grid()


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
