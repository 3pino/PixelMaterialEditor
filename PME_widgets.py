import tkinter as tk
from tkinterdnd2 import *
import PME_base as base
import sys, os, json, re
from PIL import Image, ImageTk
from tkinter import filedialog, ttk
from tkscrolledframe import ScrolledFrame
from pyautogui import size



class PIEwidgets(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.master.title("PixelMaterialEditor")

    def window(self):
        scr_w, scr_h = size()
        winsize = base.settings("win_geometry").split("+")[0]
        winsizex, winsizey = winsize.split("x")
        if str(scr_w) == winsizex or str(scr_h) == winsizey:
            self.master.state("zoomed")
        else:
            self.master.geometry(base.settings("win_geometry"))
        self.master.bind("<F11>", lambda event: self.window.attributes("-fullscreen", not self.window.attributes("-fullscreen")))

        self.master.minsize(250,40)
        self.master.iconbitmap("PME//grass.ico")
        self.master.protocol("WM_DELETE_WINDOW", self.delete_window)


    def preview_settings(self):
        if self.sub_win == None or not self.sub_win.winfo_exists():
            pass
        else: return()
        self.sub_win = tk.Toplevel()
        self.sub_win.geometry("400x300")
        self.sub_win.title("プレビューの設定　現状何もできません")

        label_frame = ttk.Labelframe(self.sub_win, text='種類', padding=(10))
        self.preview_type = tk.StringVar()
        rb1 = ttk.Radiobutton(label_frame, text='(WRE)オートタイル', value='wre_auto', variable=self.preview_type)
        rb1.grid(row = 0, column= 0)
        rb1 = ttk.Radiobutton(label_frame, text='(WRE)キャラチップ', value='wre_chara', variable=self.preview_type)
        rb1.grid(row = 1, column= 0)
        rb1 = ttk.Radiobutton(label_frame, text='(GDW)オートブロック', value='gdw_auto', variable=self.preview_type)
        rb1.grid(row = 0, column= 1 ,sticky= tk.W)
        rb1 = ttk.Radiobutton(label_frame, text='(GDW)アニメーション(水)', value='gdw_water', variable=self.preview_type)
        rb1.grid(row = 1, column= 1 ,sticky= tk.W)
        rb1 = ttk.Radiobutton(label_frame, text='(GDW)アニメーション(滝)', value='gdw_fall', variable=self.preview_type)
        rb1.grid(row = 2, column= 1 ,sticky= tk.W)
        label_frame.grid(row = 0, column = 0, columnspan= 2)

        self.preview_cellsize = tk.IntVar()
        tk.Label(self.sub_win, text = "チップの大きさ(ピクセル)：").grid(row = 1, column = 0, sticky= tk.E)
        ttk.Entry(self.sub_win, textvariable=self.preview_cellsize, width=5).grid(row = 1, column = 1, sticky= tk.W)
        tk.Label(self.sub_win, text = "コマ数：").grid(row = 2, column = 0,  sticky= tk.E)
        ttk.Entry(self.sub_win, textvariable=self.preview_cellsize, width=5).grid(row = 2, column = 1, sticky= tk.W)

    def explanation(self):
        if self.sub_win == None or not self.sub_win.winfo_exists(): pass
        else: return()
        self.sub_win = tk.Toplevel()
        self.sub_win.geometry("400x300")
        text1 = """このソフトは主に、個々の画像を画像規格に従うように組み合わせて素材画像を作成したり、素材画像を分解して個々の画像に変換するために作られました。
素材画像の作成については、Wolf RPG Editor(以下WRE)またはGame Designer World (以下GDW)向けの利用を想定しています。
気が向いたら書き足します。
        """
        expLabel = tk.Label(self.sub_win, text = text1, wraplength=350, justify= "left")
        expLabel.pack(side= tk.TOP, fill=tk.X, anchor= tk.W)

    def menubar(self):
        menu_bar = tk.Menu(self.master)

        #ファイル
        menu_file = tk.Menu(menu_bar, tearoff=False)
        menu_file.add_command(label = "新規",  command = self.ctrl_n,  accelerator="Ctrl+N")
        menu_file.add_command(label = "ファイルを開く",  command = self.ctrl_o,  accelerator="Ctrl+O")
        menu_file.add_command(label = "保存", command = self.ctrl_s, accelerator="Ctrl+S")
        menu_file.add_command(label = "名前を付けて保存", command = self.ctrl_shift_s, accelerator="Ctrl+Shift+S")
        menu_file.add_separator() # 仕切り線
        menu_file.add_command(label = "終了",            command = self.delete_window)
        menu_file.bind_all("<Escape>", self.delete_window)
        menu_file.bind_all("<Control-n>", self.ctrl_n)
        menu_file.bind_all("<Control-o>", self.ctrl_o)
        menu_file.bind_all("<Control-s>", self.ctrl_s)
        menu_file.bind_all("<Control-Shift-S>", self.ctrl_shift_s)
        menu_bar.add_cascade(label="ファイル", menu = menu_file)

        #編集
        self.menu_edit = tk.Menu(menu_bar, tearoff=False)
        self.menu_edit.add_command(label = "元に戻す",  command = self.ctrl_z,  accelerator="Ctrl+Z")
        self.menu_edit.add_command(label = "やり直す",  command = self.ctrl_y,  accelerator="Ctrl+Y")
        self.menu_edit.add_command(label = "切り取り",  command = self.ctrl_x,  accelerator="Ctrl+X")
        self.menu_edit.add_command(label = "コピー",  command = self.ctrl_c,  accelerator="Ctrl+C")
        self.menu_edit.add_command(label = "貼り付け",  command = self.ctrl_v,  accelerator="Ctrl+V")
        self.menu_edit.add_command(label = "全選択",  command = self.ctrl_a,  accelerator="Ctrl+A")
        self.menu_edit.add_command(label = "消去",  command = self.delete,  accelerator="Delete")
        self.menu_edit.add_command(label = "余白を削除",  command = self.ctrl_delete,  accelerator="Ctrl+Delete")
        self.menu_edit.add_command(label = "選択部分を名前を付けて保存",  command = self.ctrl_alt_s,  accelerator="Ctrl+Alt+S")
        self.menu_edit.add_command(label = "90°回転",  command = self.key_r,  accelerator="R")
        self.menu_edit.add_command(label = "(GDW向け)影を生成しクリップボードにコピー",  command = self.key_d,  accelerator="D")
        self.menu_edit.add_command(label = "透過部分を埋めるように拡大",  command = self.key_b,  accelerator="B")
        self.menu_edit.add_command(label = "描く*",  command = self.key_F2,  accelerator="F2")

        self.menu_edit.bind_all("<Control-z>", self.ctrl_z)
        self.menu_edit.bind_all("<Control-y>", self.ctrl_y)
        self.menu_edit.bind_all("<Control-x>", self.ctrl_x)
        self.menu_edit.bind_all("<Control-c>", self.ctrl_c)
        self.menu_edit.bind_all("<Control-v>", self.ctrl_v)
        self.menu_edit.bind_all("<Control-a>", self.ctrl_a)
        self.menu_edit.bind_all("<Delete>", self.delete)
        self.menu_edit.bind_all("<Control-Delete>", self.ctrl_delete)
        self.menu_edit.bind_all("<Control-Alt-s>", self.ctrl_alt_s)
        self.menu_edit.bind_all("<r>", self.key_r)
        self.menu_edit.bind_all("<d>", self.key_d)
        self.menu_edit.bind_all("<b>", self.key_b)
        self.menu_edit.bind_all("<F2>", self.key_F2)
        menu_bar.add_cascade(label="編集", menu = self.menu_edit)

        #表示
        menu_disp = tk.Menu(menu_bar, tearoff=False)
        menu_disp.add_command(label = "拡大",  command = self.ctrl_plus,  accelerator="Ctrl+;")
        menu_disp.add_command(label = "縮小",  command = self.ctrl_minus,  accelerator="Ctrl+-")
        menu_disp.add_command(label = "プレビュー*",  command = self.ctrl_p,  accelerator="Ctrl+P")
        self.menu_edit.add_command(label = "説明",  command = self.key_F1,  accelerator="F1")
        menu_disp.bind_all("<Control-;>", self.ctrl_plus)
        menu_disp.bind_all("<Control-minus>", self.ctrl_minus)
        menu_disp.bind_all("<Control-p>", self.ctrl_p)
        menu_disp.bind_all("<F1>", self.key_F1)
        if True: #背景色
            menu_bg = tk.Menu(menu_disp, tearoff=False)
            menu_bg.add_radiobutton(label = "黒", command = self.bgChanged, variable = self.background, value = "black")
            menu_bg.add_radiobutton(label = "灰", command = self.bgChanged, variable = self.background, value = "gray")
            menu_bg.add_radiobutton(label = "白", command = self.bgChanged, variable = self.background, value = "white")
            self.master.config(menu = menu_bar)
            menu_disp.add_cascade(label = "背景色*",  menu= menu_bg)
        menu_bar.add_cascade(label="表示", menu = menu_disp)
    

    def left_settings(self, event=None):
        self.LSframe = base.ScrollableFrame(self.master, bar_x = False, width= 250)
        self.LSframe.grid(row=0, column=0, sticky=tk.NS)
        self.master.grid_rowconfigure(0, weight=1)

        fileLabel = tk.Label(self.LSframe.scrollable_frame, text = self.currentFile, wraplength=200)
        fileLabel.pack(side= tk.TOP, fill=tk.X)
        fileLabel.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)

        self.Cellsizeframe = ttk.Labelframe(self.LSframe.scrollable_frame, text='セルの大きさ', padding=(10))
        self.Cellsizeframe.pack(side= tk.TOP, fill=tk.X)
        self.Cellsizeframe.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        rb1 = ttk.Radiobutton(self.Cellsizeframe, text='16ピクセル　', value=16, variable=self.cellsize, command= lambda: self.cellsizeChanged(16))
        rb1.grid(row = 0, column = 0, sticky= tk.NW)
        rb1.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        rb1 = ttk.Radiobutton(self.Cellsizeframe, text='32ピクセル　', value=32, variable=self.cellsize, command= lambda: self.cellsizeChanged(32))
        rb1.grid(row = 0, column = 1, sticky= tk.NW, columnspan= 2)
        rb1.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        rb1 = ttk.Radiobutton(self.Cellsizeframe, text='48ピクセル　', value=48, variable=self.cellsize, command= lambda: self.cellsizeChanged(48))
        rb1.grid(row = 1, column = 0, )
        rb1.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        rb1 = ttk.Radiobutton(self.Cellsizeframe, text='カスタム　', value=self.cellsize_custom.get(), variable=self.cellsize, command= lambda: self.cellsizeChanged(self.cellsize_custom.get()))
        rb1.grid(row = 1, column = 1, sticky= tk.W)
        rb1.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        rb1 = ttk.Entry(self.Cellsizeframe, textvariable=self.cellsize_custom, width=5)
        rb1.grid(row = 1, column = 2, )
        rb1.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)

        sizetext = str(self.currentImg().width) + "*" + str(self.currentImg().height)
        Imgsizeframe = ttk.Labelframe(self.LSframe.scrollable_frame, text='画像の大きさ　' + sizetext, padding=(10))
        Imgsizeframe.pack(side= tk.TOP, fill=tk.X)
        Imgsizeframe.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        tk.Label(Imgsizeframe, text = "右クリックした場合 -1セル").grid(row = 0, column = 0, columnspan = 3,sticky= tk.N)
        buttonUp    = ttk.Button(Imgsizeframe, text ="上に+1セル")
        buttonUp.grid(row = 1, column = 0, columnspan = 3,sticky= tk.N)
        buttonUp.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        buttonDown  = ttk.Button(Imgsizeframe, text ="下に+1セル")
        buttonDown.grid(row = 3, column = 0, columnspan = 3, sticky= tk.S)
        buttonDown.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        buttonLeft  = ttk.Button(Imgsizeframe, text ="左に+1セル")
        buttonLeft.grid(row = 2, column = 0)
        buttonLeft.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        buttonRight = ttk.Button(Imgsizeframe, text ="右に+1セル")
        buttonRight.grid(row = 2, column = 2)
        buttonRight.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        buttonUp.bind("<Button-1>", self.ImgsizeChanged)
        buttonUp.bind("<Button-3>", self.ImgsizeChanged,'+')
        buttonDown.bind("<Button-1>", self.ImgsizeChanged)
        buttonDown.bind("<Button-3>", self.ImgsizeChanged,'+')
        buttonLeft.bind("<Button-1>", self.ImgsizeChanged)
        buttonLeft.bind("<Button-3>", self.ImgsizeChanged,'+')
        buttonRight.bind("<Button-1>", self.ImgsizeChanged)
        buttonRight.bind("<Button-3>", self.ImgsizeChanged,'+')

        self.mag_label = tk.Label(self.LSframe.scrollable_frame, text='拡大率：'+str(self.magnification)+"%")
        self.mag_label.pack(side= tk.TOP, fill=tk.X)
        self.mag_label.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        scale = ttk.Scale(self.LSframe.scrollable_frame, variable=self.magnification_choose, orient=tk.HORIZONTAL, length=200, from_=0, to=22, command=self.magnificationChanged)
        scale.pack(side= tk.TOP, fill=tk.X, padx = 10)
        scale.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)

        self.pasteSettingsframe = ttk.Labelframe(self.LSframe.scrollable_frame, text='貼り付け設定', padding=(10))
        self.pasteSettingsframe.pack(side= tk.TOP, fill=tk.X)
        self.pasteSettingsframe.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        rb1 = ttk.Radiobutton(self.pasteSettingsframe, text="拡大", value="expand", variable=self.pasteSettings, command= lambda: self.pasteSettingsChanged("expand"))
        rb1.grid(row = 0, column = 0,sticky= tk.NW)
        rb1.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        rb2 = ttk.Radiobutton(self.pasteSettingsframe, text="リピート", value="repeat", variable=self.pasteSettings, command= lambda: self.pasteSettingsChanged("repeat"))
        rb2.grid(row = 0, column = 1,sticky= tk.NE)
        rb2.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)
        cb1 = ttk.Checkbutton(self.pasteSettingsframe, text='サイズの変更を許可', variable=self.pasteChangeSize, onvalue=True, offvalue=False)
        cb1.grid(row = 1, column = 0,columnspan = 2, sticky= tk.EW)
        cb1.bind("<MouseWheel>", self.LSframe.mouse_y_scroll)


    def editarea_button3(self, event):
        self.menu_edit.post(event.x_root, event.y_root)
        
    def editarea(self):
        self.editarea = tk.Canvas(self.master, bg=self.background.get())
        self.editarea.grid(row=0, column=1, sticky=tk.NW)
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

        self.updateEditarea()

        self.editarea.bind("<ButtonPress-1>", self.editarea_button1)
        self.editarea.bind("<Button1-Motion>", self.editarea_motion)
        self.editarea.bind("<Button-3>", self.editarea_button3)
        self.editarea.drop_target_register(DND_FILES)
        self.editarea.dnd_bind("<<Drop>>", self.dropped)

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
                

        