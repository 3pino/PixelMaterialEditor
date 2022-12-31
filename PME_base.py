import os, json, math
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageEnhance

defaultSettings = {"win_geometry": "600x400+100+100",
                   "initial_dir":os.getcwd(),
                   "backpathes": False,
                   "cellsize": 32,
                   "background": "gray",
                   "magnification" : 100,
                   "pasteSettings": "expand",
                   "pasteChangeSize": True,
                   "currentFile" : "",
                  }

def settings(item, overwrite= None):
    json_open = open('settings.json', 'r')
    data = json.load(json_open)
    if not overwrite is None:
        data[item]= overwrite
        with open('settings.json', 'w') as f:
            json.dump(data,f, indent=4, ensure_ascii=False)
        return(overwrite)
    else:
        return(data[item])
        

def checkIfSettings():
    try: #settings.jsonが存在するかどうかチェック
        json_open = open('settings.json', 'r')
        try:
            data = json.load(json_open)
        except json.decoder.JSONDecodeError:
            with open('settings.json', 'w') as f:
                json.dump(defaultSettings,f, sort_keys=True, indent=4, ensure_ascii=False)
            return (0)           
    except FileNotFoundError: #無ければdefaultSettingsを上書きして保存し終了
        with open('settings.json', 'w') as f:
            json.dump(data,f, indent=4, ensure_ascii=False)
        return (0)
    for key in defaultSettings.keys(): #あれば全部のキーがあるかどうかチェック
        try:
            value = data[key]
        except KeyError:
            data[key] = defaultSettings[key]
        with open('settings.json', 'w') as f:
            json.dump(data,f, indent=4, ensure_ascii=False)

def importDialog(type,title = "ファイルを開く",dir = None,multiple = False):
    dir = settings("initial_dir")
    if type == "image":
        imgType = [('画像ファイル',"*.png;*.jpg;*.jpeg;*.jpe;*.jfif;*.bmp;*.dip;*.bim;*.tif;*.tiff;*.gif;*.ico;*.webp")]
        if multiple:
            path = tk.filedialog.askopenfilenames(title = title, filetypes = imgType, initialdir=dir)
        else:
            path = tk.filedialog.askopenfilename( title = title, filetypes = imgType, initialdir=dir)
    return(path)

def resize(img, mwidth, mheight,fit = False):
    if type(img) == str:
        img = Image.open(img)
    if img.width < mwidth and img.height < mheight and not fit:#そのまま返せる場合
        return (img)
    if fit:
        if img.width/mwidth > img.height/mheight:
            img = img.resize((mwidth,int(mwidth*img.height/img.width)))
        else:
            img = img.resize((mwidth,int(mwidth*img.height/img.width)))
    else:
        if img.width > mwidth:
            img = img.resize((mwidth,int(mwidth*img.height/img.width)))
        if img.height> mheight:
            img = img.resize((int(mheight*img.width/img.height),mheight))
    
    return(img)

class ScrollableFrame(tk.Frame):
    def __init__(self, container, bar_x = True, bar_y = True,width = 250):
        fwidth = width
        del width
        super().__init__(container)
        self.canvas = tk.Canvas(self, width=fwidth, highlightthickness=0)
        self.scrollable_frame = tk.Frame(self.canvas, width = fwidth)
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
        if bar_x:
            self.scrollbar_x = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview, width=20)
            self.scrollbar_x.pack(side=tk.BOTTOM, fill="x")
            self.canvas.configure(xscrollcommand=self.scrollbar_x.set)
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)
        self.scrollable_frame.bind("MouseWheel",self.mouse_y_scroll)

    def mouse_y_scroll(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.canvas.yview_scroll(1, 'units')
    
def within(num, min, max):
    if num < min:
        return min
    if num > max:
        return max
    return num

def enlarge(img, min = 16):
    if type(img) == str:
        img = Image.open(img)
    if img.width < min:
        img = img.resize((min,int(min*img.height/img.width)), resample=Image.Resampling.NEAREST)
    if img.height < min:
        img = img.resize((int(min*img.width/img.height),min), resample=Image.Resampling.NEAREST)
    
    return img

def repeatx(im, column):
    dst = Image.new('RGB', (im.width * column, im.height))
    for x in range(column):
        dst.paste(im, (x * im.width, 0))
    return dst

def repeaty(im, row):
    dst = Image.new('RGB', (im.width, im.height * row))
    for y in range(row):
        dst.paste(im, (0, y * im.height))
    return dst

def repeat(im, row, column):
    dst_h = repeatx(im, column)
    return repeaty(dst_h, row)

def round(direction, num, unit):
    if direction == "up":
        return( math.ceil(num/unit)*unit)
    elif direction == "down":
        return( int(num/unit)*unit)
    else:
        raise ValueError("direction must be 'up' or 'down' ")

def darken(img):
    img = ImageEnhance.Brightness(img)
    return(img.enhance(0.5))

def transparentImg():
    img = Image.new("L", (2, 2), 255)
    img.putpixel((1, 0), 127)
    img.putpixel((0, 1), 127)
    img = img.resize((4, 4),resample= Image.Resampling.NEAREST)
    new = Image.new("L", (1000, 1000), 255)
    for y in range(250):
        for x in range(250):
            new.paste(img, [x*4, y*4])
    return(new)