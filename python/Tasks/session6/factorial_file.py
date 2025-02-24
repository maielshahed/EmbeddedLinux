

'''
 Write a program in Python that displays a window to the user 
 that asks them to enter an integer N and displays its factorial
'''
from tkinter import *

# Python 3 program to find
# factorial of given number
import math
def factorial(n):
    return(math.factorial(n))




def show():

    x= e1.get()
    num=int(x)
    #print("Factorial of", num, "is", factorial(num))
    Label(root,text=f'The Factorial of  {num} is {factorial(num)}',background='black',fg ='yellow').grid(row=3,column=1)
      
   

root=Tk()
root.geometry("400x400+125+100")
root.configure(background='black')

Label(root,text="Enter the value of M",background='black',fg ='yellow').grid(row=0)



e1=Entry(root,background='green',fg='white')


e1.grid(row=0,column=1)



log=Button(root,text="Submit",command=show,width=17, fg ='blue',background='yellow',bd=5).grid(row=4,column=1)

root.mainloop()
