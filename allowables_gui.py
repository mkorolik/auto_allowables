from tkinter import *
from tkinter import ttk

from allowable_math import *
import pandas as pd

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from tkinter import filedialog


## FUNCTIONS

def is_float_try(str):
    try:
        float(str)
        return True
    except ValueError:
        return False
    

def display(*args):
    fig, axs = plt.subplots()

    q = chosen_quantity.get()

    try:
        data_select.plot_dists(q, ax=axs)
    except:
        dataset.plot_dists(q, ax=axs)


    canvas = FigureCanvasTkAgg(fig, master = window)   
    canvas.draw() 
  
    canvas.get_tk_widget().grid() 
  
    # toolbar = NavigationToolbar2Tk(canvas, window) 
    # toolbar.update() 
  
    # canvas.get_tk_widget().grid() 

    

def get_allows():
    try:
        data_select.get_allowable(chosen_quantity.get(), all_types=True)
    except:
        dataset.get_allowable(chosen_quantity.get(), all_types=True)


def get_files():
    global path
    path = filedialog.askopenfilename(initialdir = r'C:\Users\mkorolik\Downloads', title = "Select a File", filetypes = (("Excel files", "*.xlsx*"), ("all files", "*.*")))

    label_file_explorer.configure(text="File Opened: "+path)

    global dataset
    dataset = subset(pd.read_excel(path)[pd.read_excel(path)['MC'].notna()])

    
    global chosen_quantity
    chosen_quantity = StringVar()
    chosen_quantity.set("Choose Quantity")
    chosen_quantity.trace_add("write", display)




    def select():
        def get_sort(*args):
            def get_sort_var(*args):
                sv = sort_var.get()
                if is_float_try(sv):
                    sv = float(sv)
                    print(sv)

                global data_select

                try:
                    data_select = data_select.sort(sort_by.get(), sv)
                except:
                    data_select = dataset.sort(sort_by.get(), sv)


            sort_var = StringVar()
            sort_var.set("Sort Variable")
            sort_var.trace_add("write", get_sort_var)

            drop_sv = OptionMenu(window, sort_var, *list(set(dataset.df[sort_by.get()]))).grid()


        sort_by = StringVar()
        sort_by.set('Sort By')
        sort_by.trace_add("write", get_sort)

        drop_s = OptionMenu(window, sort_by, *dataset.headers).grid()

    
    button_sort = Button(window, 
                        text = "Only Include...",
                        command = select).grid()

    drop = OptionMenu(window, chosen_quantity, *dataset.headers).grid()

    button_allowables = Button(window, text="Get all allowables", command=get_allows).grid()






## Create window

root = Tk()
root.title('Autogenerate Allowable')

window = ttk.Frame(root, padding="0.5i")
window.grid(column=0, row=0)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)



## Get relevant variables (file, headers, etc)

label_file_explorer = Label(window, fg = "blue")
      
button_explore = Button(window, text = "Browse Files", command = get_files)


# scrollbar

# canvas = Canvas(window)
# canvas.grid(row=0, column=0)
# vsb = Scrollbar(window, orient='vertical', command=canvas.yview)
# vsb.grid(row=0, column=1, sticky='ns')
# canvas.configure(yscrollcommand=vsb.set)

# canvas.config(scrollregion=canvas.bbox("all"))

# etc

for child in window.winfo_children(): 
    child.grid_configure(padx=5, pady=5)


root.bind("<Return>", display)


root.mainloop()