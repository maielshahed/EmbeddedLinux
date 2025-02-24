
from tkinter import *
from tkinter import ttk
'''
root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()

ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
root.mainloop()


'''


frm=Tk()

def led_on():
    print('Hello Mai El Shahed')


def Hello_World():
    print('Hello_World')


frm.title("Mai El Shahed")
#frm.geometry("200x200+150+200")
frm.configure(background='black')
ttk.Button(frm, text="Hello Mai", command=led_on).grid(column=1, row=0)
ttk.Button(frm, text="Quit", command=frm.destroy).grid(column=0, row=1)
ttk.Button(frm, text="Hello Mai", command=Hello_World).grid(column=1, row=2)
ttk.Button(frm, text="Quit", command=frm.destroy).grid(column=2, row=1)
frm.mainloop()
