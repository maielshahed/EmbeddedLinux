
from tkinter import *

frm=Tk()

canvas = Canvas()

def ledon():
    Label(frm,text="Led Is On").pack()
    canvas.create_oval(110,10,210,110,outline = "blue", fill = "orange",width = 2)
    canvas.pack(pady=10)
    
    


def ledoff():
    Label(frm,text="Led Is Off").pack()
    canvas.create_oval(110,10,210,110,outline = "blue",fill = "white",width = 2)
    canvas.pack(pady=10)
    

frm.title("Mai El Shahed")
#frm.geometry("200x200+150+200")
frm.configure(background='black')
Button(frm, text="Led ON", command=ledon).pack(pady=10)
Button(frm, text="Led OFF", command=ledoff).pack(pady=10)

frm.mainloop()



