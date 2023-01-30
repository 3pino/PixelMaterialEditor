#ver4
import re
import tkinter as tk
from tkinter import ttk

class ScrollableFrame(tk.Frame):
    def __init__(self, container, bar_x = True, bar_y = True, **args):
        super().__init__(container)
        self.canvas = tk.Canvas(self, highlightthickness=0, **args)
        self.scrollable_frame = tk.Frame(self.canvas, **args)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        if bar_y:
            self.scrollbar_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, width=20)
            self.scrollbar_y.pack(side=tk.RIGHT, fill="y")
            self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
            self.scrollable_frame.bind("MouseWheel",self.mouse_y_scroll)
        if bar_x:
            self.scrollbar_x = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview, width=20)
            self.scrollbar_x.pack(side=tk.BOTTOM, fill="x")
            self.canvas.configure(xscrollcommand=self.scrollbar_x.set)
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)

    def mouse_y_scroll(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')


class MenuE(tk.Menu):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
    
    def add_command(self, event = None, command = None, accelerator=None, label = None):
        super().add_command(label = label,  command = command, accelerator= accelerator)
        if event:
            self.master.master.bind(event, command)

class ButtonE(ttk.Button):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
    
    def bind(self, *args):
        if type(args[0]) == list:
            for arg in args:
                super().bind(arg[0], arg[1],'+')
        
        else:
            super().bind(args[0], args[1])

    def grid(self, **kw):
        super().grid(**kw)
        return self

    def pack(self, **kw):
        super().pack(**kw)
        return self

class RadiobuttonE(ttk.Radiobutton):
    def __init__(self, master = None, row = None, column = None, **kw):
        super().__init__(master, **kw)
        if row:
            super().grid(row, column)

    def grid(self, **kw):
        super().grid(**kw)
        return self

class statusbar(tk.Label):
    def __init__(self, master = None, layout = None, **kw):
        super().__init__(master, bd=1, relief=tk.SUNKEN, anchor=tk.W, **kw)
        if layout == "pack":
            self.pack(side=tk.BOTTOM, fill=tk.X)
        
        if layout == "grid":
            self.grid(column= 0, columnspan= 100, row=100)
            self.master.grid_columnconfigure(99, weight=1)


class Labelframe(ttk.Labelframe):
    def __init__(self, master = None, layout = None, side= None, fill=None, **kw):
        super().__init__(master, **kw)
        if layout == "pack":
            self.pack(side = side, fill = tk.X)
        

    def pack(self, **kw):
        super().pack(**kw)
        return self

class Label(tk.Label):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
    
   
    def bind(self, *args):
        if type(args[0]) == list:
            for arg in args:
                super().bind(arg[0], arg[1],'+')
        
        else:
            super().bind(args[0], args[1])

    def grid(self, **kw):
        super().grid(**kw)
        return self

    def pack(self, **kw):
        super().pack(**kw)
        return self
