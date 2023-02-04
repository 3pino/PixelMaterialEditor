#ver5
import PME5_Imgplus as Image
import os, json, math
import tkinter as tk
from tkinter import filedialog, ttk

defaultSettings = {"win_geometry": "600x400+100+100",
                   "initial_dir": os.getcwd(),
                   "backpathes": False,
                   "cellsize": 32,
                   "trans" : 255, 
                   "background": 255,
                   "magnification" : 100,
                   "pasteSettings": "expand",
                   "pasteChangeSize": True,
                   "currentFile" : "",
                   "wre_chara_patterns": 3,
                   "wre_chara_dir": 8,
                   "color": [0, 0, 0, 255],
                   "resize_resampling": "nearest",
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
            return
    except FileNotFoundError: #無ければdefaultSettingsを上書きして保存し終了
        with open('settings.json', 'w') as f:
            json.dump(defaultSettings,f, indent=4, ensure_ascii=False)
        return
    for key in defaultSettings.keys(): #あれば全部のキーがあるかどうかチェック
        try:
            value = data[key]
        except KeyError:
            data[key] = defaultSettings[key]
        with open('settings.json', 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def importDialog(type: str = "", title = "ファイルを開く", dir = None, multiple = False):
    dir = settings("initial_dir")
    if type == "image":
        imgType = [('画像ファイル',"*.png;*.jpg;*.jpeg;*.jpe;*.jfif;*.bmp;*.dip;*.bim;*.tif;*.tiff;*.gif;*.ico;*.webp")]
        if multiple:
            path = filedialog.askopenfilenames(title = title, filetypes = imgType, initialdir=dir)
        else:
            path = filedialog.askopenfilename( title = title, filetypes = imgType, initialdir=dir)
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

def round2(direction, num, unit):
    if direction == "up":
        return( math.ceil(num/unit)*unit)
    elif direction == "down":
        return( int(num/unit)*unit)
    else:
        raise ValueError("direction must be 'up' or 'down' ")

def colorHex(rgba):
    if len(rgba) >= 4:
        return format(rgba[0], 'x').zfill(2) + format(rgba[1], 'x').zfill(2) + format(rgba[2], 'x').zfill(2) + format(rgba[3], 'x').zfill(2)
    else:
        return format(rgba[0], 'x').zfill(2) + format(rgba[1], 'x').zfill(2) + format(rgba[2], 'x').zfill(2)

class history():
    def __init__(self, firstCont = None):
        self.N_history = 0
        self.history = []
        if firstCont:
            self.history = [firstCont]

    def currentHistory(self):
        return( self.history[self.N_history] )
    
    def editted(self, new):
        if len(self.history) == self.N_history : #1回undoされていた場合
            del self.history[-1]
        elif len(self.history) > self.N_history + 1: #2回以上undoされていた場合
            del self.history[self.N_history+1 :]
        self.history.append(new)
        self.N_history = len(self.history)-1

    def overwrite(self, new):
        self.history[-1] = new

    def undo(self) -> bool:
        if self.N_history <= 0:
            return False
        else:
            self.N_history = self.N_history - 1
            return True

    def redo(self) -> bool:
        if self.N_history < len(self.history) - 1:
            self.N_history = self.N_history + 1
            return True
        else :
            return False

def bit8to(bit, num: int) -> int:
    d = 8 - bit
    return (num >> d << d) + (num >> bit)

def getRGBA(txtHex:str):
    if   len(txtHex) == 3:
        txtHex = txtHex + "f"
    if   len(txtHex) == 4:
        txtHex = txtHex[0]*2 + txtHex[1]*2 + txtHex[2]*2 + txtHex[3]*2
    elif len(txtHex) == 6:
        txtHex = txtHex + "ff"
    
    return [int(txtHex[0:2],16), int(txtHex[2:4],16), int(txtHex[4:6],16), int(txtHex[6:8],16)]
    
        
