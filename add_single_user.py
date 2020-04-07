# from FaceDetectionSSD import FaceDetectionSSD
# from Facenet import Facenet
import tkinter as tk
import utils as u
import cv2, numpy as np
import os
import imutils



def resetValues():
    sid.set("")
    sname.set("")
    specs.set(0)


def printVals():
    print(sid.get(), sname.get(), specs.get())



X, Y = 20, 10

add_window = tk.Tk()
add_window.geometry("400x300")
add_window.title("Add User Window")


sid, sname = tk.StringVar(), tk.StringVar()
specs = tk.IntVar()


tk.Label(add_window, text='Student ID').place(x=X, y=Y)
tk.Label(add_window, text='Student Name').place(x=X, y=Y+30)

idEntry = tk.Entry(add_window, width=30, textvar=sid)
nameEntry = tk.Entry(add_window, width=30, textvar=sname)
idEntry.place(x=X+140, y=Y); nameEntry.place(x=X+140, y=Y+30)

tk.Label(add_window, text='Spectacles').place(x=X, y=Y+60)
tk.Radiobutton(add_window, text='YES', variable=specs, value=1).place(x=X+140, y=Y+60)
tk.Radiobutton(add_window, text='NO', variable=specs, value=0).place(x=X+190, y=Y+60)

nextBtn = tk.Button(add_window, text="Next", width=15, command=printVals)
resetBtn = tk.Button(add_window, text="Reset", width=15, command=resetValues)
nextBtn.place(x=X+40, y=Y+110); resetBtn.place(x=X+180, y=Y+110)

add_window.mainloop()