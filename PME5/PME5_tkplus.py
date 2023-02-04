#ver5
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog, simpledialog
from tkinter import *
from tkinterdnd2 import *
from PIL import Image, ImageTk
import PME5_Imgplus as Image

class Widget(Widget): # type: ignore
    def usrval(self, val = None):
        if val:
            self.usrval_opt = val
            return self
        else:
            return self.usrval_opt

    def bind(self, *args):
        if type(args[0]) == list:
            for arg in args:
                super().bind(arg[0], arg[1],'+')
        
        else:
            super().bind(args[0], args[1])

    def pack(self, cnf={}, **kw):
        super().pack(cnf, **kw)
        return self

    def grid(self, **kw):
        super().grid(**kw)
        return self

class Menu(Menu, Widget): # type: ignore
    def add_command(self, event = None, command = None, accelerator=None, label = None):
        super().add_command(label = label,  command = command, accelerator= accelerator)
        if event:
            self.master.master.bind(event, command)

class Button(ttk.Button, Widget): # type: ignore
    pass

class Canvas(Canvas, Widget):
    pass

class Checkbutton(ttk.Checkbutton, Widget): # type: ignore
    pass

class Entry(ttk.Entry, Widget): # type: ignore
    pass

class Radiobutton(ttk.Radiobutton, Widget): # type: ignore
    pass

class Labelframe(ttk.Labelframe, Widget): # type: ignore
    pass
        
class Label(Label, Widget): # type: ignore
    def bind(self, *args):
        if type(args[0]) == list:
            for arg in args:
                super().bind(arg[0], arg[1],'+')
        
        else:
            super().bind(args[0], args[1])

class Scale(ttk.Scale, Widget): # type: ignore
    pass

#https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/event-handlers.html
def shift(event: Event)   -> bool:    return event.state % 2    == 1
def ctrl(event: Event)    -> bool:    return event.state % 8    >= 4
def alt(event: Event)     -> bool:    return event.state % 16   >= 8   or event.state % 256 >= 128
def button1(event: Event) -> bool:    return event.state % 512  >= 256
def button2(event: Event) -> bool:    return event.state % 1024 >= 512
def button3(event: Event) -> bool:    return event.state % 2048 >= 1024

class Statusbar(Label):
    def __init__(self, master = None, layout = "grid", **kw):
        super().__init__(master, bd=1, relief=SUNKEN, anchor=W, **kw)
        if layout == "pack":
            self.pack(side=BOTTOM, fill=X)
        
        if layout == "grid":
            self.grid(column= 0, columnspan= 100, row=100)
            self.master.grid_columnconfigure(99, weight=1)

class ScrollableFrame(Frame):
    def __init__(self, container, bar_x = True, bar_y = True, **args):
        super().__init__(container)
        self.canvas = Canvas(self, highlightthickness=0, **args)
        self.scrollable_frame = Frame(self.canvas, **args)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        if bar_y:
            self.scrollbar_y = Scrollbar(self, orient="vertical", command=self.canvas.yview, width=20)
            self.scrollbar_y.pack(side=RIGHT, fill="y")
            self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
            self.scrollable_frame.bind("MouseWheel",self.mouse_y_scroll)
        if bar_x:
            self.scrollbar_x = Scrollbar(self, orient="horizontal", command=self.canvas.xview, width=20)
            self.scrollbar_x.pack(side=BOTTOM, fill="x")
            self.canvas.configure(xscrollcommand=self.scrollbar_x.set)
        self.canvas.pack(side=LEFT, fill="both", expand=True)

    def mouse_y_scroll(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')

class ImgCanvas(Canvas):
    def __init__(self, master = None, img = None, trans = False, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.savedImg  = img
        self.updateImg(img)
        if trans:
            self.trans = Image.transparentImg(int(self["width"]), height = int(self["height"]))
            self.TKtrans = ImageTk.PhotoImage(image=self.trans)
            self.create_image(0, 0, image=self.TKtrans, anchor=NW, tag="TRANS")
            self.tag_lower("TRANS")
    
    def updateImg(self, img = None):
        self.delete("IMG")
        if img :
            self.savedImg = img
        else:
            try:  img = self.savedImg
            except AttributeError: pass

        if type(img) == str:
            try: PILimg = Image.open(img)
            except FileNotFoundError:   return
        elif type(img) == Image.Image:
            PILimg = img
        else: return
        
        PILimg = Image.resize2(PILimg, width = int(self["width"]), height = int(self["height"]))
        self.TKimg = ImageTk.PhotoImage(image=PILimg)
        self.create_image(0, 0, image=self.TKimg, anchor=NW, tag="IMG")