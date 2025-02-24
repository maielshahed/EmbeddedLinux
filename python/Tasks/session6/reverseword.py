from tkinter import *

def login():

    print(word.get()[::-1])
    
root=Tk()
txt=Label(root,text="Enter a word").grid(row=0)
word=Entry(root)

word.grid(row=0,column=1)

log=Button(root,text="reverse",command=login).grid(row=2,column=1)


root.mainloop()