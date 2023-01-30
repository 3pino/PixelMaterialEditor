#ver4
import PME4_base     as base
import tk_expander   as tke
import PME4_commands as commands
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import *
import sys, os, json, re
from PIL import Image, ImageTk
from pyautogui import size
 

class PMEwidgets(commands.PMEcommands):
    def __init__(self, master:tk.Tk = None):
        super().__init__(master)
        self.master: tk.Tk = master
        self.master.title("PixelMaterialEditor")

    def window(self):
        scr_w, scr_h = size()
        winsize = base.settings("win_geometry").split("+")[0]
        winsizex, winsizey = winsize.split("x")
        if str(scr_w) == winsizex or str(scr_h) == winsizey:
            self.master.state("zoomed")
        else:
            self.master.geometry(base.settings("win_geometry"))
        self.master.bind("<F11>", lambda event: self.master.attributes("-fullscreen", not self.master.attributes("-fullscreen")))

        self.master.minsize(250,40)
        try: self.master.iconphoto(True, tk.PhotoImage(file="grass.png"))
        except: 
            try: self.master.iconphoto(True, tk.PhotoImage(file="../grass.png"))
            except: 
                try: self.master.iconphoto(True, tk.PhotoImage(file="PME/grass.png"))
                except:
                    pass

        self.master.protocol("WM_DELETE_WINDOW", self.delete_window)

    def menubar(self):
        menu_bar = tke.MenuE(self.master)

        #ファイル
        menu_file = tke.MenuE(menu_bar, tearoff=False)
        menu_file.add_command(command = self.ctrl_n, accelerator = "Ctrl+N", event = "<Control-n>", label = "新規")
        menu_file.add_command(command = self.ctrl_o, accelerator = "Ctrl+O", event = "<Control-o>", label = "ファイルを開く")
        menu_file.add_command(command = self.ctrl_s, accelerator = "Ctrl+S", event = "<Control-s>", label = "上書き保存")
        menu_file.add_command(command = self.ctrl_shift_s, accelerator="Ctrl+Shift+S", event="<Control-Shift-S>", label = "名前を付けて保存")
        menu_file.add_separator() # 仕切り線
        menu_file.add_command(command = self.delete_window, accelerator = "Esc", event ="<Escape>", label = "終了")

        menu_bar.add_cascade(label="ファイル", menu = menu_file)

        #編集
        menu_edit = tke.MenuE(menu_bar, tearoff=False)
        menu_edit.add_command(command = self.ctrl_z, accelerator = "Ctrl+Z", event = "<Control-z>", label = "元に戻す")
        menu_edit.add_command(command = self.ctrl_y, accelerator = "Ctrl+Y", event = "<Control-y>", label = "やり直す")
        menu_edit.add_command(command = self.ctrl_a,  accelerator = "Ctrl+A", event = "<Control-a>", label = "全選択")
        menu_edit.add_command(command = self.ctrl_delete,  accelerator="Ctrl+Delete", event = "<Control-Delete>",label = "余白を削除")
        menu_edit.add_command(command = self.ctrl_r,  accelerator = "Ctrl+R", event = "<Control-r>", label = "リサイズ")
        menu_edit.bind_all("<Button-4>", self.ctrl_z)
        menu_edit.bind_all("<Button-5>", self.ctrl_y)

        menu_bar.add_cascade(label="編集", menu = menu_edit)


        #選択
        self.menu_select = tke.MenuE(menu_bar, tearoff=False)
        self.menu_select.add_command(command = self.ctrl_x, accelerator = "Ctrl+X", event = "<Control-x>", label = "切り取り")
        self.menu_select.add_command(command = self.ctrl_c, accelerator = "Ctrl+C", event = "<Control-c>", label = "コピー")
        self.menu_select.add_command(command = self.ctrl_v, accelerator = "Ctrl+V", event = "<Control-v>", label = "貼り付け")
        self.menu_select.add_command(command = self.delete,  accelerator = "Delete", event = "<Delete>",    label = "消去")
        self.menu_select.add_command(command = self.key_s,   accelerator = "S",  event = "<s>",  label = "選択部分を名前を付けて保存")
        self.menu_select.add_command(command = self.key_r, accelerator = "R",  event = "<r>",  label = "90°回転")
        self.menu_select.add_command(command = self.key_h, accelerator = "H",  event = "<h>",  label = "左右反転")
        self.menu_select.add_command(command = self.key_v, accelerator = "V",  event = "<v>",  label = "上下反転")
        self.menu_select.add_command(command = self.key_b,   accelerator = "B",  event = "<b>",  label = "透過部分を埋めるように拡大")
        self.menu_select.add_command(command = self.key_d,   accelerator = "D",  event = "<d>",  label = "(GDW)影を生成しクリップボードにコピー")
        self.menu_select.add_command(command = self.key_F2,  accelerator = "F2", event = "<F2>", label = "描く")

        menu_bar.add_cascade(label="選択", menu = self.menu_select)

        #表示
        menu_disp = tke.MenuE(menu_bar, tearoff=False)
        menu_disp.add_command(command = self.ctrl_plus, accelerator="Ctrl+;", event = "<Control-;>", label = "拡大")
        menu_disp.add_command(command = self.ctrl_minus,accelerator="Ctrl+-", event = "<Control-minus>", label = "縮小")
        menu_disp.add_command(command = self.key_p,     accelerator="P",      event = "<p>", label = "プレビュー")
        menu_disp.add_command(command = self.key_F1,    accelerator="F1",     event = "<F1>", label = "説明")
        if True: #背景色
            menu_bg = tk.Menu(menu_disp, tearoff=False)
            menu_bg.add_radiobutton(label = "黒", command = self.transChanged, variable = self.trans, value = 0)
            menu_bg.add_radiobutton(label = "白", command = self.transChanged, variable = self.trans, value = 255)
            self.master.config(menu = menu_bar)
            menu_disp.add_cascade(label = "透過部分の色",  menu= menu_bg)
        menu_bar.add_cascade(label="表示", menu = menu_disp)
    

    def left_settings(self, event=None):
        self.LSframe = tke.ScrollableFrame(self.master, bar_x = False, width= 250)
        self.LSframe.grid(row=0, column=0, sticky=tk.NS)
        self.master.grid_rowconfigure(0, weight=1)

        self.fileLabel = tk.Label(self.LSframe.scrollable_frame, text = self.currentFile, wraplength=200)
        self.fileLabel.pack(side= tk.TOP, fill=tk.X)

        self.Cellsizeframe = tke.Labelframe(self.LSframe.scrollable_frame, text="セルの大きさ：" + str(base.settings("cellsize")), padding=(10)).pack(side= tk.TOP, fill=tk.X)
        rb1 = ttk.Radiobutton(self.Cellsizeframe, text='16ピクセル　', value=16, variable=self.cellsize)
        rb1.bind("<Button-1>", self.cellsizeChanged)
        rb1.grid(row = 0, column = 0, sticky= tk.NW, )
        rb1 = ttk.Radiobutton(self.Cellsizeframe, text='32ピクセル　', value=32, variable=self.cellsize)
        rb1.grid(row = 0, column = 1, sticky= tk.NW, columnspan= 2)
        rb1.bind("<Button-1>", self.cellsizeChanged)
        rb1 = ttk.Radiobutton(self.Cellsizeframe, text='48ピクセル　', value=48, variable=self.cellsize)
        rb1.grid(row = 1, column = 0, )
        rb1.bind("<Button-1>", self.cellsizeChanged)
        self.cellCustom = ttk.Radiobutton(self.Cellsizeframe, text='カスタム　', value=0, variable=self.cellsize)
        self.cellCustom.bind("<Button-1>", self.cellsizeChanged)
        self.cellCustom.grid(row = 1, column = 1, sticky= tk.W)
        
        entry1 = ttk.Entry(self.Cellsizeframe, textvariable=self.cellsize_custom, width=5)
        entry1.grid(row = 1, column = 2,)
        entry1.bind('<Return>', self.cellsizeChanged)


        sizetext = str(self.currentCrop().width) + "*" + str(self.currentCrop().height)
        self.Imgsizeframe = ttk.Labelframe(self.LSframe.scrollable_frame, text='画像の大きさ　' + sizetext, padding=(10))
        self.Imgsizeframe.pack(side= tk.TOP, fill=tk.X)
        tk.Label(self.Imgsizeframe, text = "右クリックした場合 -1セル").grid(row = 0, column = 0, columnspan = 3,sticky= tk.N)

        buttonUp    = tke.ButtonE(master = self.Imgsizeframe, text ="上に+1セル")
        buttonUp.grid(row = 1, column = 0, columnspan = 3,sticky= tk.N)
        buttonDown  = tke.ButtonE(self.Imgsizeframe, text ="下に+1セル")
        buttonDown.grid(row = 3, column = 0, columnspan = 3, sticky= tk.S)
        buttonLeft  = tke.ButtonE(self.Imgsizeframe, text ="左に+1セル")
        buttonLeft.grid(row = 2, column = 0)
        buttonRight = tke.ButtonE(self.Imgsizeframe, text ="右に+1セル")
        buttonRight.grid(row = 2, column = 2)
        buttonUp.   bind(["<Button-1>", self.ImgsizeChanged],["<Button-3>", self.ImgsizeChanged])
        buttonDown. bind(["<Button-1>", self.ImgsizeChanged],["<Button-3>", self.ImgsizeChanged])
        buttonLeft. bind(["<Button-1>", self.ImgsizeChanged],["<Button-3>", self.ImgsizeChanged])
        buttonRight.bind(["<Button-1>", self.ImgsizeChanged],["<Button-3>", self.ImgsizeChanged])



        self.mag_label = tk.Label(self.LSframe.scrollable_frame, text='拡大率：'+str(int(self.magnification * 100))+"%")
        self.mag_label.pack(side= tk.TOP, fill=tk.X)
        mag100    = ttk.Button(self.LSframe.scrollable_frame, text ="100%")
        mag100.pack(side= tk.TOP)
        mag100.bind("<Button-1>", self.mag100)
        scale = ttk.Scale(self.LSframe.scrollable_frame, variable=self.magnification_choose, orient=tk.HORIZONTAL, length=200, from_=0, to=22, command=self.magnificationChanged)
        scale.pack(side= tk.TOP, fill=tk.X, padx = 10)

        self.pasteSettingsframe = ttk.Labelframe(self.LSframe.scrollable_frame, text='貼り付け設定', padding=(10))
        self.pasteSettingsframe.pack(side= tk.TOP, fill=tk.X)
        rb1 = ttk.Radiobutton(self.pasteSettingsframe, text="拡大", value="expand", variable=self.pasteSettings, command= lambda: self.pasteSettingsChanged("expand"))
        rb1.grid(row = 0, column = 0,sticky= tk.NW)
        rb2 = ttk.Radiobutton(self.pasteSettingsframe, text="リピート", value="repeat", variable=self.pasteSettings, command= lambda: self.pasteSettingsChanged("repeat"))
        rb2.grid(row = 0, column = 1,sticky= tk.NE)
        cb1 = ttk.Checkbutton(self.pasteSettingsframe, text='サイズの変更を許可', variable=self.pasteChangeSize, onvalue=True, offvalue=False)
        cb1.grid(row = 1, column = 0,columnspan = 2, sticky= tk.EW)


    def editarea_button3(self, event):
        self.menu_select.post(event.x_root, event.y_root)
        
    def drawEditarea(self):
        self.editarea = tk.Canvas(self.master, cursor = "plus")
        self.editarea.grid(row=0, column=1, sticky=tk.NSEW)
        self.editarea.bind("<MouseWheel>",self.editarea_scroll)
        self.master.grid_columnconfigure(1, weight=1)
        
        xbar = tk.Scrollbar(self.master,  orient=tk.HORIZONTAL)
        ybar = tk.Scrollbar(self.master,  orient=tk.VERTICAL)
        xbar.grid(row = 1, column = 1, sticky = tk.EW)
        ybar.grid(row = 0, column = 2, sticky = tk.NS)
        xbar.config(command= self.editarea.xview)
        ybar.config(command= self.editarea.yview)
        self.editarea.config(xscrollcommand= xbar.set)
        self.editarea.config(yscrollcommand= ybar.set)

        self.editarea.bind("<ButtonPress-1>", self.editarea_button1)
        self.editarea.bind("<Button1-Motion>", self.editarea_motion)
        self.editarea.bind("<Button-3>", self.editarea_button3)
        self.editarea.drop_target_register(DND_FILES)
        self.editarea.dnd_bind("<<Drop>>", self.dropped)
        self.editarea.bind("<Button-2>",self.button2)

        self.master.bind_all("<Up>",self.arrow)
        self.master.bind_all("<Control-Up>",self.ctrl_arrow)
        self.master.bind_all("<Down>",self.arrow)
        self.master.bind_all("<Control-Down>",self.ctrl_arrow)
        self.master.bind_all("<Left>",self.arrow)
        self.master.bind_all("<Control-Left>",self.ctrl_arrow)
        self.master.bind_all("<Right>",self.arrow)
        self.master.bind_all("<Control-Right>",self.ctrl_arrow)
        self.master.bind_all("<Shift-Up>",self.shift_arrow)
        self.master.bind_all("<Control-Shift-Up>",self.ctrl_shift_arrow)
        self.master.bind_all("<Shift-Down>",self.shift_arrow)
        self.master.bind_all("<Control-Shift-Down>",self.ctrl_shift_arrow)
        self.master.bind_all("<Shift-Left>",self.shift_arrow)
        self.master.bind_all("<Control-Shift-Left>",self.ctrl_shift_arrow)
        self.master.bind_all("<Shift-Right>",self.shift_arrow)
        self.master.bind_all("<Control-Shift-Right>",self.ctrl_shift_arrow)
    



if __name__ == '__main__':
    root = TkinterDnD.Tk()
    mass = PMEwidgets(master = root)
    mass.window()
    mass.left_settings()
    mass.menubar()
    mass.drawEditarea()
    mass.update(init = True)
    mass.master.mainloop()
