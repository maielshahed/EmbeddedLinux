
'''
Create a graphical application in Python Tkinter that asks 
the user to enter two integers and displays their sum 
'''
from tkinter import *


def show():
    
   

    if v.get()==1:
        x=e1.get()
        y=e2.get()
        sum = int(x) + int(y)
        Label(root,text=f"The Sum Is: {x} + {y} ={sum}",background='black',fg ='yellow').grid(row=3,column=1)
       
    elif v.get()==2:
        x=e1.get()
        y=e2.get()
        sup = int(x) - int(y)
        Label(root,text=f"The Sup Is: {x} - {y} ={sup}",background='black',fg ='yellow').grid(row=3,column=1)
       
    
   

root=Tk()
root.geometry("400x400+125+100")
root.configure(background='black')

Label(root,text="Enter the value of M",background='black',fg ='yellow').grid(row=0)
Label(root,text="Enter the value of N",background='black',fg ='yellow').grid(row=1)


e1=Entry(root,background='green',fg='white')
e2=Entry(root,background='green',fg='white')
#مربع هيكتب فيه  الكلام  
e1.grid(row=0,column=1)
e2.grid(row=1,column=1)


log=Button(root,text="Submit",command=show,width=17, fg ='blue',background='yellow',bd=5).grid(row=4,column=1)
v=IntVar() 
Radiobutton(root,text='Sum',variable=v,value=1,background='black',fg ='green').grid(row=5,column=0)
Radiobutton(root,text='Sup',variable=v,value=2,background='black',fg ='green').grid(row=6,column=0)



root.mainloop()
