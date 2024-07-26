from allowable_math import *
from tkinter import *

import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
from tkinter import ttk
from PIL import Image
    

def get_alls():
# print all allowables for currently selected property; works for both sorted and unsorted
    try:
        return [data_select.get_allowable(chosen_quantity.get(), all_types=True), data_select.get_ps(chosen_quantity.get()), 
                np.mean(data_select.df[chosen_quantity.get()].values.astype(float)), np.std(data_select.df[chosen_quantity.get()].values.astype(float), ddof=1)]
    except: 
        return [dataset.get_allowable(chosen_quantity.get(), all_types=True), dataset.get_ps(chosen_quantity.get()),
                np.mean(dataset.df[chosen_quantity.get()].values.astype(float)), np.std(dataset.df[chosen_quantity.get()].values.astype(float), ddof=1)]

    


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
    allowable_norm, allowable_gamma, allowable_weib = allowables
    p_norm,p_gamma, p_weib = ps
    
    Label(frame_text, text=q, fg='blue').grid()
    Label(frame_text, text=f'Mean: {mean:.2f}; StDev: {stdev:.2f}').grid()
    Label(frame_text, text=f'Normal method: {allowable_norm:.3f}, p = {p_norm:.2f}').grid()
    Label(frame_text, text=f'Weibull (ish) method: {allowable_weib:.3f}, p = {p_weib:.2f}').grid()
    Label(frame_text, text=f'Gamma method: {allowable_gamma:.3f}, p = {p_gamma:.2f}').grid()
    if len(all_sorts)==0:
        Label(frame_text, text='Unsorted').grid()
    else:
        # texts = []
        # for pair in all_sorts:
        #     texts.append(f'{pair[0]}: {pair[1]}')
        Label(frame_text, text=all_sorts).grid()

    def save():
        filename = filedialog.asksaveasfilename(filetypes=[('JPEG', '*.jpeg'), ('All Files', '*.*')])
        fig.savefig(filename)

    Button(frame_text, text='Save Latest Distribution', command=save).grid()
            

def plot_temp(frame_plot, *args):
    # fig, axs = plt.subplots()
    fig = Figure()
    axs = fig.add_subplot(111)

    q = chosen_quantity.get()


    try:
        temp_fit, r2 = data_select.plot_temperature(q, temp.get(), rt.get(), ax=axs, deg=degree.get())
    except:
        temp_fit, r2 = dataset.plot_temperature(q, temp.get(), rt.get(), ax=axs, deg=degree.get())

    canvas2 = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas2.draw()

    canvas2.get_tk_widget().grid()

    np.set_printoptions(precision=3)
    Label(frame_plot, text=f'Temperature fit (ax^n + bx^(n-1) + ...): {temp_fit}').grid()
    np.set_printoptions(precision=5)
    Label(frame_plot, text=f'R2 = {r2}').grid()
    print(f'Temperature fit: {temp_fit}')
    print(f'R2 = {r2}')


def get_files(frame_browse, frame_selections, frame_plots, frame_text):
# INPUTS:
    # frame_browse: frame for browse file button, opened file text, choose quantity button, and new sort button
    # frame_selections: frame for selected quantities and options

# open file from file explorer, prints path
    global path
    path = filedialog.askopenfilename(title = "Select a File", filetypes = (("Excel files", "*.xlsx*"), ("CSV files", "*.csv"), ("all files", "*.*")))

    label_file_explorer = Label(frame_browse, fg = "blue")
    label_file_explorer.configure(text="File Opened: "+path)

    na_values = ["", "#N/A", "#N/A N/A", "#NA", "-1.#IND", "-1.#QNAN","-NaN", "-nan", "1.#IND", "1.#QNAN", "<NA>", "N/A", 
#              "NA", 
             "NULL", "NaN", "n/a", "nan", "null"]

# opens excel file as subset class from allowable_math
    global dataset
    try:  
        try:  # excel file
            try:  # no pre-header rows
                dataset = subset(pd.read_excel(path, keep_default_na=False, na_values=na_values)[pd.read_excel(path)['MC'].notna()])
            except:
                dataset = subset(pd.read_excel(path, skiprows=1, keep_default_na=False, na_values=na_values)[pd.read_excel(path, skiprows=1)['MC'].notna()])
        except:  # csv file
            try:  # no pre-header rows
                dataset = subset(pd.read_csv(path, keep_default_na=False, na_values=na_values)[pd.read_csv(path)['MC'].notna()])
            except:
                dataset = subset(pd.read_csv(path, skiprows=1, keep_default_na=False, na_values=na_values)[pd.read_csv(path, skiprows=1)['MC'].notna()])
    except:
        print("There's something wrong with your file format. Try checking your MC header")


# creates variable, tracer, and dropdown menu for quantity you want to analyze
    global chosen_quantity
    chosen_quantity = StringVar()
    chosen_quantity.set("Property")
    quantity_label = Label(frame_browse, text="Choose Property to Analyze: ")
    quantity_label.grid()
    drop = OptionMenu(frame_browse, chosen_quantity, *dataset.headers).grid(row=quantity_label.grid_info()['row'], column=quantity_label.grid_info()['column']+1)

# temperature curve
    global degree
    degree = IntVar()
    degree.set("Degree")
    degree_label = Label(frame_browse, text='Temperature Fit Polynomial Order: ')
    degree_label.grid()
    drop_t = OptionMenu(frame_browse, degree, *[1, 2, 3, 4]).grid(row=degree_label.grid_info()['row'], column=degree_label.grid_info()['column']+1)

    global temp 
    temp = StringVar()
    temp.set("Temperature Column")
    temp.trace_add("write", lambda a, b, c: OptionMenu(frame_browse, rt, *list(set(dataset.df[temp.get()]))).grid(row=rt_label.grid_info()['row'], column=rt_label.grid_info()['column']+1))
    temp_label = Label(frame_browse, text="Choose Temperature Data for Temperature Curve: ")
    temp_label.grid()
    button_temp = OptionMenu(frame_browse, temp, *dataset.headers)
    button_temp.grid(row=temp_label.grid_info()['row'], column=temp_label.grid_info()['column']+1)

    global rt 
    rt = StringVar()
    rt.set("RT")
    rt_label = Label(frame_browse, text='Choose RT Value: ')
    rt_label.grid()
    # Button(frame_browse, text='debug rt', command= lambda: print(rt.get())).grid()

    Button(frame_browse, text='Plot distributions', command= lambda: display(frame_plots, frame_text)).grid()
    Button(frame_browse, text='Plot Temperature', command = lambda: plot_temp(frame_plots)).grid()


# creates button for initiating a new sort
    button_sort = Button(frame_selections, text = "New Sort", command = lambda: select(frame_selections)).grid()
    global all_sorts
    all_sorts = []

# sorting 
    def select(frame):
        def get_sort(*args):
            def sort_mult(sel, *args):
                print(sel[0])
                all_sorts.append([sort_by.get(), sel])

                global data_select 
                try:
                    data_select = data_select.sort(sort_by.get(), sel)
                except:
                    data_select = dataset.sort(sort_by.get(), sel)
            
            mult_sv = Listbox(frame, selectmode="multiple", exportselection=0, height=len(list(set(dataset.df[sort_by.get()]))))
            for value in list(set(dataset.df[sort_by.get()])):
                mult_sv.insert(END, value)
            
            def update_selection():
                global selected
                selected = [mult_sv.get(idx) for idx in mult_sv.curselection()]

            mult_sv.bind("<<ListboxSelect>>", lambda _: update_selection())
            mult_sv.grid()

            print_sortvars = Button(frame, text='Sort', command = lambda: sort_mult(selected)).grid()
            

    # begin sort
        sort_by = StringVar()
        sort_by.set('Sort By')
        sort_by.trace_add("write", get_sort)

        # dropdown for quantities
        drop_s = OptionMenu(frame, sort_by, *dataset.headers)
        drop_s.grid()
