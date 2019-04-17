import tkinter
from tkinter.messagebox import *
from tkinter import filedialog
from tkinter.simpledialog import askinteger
from .AmbiNoiseDataSource import AmbiNoiseDataSource


class Launcher(tkinter.Tk):
    def __init__(self):
        super(Launcher, self).__init__()
        btnInput = tkinter.Button(self, text="来源目录", command=self.askInput)
        btnInput.pack()
        btnOutput = tkinter.Button(self, text="来源目录", command=self.askOutput)
        btnOutput.pack()
        EValue = 0
        NValue = 0
        ZValue = 1
        FValue = 0
        checkE = tkinter.Checkbutton(self, text="E", variable=EValue, onValue=1, offValue=0)
        checkN = tkinter.Checkbutton(self, text="N", variable=NValue, onValue=1, offValue=0)
        checkZ = tkinter.Checkbutton(self, text="Z", variable=ZValue, onValue=1, offValue=0)
        checkE.pack()
        checkN.pack()
        checkZ.pack()
        checkF = tkinter.Checkbutton(self, text="滤波", variable=FValue, onValue=1, offValue=0)
        checkF.pack()
        E1 = tkinter.Entry(self)
        E2 = tkinter.Entry(self)
        E1.pack()
        E2.pack()
        def quitLauncher():
            del self.worm
            self.destroy()

        self.protocol('WM_DELETE_WINDOW', quitLauncher)
        self.mainloop()


