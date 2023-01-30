#ver4.1
import PME4_1_base    as base
import PME4_1_slaves  as slaves
import PME4_1_Imgplus as Image
import tk_expander as tke
import tkinter as tk
from tkinterdnd2 import *
import sys, os, json, re, math
from PIL import ImageTk
from tkinter import filedialog, ttk, messagebox
from math import ceil
import pyautogui as pg


class PMEcommands(tk.Frame, base.history):
    def __init__(self, master = None):
        super().__init__(master)
        base.checkIfSettings()
        self.currentFile = base.settings("currentFile")
        self.cellsize = base.settings("cellsize")
        self.cellsize_custom = tk.IntVar(value = base.settings("cellsize"))
        self.pasteSettings = tk.StringVar(value = base.settings("pasteSettings"))
        self.pasteChangeSize = tk.BooleanVar(value = base.settings("pasteChangeSize"))
        self.trans = tk.IntVar(value = base.settings("trans"))
        self.N_history = 0
        self.mag_list = [50, 75, 100, 125, 150, 175, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
        self.magnification = 1
        self.magnification_choose = tk. IntVar()
        self.magnification_choose.set(2)
        self.clipboard = Image.new("RGBA",(self.cellsize, self.cellsize) )
        self.select1 = [0, 0]
        self.select2 = [0, 0]
        self.sub_win = None
        try: self.history = [Image.open(self.currentFile).convert('RGBA')]
        except FileNotFoundError:
            self.history = [Image.new("RGBA",(self.cellsize, self.cellsize) )]
        except AttributeError:
            self.history = [Image.new("RGBA",(self.cellsize, self.cellsize) )]
        self.transImg  = Image.transparentImg(10, 10, back = self.trans.get())
        self.currentTrans = None

        #prototype
        self.fileLabel     :tk.Label       = None
        self.Cellsizeframe :tke.Labelframe = None
        self.Imgsizeframe  :ttk.Labelframe = None
        self.mag_label     :tk.Label       = None
        self.editarea      :tk.Canvas      = None
        self.TKtemp = None
        self.TKtrans = None

    def currentImg(self) -> Image.Image:
        return super().currentHistory()

    def currentCrop(self, cut = False):
        x1, y1, x2, y2 = self.selectedArea()
        im_crop = self.currentImg().crop((x1, y1, x2, y2))
        if cut:
            im_crop = im_crop.crop(im_crop.getbbox())
        return(im_crop)

    def update(self, init:bool = False,
               img     :Image.Image = None,
               leftOnly:bool        = False,
               transOnly:bool       = False,
               cellOnly:bool        = False,
               selectedOnly:bool    = False,):

        def left_settings():
            self.fileLabel["text"]    = self.currentFile
            self.Cellsizeframe["text"] = "セルの大きさ：" + str(base.settings("cellsize"))
            self.Imgsizeframe ["text"] = "画像の大きさ：" + str(self.currentImg().width) + "*" + str(self.currentImg().height)
            self.mag_label["text"] = '拡大率：'+str(int(self.magnification * 100))+"%"

        def drawTrans(force:bool = False):
            self.editarea.delete("TRANS")
            if canvasw + 100 > self.transImg.width or canvash + 100 > self.transImg.height or force:
                self.transImg = Image.transparentImg(canvasw+100, canvash+100, back = self.trans.get())
            self.TKtrans = self.transImg.crop((0, 0, canvasw+100, canvash+100))
            self.TKtrans = ImageTk.PhotoImage(image=self.TKtrans)
            self.editarea.create_image(-50, -50, image = self.TKtrans, anchor=tk.NW, tag = "TRANS")
            self.editarea.tag_lower("TRANS")

        def drawImg():
            self.editarea.delete("IMG")
            displayImg = self.currentImg()
            displayImg = displayImg.resize((canvasw, canvash),Image.Resampling.NEAREST)
            self.TKtemp = ImageTk.PhotoImage(image=displayImg)
            self.editarea.create_image(0, 0, image = self.TKtemp, anchor=tk.NW, tag = "IMG")

        def drawCell():
            self.editarea.delete("BORDER")
            self.editarea.create_rectangle(0, 0, canvasw, canvash, fill = None, outline = "black", width = 2, tag="BORDER")

            self.editarea.delete("CELL")
            cellsize = self.cellsize
            mag_cellsize = int(cellsize * self.magnification)
            for x in range(ceil(self.currentImg().width / cellsize)):
                self.editarea.create_line(x*mag_cellsize, 0, x * mag_cellsize, canvash, fill = "gray", tag = "CELL")
            for y in range(ceil(self.currentImg().height / cellsize)):
                self.editarea.create_line(0, y*mag_cellsize, canvasw, y * mag_cellsize, fill = "gray", tag = "CELL")

        def drawSelected():
            mag = self.magnification
            self.vaildSelect()
            x1, y1, x2, y2 = self.selectedArea()
            self.editarea.delete("SELECTED")
            self.editarea.create_rectangle(x1, y1, x2, y2, fill = None, outline = "#bb2222", width = 3, tag="SELECTED")
            self.editarea.scale("SELECTED",0,0,mag,mag)


        if img:  
            self.editted(img)

        if selectedOnly:
            drawSelected()
            return
        if transOnly:
            drawTrans(force=True)
            return
        
        left_settings()
        if leftOnly:  return

        canvasw = int(self.currentImg().width  * self.magnification)
        canvash = int(self.currentImg().height * self.magnification)
        self.editarea["scrollregion"] = (-50, -50, canvasw+50, canvash+50)
        self.editarea["width"] = canvasw+100
        self.editarea["height"]= canvash+100

        if cellOnly:
            drawCell()
            drawSelected()
        else:
            drawTrans()
            drawImg()
            drawCell()
            drawSelected()

    def delete_window(self, event = None):
        if self.sub_win == None or not self.sub_win.toplevel.winfo_exists():
            self.update_idletasks() #ウィンドウサイズなどの数値を最新状態にする
            base.settings("win_geometry",self.master.geometry())
            base.settings("currentFile", self.currentFile)
            base.settings("pasteChangeSize", self.pasteChangeSize.get())
            base.settings("trans", self.trans.get())
            self.master.destroy()

        else:
            self.sub_win.toplevel.destroy()


#メニューバー
    def ctrl_n(self, event = None):
        self.currentFile = ""
        self.history = [Image.new("RGBA",(self.cellsize, self.cellsize) )]
        self.N_history = 0
        self.update()

    def ctrl_a(self, event = None):
        img = self.currentImg()
        self.select1 = [0, 0]
        self.select2 = [img.width-1, img.height-1]
        self.update(selectedOnly= True)

    def ctrl_z(self, event = None):
        if self.undo():
            self.update()

    def ctrl_y(self, event = None):
        if self.redo():
            self.update()

    def ctrl_o(self, event = None):
        path = base.importDialog("image")
        if not path: return()

        img = Image.open(path).convert('RGBA')
        self.currentFile = path
        self.history = [img]
        self.N_history = 0
        self.currentFile = path
        base.settings("initial_dir", os.path.dirname(path))
        self.update()
    
    def ctrl_s(self, event = None):
        if self.currentFile:
            self.currentImg().save(self.currentFile)
        else:
            self.ctrl_shift_s()

    def key_p(self, event = None):
        self.sub_win = slaves.Preview(container = self, Img = self.currentCrop(cut=False), name = self.currentFile)
        self.sub_win.start()

    def ctrl_shift_s(self, event = None):
        filename = filedialog.asksaveasfilename(initialdir = base.settings("initial_dir"), defaultextension = "png", filetypes = [('画像ファイル',"*.png")])
        if filename:
            base.settings("initial_dir", os.path.dirname(filename))
            self.currentImg().save(filename)
            self.currentFile = filename
            self.update(leftOnly=True)

    def key_F1(self, event = None):
        self.sub_win = slaves.Explanation(container = self)
        self.sub_win.start()

    def ctrl_plus(self, event = None):
        self.magnification_choose.set(base.within(self.magnification_choose.get() + 1, 0, 22))
        self.magnificationChanged()

    def ctrl_minus(self, event = None):
        self.magnification_choose.set(base.within(self.magnification_choose.get() + -1, 0, 22))
        self.magnificationChanged()


#左設定
    def transChanged(self, event = None):
        self.update(transOnly= True)

    def cellsizeChanged(self, event = None):
        try:
            if event.widget["value"] :
                value = event.widget["value"]
            else:
                value = self.cellsize_custom.get()
        
        except tk.TclError:
            value = self.cellsize_custom.get()
        except AttributeError:
            value = self.cellsize_custom.get()
        
        if value < 3: return()

        base.settings("cellsize", value)
        self.cellsize = value
        #self.cellCustom["value"] = self.cellsize_custom.get()
        self.Cellsizeframe["text"] = "セルの大きさ：" + str(base.settings("cellsize"))
        self.cellCustom["value"] = self.cellsize_custom.get()
        self.update(cellOnly = True)
        

    def ImgsizeChanged(self, event = None, direction = None, expand = True):
        if event:
            dict = {"上":"up", "下": "down", "右": "right", "左": "left", "余":None}
            direction = event.widget["text"][0]
            direction = dict[direction]
            button = event.num
            if button == 1: expand = True  #左クリック
            if button == 3: expand = False #右
        imgHis = self.currentImg()
        cellsize = self.cellsize
        if direction == None:
            imgNew = imgHis.crop(imgHis.getbbox())
        
        elif expand:
            if direction in ("left", "right"):
                imgNew = Image.new("RGBA",(int((imgHis.width+cellsize)/cellsize)*cellsize, imgHis.height))
            if direction in ("up", "down"):
                imgNew = Image.new("RGBA",(imgHis.width, int((imgHis.height+cellsize)/cellsize)*cellsize))
            
            if direction == "left":
                imgNew.paste(imgHis,(imgNew.width-imgHis.width,0))
            if direction == "up":
                imgNew.paste(imgHis,(0,imgNew.height-imgHis.height))
            if direction in ("right", "down"):
                imgNew.paste(imgHis,(0,0))

        else:
            imgNew = imgHis
            if direction == "up":
                imgNew = imgNew.crop((0, cellsize, imgHis.width, imgHis.height))
            elif direction == "down":
                imgNew = imgNew.crop((0, 0, imgHis.width, ceil(imgHis.height/cellsize)*cellsize-cellsize))
            elif direction == "left":
                imgNew = imgNew.crop((cellsize, 0, imgHis.width, imgHis.height))
            elif direction == "right":
                imgNew = imgNew.crop((0, 0, ceil(imgHis.width/cellsize)*cellsize-cellsize, imgHis.height))
            else:
                return()
        
        self.update(img = imgNew)

    def magnificationChanged(self,event = None):
        self.magnification = self.mag_list[self.magnification_choose.get()] / 100
        self.update()

    def mag100(self, event = None):
        self.magnification = 1
        self.magnification_choose.set(2)
        self.update()

    def pasteSettingsChanged(self, settings):
        base.settings("pasteSettings", settings)

#エディット画面

    def paste(self, clip:Image.Image, pasteSettings = None):
        cellsize = self.cellsize
        old = self.currentImg()
        if not clip: return()
        if not pasteSettings: pasteSettings = self.pasteSettings.get()

        if pasteSettings == "expand":
            if clip.width < cellsize and clip.height < cellsize:
                if clip.width > clip.height:
                    clip = clip.resize((cellsize, int(cellsize * clip.height/ clip.width)), resample=Image.Resampling.NEAREST)
                else:
                    clip = clip.resize((int(cellsize * clip.width/ clip.height), cellsize), resample=Image.Resampling.NEAREST)
        elif pasteSettings == "repeat":
            clip2 = Image.repeat(clip, math.ceil(cellsize/clip.width), math.ceil(cellsize/clip.height))
            clip = clip2.crop((0, 0, max(clip.width, cellsize), max(clip.height, cellsize)))
        startx  = min(self.select1[0], self.select2[0])
        starty  = min(self.select1[1], self.select2[1])
        finishx = startx + clip.width
        finishy = starty + clip.height
        new = Image.alphaPaste(old, clip, (startx, starty), self.pasteChangeSize.get())

        self.select1 = [startx, starty]
        self.select2 = [finishx-1, finishy-1]
        self.update(img = new)

    def selectedArea(self):
        cellsize = self.cellsize
        try:
            x1 , y1 = self.select1
            x2 , y2 = self.select2
        except TypeError: return()

        if x1 > x2: x1, x2 = (x2, base.within(x1 + cellsize, 0, self.currentImg().width)) #x1>x2のときはswap
        else:           x2 =      base.within(x2 + cellsize, 0, self.currentImg().width)
        if y1 > y2: y1, y2 = (y2, base.within(y1 + cellsize, 0, self.currentImg().height))
        else:           y2 =      base.within(y2 + cellsize, 0, self.currentImg().height)
        return((x1,y1,x2,y2))

    def vaildSelect(self):
        cellsize = self.cellsize
        self.select1[0] = base.round2("down", base.within(self.select1[0], 0, self.currentImg().width - 1), cellsize)
        self.select1[1] = base.round2("down", base.within(self.select1[1], 0, self.currentImg().height- 1), cellsize)
        self.select2[0] = base.round2("down", base.within(self.select2[0], 0, self.currentImg().width - 1), cellsize)
        self.select2[1] = base.round2("down", base.within(self.select2[1], 0, self.currentImg().height- 1), cellsize)


    def editarea_scroll(self, event: tk.Event):
        if event.delta > 0:
            self.editarea.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.editarea.yview_scroll(1, 'units')

    def editarea_button1(self, event = None):
        cellsize = self.cellsize
        mag = self.magnification
        x,y = (self.editarea.canvasx(event.x)/ mag, self.editarea.canvasy(event.y)/ mag)
        if not 0 <= x <= self.currentImg().width  :  return()
        if not 0 <= y <= self.currentImg().height :  return()
        x = base.round2("down", x, cellsize)
        y = base.round2("down", y, cellsize)
        if keyboard.is_pressed("shift") or keyboard.is_pressed("ctrl"):
            self.select2 = [x, y]
        else: 
            self.select1 = self.select2 = [x, y]
        self.update(selectedOnly=True)

    def editarea_motion(self, event = None):
        cellsize = self.cellsize
        mag = self.magnification
        x,y = (int(self.editarea.canvasx(event.x)/ mag), int(self.editarea.canvasy(event.y)/ mag))
        self.select2 = [x, y]
        self.update(selectedOnly= True)

    def ctrl_c(self, event = None):
        self.clipboard = self.currentCrop(cut=False)
    
    def ctrl_x(self, event = None):
        self.ctrl_c()
        self.delete()
    
    def ctrl_v(self, event = None):
        self.paste(self.clipboard)

    def delete(self, event = None, save = True):
        cellsize = self.cellsize
        startx = self.select1[0]
        starty = self.select1[1]
        width  = abs(self.select2[0] - startx) +cellsize
        height = abs(self.select2[1] - starty) +cellsize
        delPart = Image.new("RGBA", (width, height))
        new = self.currentImg().copy()
        new.paste(delPart, (min(startx, self.select2[0]), min(starty, self.select2[1])))
        if save:
            self.update(img = new)

    def ctrl_delete(self, event = None):
        self.ImgsizeChanged()

    def key_s(self, event = None):
        filename = filedialog.asksaveasfilename(initialdir = base.settings("initial_dir"), defaultextension = "png", filetypes = [('画像ファイル',"*.png")])    
        self.currentCrop(cut = False).save(filename)


    def key_r(self,event = None):
        crop = self.currentCrop(cut=False)
        if crop.width == crop.height:
            flip = None
            flip = crop.rotate(90, fillcolor=(0, 0, 0, 0), expand = True)
            self.delete(save = False)
            self.paste(flip)

    def key_h(self, event = None):
        crop = self.currentCrop(cut=False)
        flip = None
        flip = crop.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        self.delete(save = False)
        self.paste(flip)

    def key_v(self, event = None):
        crop = self.currentCrop(cut=False)
        flip = None
        flip = crop.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        self.delete(save = False)
        self.paste(flip)

    def key_d(self, event = None):
        crop = self.currentCrop(cut = False)
        self.clipboard = Image.darken(crop)

    def key_b(self, event = None):
        crop = self.currentCrop(cut = True)
        self.delete(save = False)
        self.paste(crop, pasteSettings="expand")

    def key_F2(self, event = None):
        if self.select1 == self.select2:
            self.sub_win = slaves.Painter(container = self, Img = self.currentCrop(cut=False), trans = self.trans.get())
            new = self.sub_win.start()
            self.paste(new)
        
        else:
            messagebox.showerror(title="エラー",message="セルを一つだけ選択してください")

    def ctrl_r(self, event = None):
        self.sub_win = slaves.Resize(container = self, nowImg = self.currentImg())
        react = self.sub_win.start()
        if react:
            if react[0] * react[1] > 0 :
                new = self.currentImg().resize((react[0], react[1]),Image.Resampling.NEAREST)
                self.update(img = new)

    def dropped(self, event = None):
        path = event.data
        try: image = Image.open(path).convert('RGBA')
        except OSError: print("error: cant import images. path: "+ path); return
        self.paste(image)

    def arrow(self, event = None):
        cellsize = self.cellsize
        x      = base.round2("down", self.select1[0],cellsize) 
        y      = base.round2("down", self.select1[1],cellsize)
        width  = base.round2("down", self.currentImg().width,cellsize)
        height = base.round2("down", self.currentImg().height,cellsize)
        if event.keysym == "Up":
            y = base.within(y-cellsize, 0, height-cellsize)
        elif event.keysym == "Down":
            y = base.within(y+cellsize, 0, height-cellsize)
        elif event.keysym == "Left":
            x = base.within(x-cellsize, 0, width-cellsize)
        elif event.keysym == "Right":
            x = base.within(x+cellsize, 0, width-cellsize)
        self.select1  = self.select2 = [x, y]
        self.update(selectedOnly=True)
    
    def ctrl_arrow(self, event = None):
        cellsize = self.cellsize
        x      = base.round2("down", self.select1[0],cellsize) 
        y      = base.round2("down", self.select1[1],cellsize)
        width  = base.round2("down", self.currentImg().width, cellsize)
        height = base.round2("down", self.currentImg().height, cellsize)
        if event.keysym == "Up":
            if y == 0:
                self.ImgsizeChanged(direction = "up")
            y = 0
        elif event.keysym == "Down":
            if y == height- cellsize:
                self.ImgsizeChanged(direction = "down"); y = height
            else:
                y = height- cellsize
        elif event.keysym == "Left":
            if x == 0:
                self.ImgsizeChanged(direction = "left")
            x = 0
        elif event.keysym == "Right":
            if x == width - cellsize:
                self.ImgsizeChanged(direction = "right"); x = width
            else:
                x = width - cellsize
        
        self.select1  = self.select2 = [x, y]
        self.update(selectedOnly=True)

    def shift_arrow(self, event = None):
        cellsize = self.cellsize
        x      = base.round2("down", self.select2[0],cellsize) 
        y      = base.round2("down", self.select2[1],cellsize)
        width  = base.round2("down", self.currentImg().width,cellsize)
        height = base.round2("down", self.currentImg().height,cellsize)
        if event.keysym == "Up":
            y = base.within(y-cellsize, 0, height-cellsize)
        elif event.keysym == "Down":
            y = base.within(y+cellsize, 0, height-cellsize)
        elif event.keysym == "Left":
            x = base.within(x-cellsize, 0, width-cellsize)
        elif event.keysym == "Right":
            x = base.within(x+cellsize, 0, width-cellsize)
        self.select2 = [x, y]
        self.update(selectedOnly=True)

    def ctrl_shift_arrow(self, event = None):
        cellsize = self.cellsize
        x1     = base.round2("down", self.select1[0],cellsize) 
        y1     = base.round2("down", self.select1[1],cellsize)
        x      = base.round2("down", self.select2[0],cellsize) 
        y      = base.round2("down", self.select2[1],cellsize)
        width  = base.round2("down", self.currentImg().width, cellsize)
        height = base.round2("down", self.currentImg().height, cellsize)
        if event.keysym == "Up":
            if y == 0:
                self.ImgsizeChanged(direction = "up"); y1 = y1 + cellsize
            y = 0
        elif event.keysym == "Down":
            if y == height- cellsize:
                self.ImgsizeChanged(direction = "down"); y = height
            else:
                y = height- cellsize
        elif event.keysym == "Left":
            if x == 0:
                self.ImgsizeChanged(direction = "left"); x1 = x1 + cellsize
            x = 0
        elif event.keysym == "Right":
            if x == width - cellsize:
                self.ImgsizeChanged(direction = "right"); x = width
            else:
                x = width - cellsize
        
        self.select1 = [x1, y1]
        self.select2 = [x, y]
        self.update(selectedOnly=True)

    def button2(self, event = None):
        x, y =pg.position()
        r, g, b = pg.pixel(x,y)
        messagebox.showinfo("マウスの座標の色", "( R, G, B ) = ( " +str(r)+ ", "+str(g)+", "+str(b)+" )\n#" + base.colorHex(pg.pixel(x,y)))


