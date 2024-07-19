from tkinter import *
from allowable_guifunctions import *
from tkinter import ttk
from customtkinter import *

root = Tk()
root.title('Autogenerate Allowable')

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

frame1 = Frame(root, width=250, height=450)
frame1.grid(row=0, column=0, padx=10, pady=5)

frame2 = CTkScrollableFrame(root, width=600, height=450)
frame2.grid(row=0, column=1, padx=10, pady=5)

frame3 = Frame(root, width=600, height=150)
frame3.grid(row=1, column=1, padx=10, pady=5)

frame4 = Frame(root, width=250, height=150)
frame4.grid(row=1, column=0, padx=10, pady=5)

button_explore = Button(frame1, text = "Browse Files", command = lambda: get_files(frame1, frame4, frame2, frame3)).grid()

root.mainloop()
