import tkinter as tk
from tkinterdnd2 import *
import PME_base as base
import PME_widgets as widgets
import sys, os, json, re, math
from PIL import Image, ImageTk
from tkinter import filedialog, ttk
from tkscrolledframe import ScrolledFrame
from math import ceil


class app(widgets.PIEwidgets):
    def __init__(self, master = None):
        super().__init__(master)
        base.checkIfSettings()
        self.currentFile = base.settings("currentFile")
        self.cellsize = tk.IntVar()
        self.cellsize.set(base.settings("cellsize"))
        self.cellsize_custom = tk.IntVar()
        self.cellsize_custom.set(base.settings("cellsize"))
        self.pasteSettings = tk.StringVar()
        self.pasteSettings.set(base.settings("pasteSettings"))
        self.pasteChangeSize = tk.BooleanVar()
        self.pasteChangeSize.set(base.settings("pasteChangeSize"))
        self.background = tk.StringVar(value = base.settings("background"))
        self.background.set(base.settings("background"))
        self.N_history = 0
        self.magnification = 100
        self.magnification_choose = tk. IntVar()
        self.magnification_choose.set(2)
        self.clipboard = Image.new("RGBA",(self.cellsize.get(), self.cellsize.get()) )
        self.select1 = [0, 0]
        self.select2 = [0, 0]
        self.sub_win = None
        self.transparentImg = base.transparentImg()
        self.currentTrans = None
        try: self.history = [Image.open(self.currentFile)]
        except FileNotFoundError:
            self.history = [Image.new("RGBA",(self.cellsize.get(), self.cellsize.get()) )]

    def currentCrop(self):
        if not self.select2:
            return
        cellsize = self.cellsize.get()
        startx  = self.select1[0]
        starty  = self.select1[1]
        finishx = self.select2[0]
        finishy = self.select2[1]
        if startx > finishx: startx, finishx = finishx, startx
        if starty > finishy: starty, finishy = finishy, starty
        finishx = finishx + cellsize
        finishy = finishy + cellsize
        im_crop = self.currentImg().crop((startx, starty, finishx, finishy))
        im_crop = im_crop.crop(im_crop.getbbox())
        return(im_crop)

    def currentImg(self):
        return( self.history[self.N_history] )
        
    def editted(self, img):
        if len(self.history) == self.N_history : #1回undoされていた場合
            del self.history[-1]
        elif len(self.history) > self.N_history + 1: #2回以上undoされていた場合
            del self.history[self.N_history+1 :]
        self.history.append(img)
        self.N_history = len(self.history)-1
        self.left_settings()
        self.updateEditarea()
        print(self.history)
        print(self.N_history)
    
    def delete_window(self, event = None):
        base.settings("currentFile", self.currentFile)
        base.settings("pasteChangeSize", self.pasteChangeSize.get())

        self.update_idletasks() #ウィンドウサイズなどの数値を最新状態にする
        base.settings("win_geometry",self.master.geometry())
        self.master.destroy()

#メニューバー
    def ctrl_n(self, event = None):
        self.history = [Image.new("RGBA",(self.cellsize.get(), self.cellsize.get()) )]
        self.N_history = 0
        self.updateEditarea()

    def ctrl_a(self, event = None):
        img = self.currentImg()
        cellsize = self.cellsize.get()
        self.select1 = [0, 0]
        self.select2 = [img.width-cellsize, img.height-cellsize]
        self.drawSelected()

    def ctrl_z(self, event = None):
        if self.N_history > 0:
            self.N_history = self.N_history - 1
            self.left_settings()
            self.updateEditarea()

    def ctrl_y(self, event = None):
        if self.N_history < len(self.history) - 1:
            self.N_history = self.N_history + 1
            self.left_settings()
            self.updateEditarea()

    def ctrl_o(self, event = None):
        path = base.importDialog("image")
        if not path:
            return()
        img = Image.open(path).convert('RGBA')
        self.history = [img]
        self.N_history = 0
        self.updateEditarea()
        self.currentFile = path
    
    def ctrl_s(self, event = None):
        if self.currentFile:
            self.currentImg().save(self.currentFile)
        else:
            self.ctrl_shift_s()

    def ctrl_p(self, event = None):
        self.preview_settings()

    def ctrl_shift_s(self, event = None):
        filename = filedialog.asksaveasfilename(initialdir = base.settings("initial_dir"), defaultextension = "png", filetypes = [('画像ファイル',"*.png")])
        if filename:
            self.currentImg().save(filename)
            self.currentFile = filename
            self.left_settings()

    def key_F1(self, event = None):
        self.explanation()

    def ctrl_plus(self, event = None):
        self.magnification_choose.set(base.within(self.magnification_choose.get() + 1, 0, 22))
        self.magnificationChanged()
    
    def ctrl_minus(self, event = None):
        self.magnification_choose.set(base.within(self.magnification_choose.get() + -1, 0, 22))
        self.magnificationChanged()


#左設定
    def bgChanged(self):
        self.editarea["background"] = self.background.get()
        base.settings("background", self.background.get())

    def cellsizeChanged(self, size):
        if size >= 4:
            base.settings("cellsize", size)
        self.Cellsizeframe["text"] = "セルの大きさ：" + str(base.settings("cellsize"))

    def ImgsizeChanged(self, event = None, direction = None, expand = True):
        if event:
            dict = {"上":"up", "下": "down", "右": "right", "左": "left", "余":None}
            direction = event.widget["text"][0]
            direction = dict[direction]
            button = event.num
            if button == 1: expand = True  #左クリック
            if button == 3: expand = False #右
        imgHis = self.currentImg()
        cellsize = self.cellsize.get()
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
        
        self.editted(imgNew)

    def magnificationChanged(self,event = None):
        self.mag_list = [50, 75, 100, 125, 150, 175, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
        self.magnification = self.mag_list[self.magnification_choose.get()]
        base.settings("magnification", self.magnification)
        self.mag_label["text"] = '拡大率：'+str(self.magnification)+"%"
        self.updateEditarea()

    def pasteSettingsChanged(self, settings):
        base.settings("pasteSettings", settings)

#エディット画面
    def updateEditarea(self):
        mag_double = self.magnification / 100
        self.canvasw = int(self.currentImg().width  * mag_double)
        self.canvash = int(self.currentImg().height * mag_double)
        self.editarea["scrollregion"] = (-50, -50, self.canvasw+50, self.canvash+50)
        self.editarea["width"] = self.canvasw+100
        self.editarea["height"]= self.canvash+100
        self.displayImg = self.currentImg()
        self.displayImg = self.displayImg.resize((self.canvasw, self.canvash),Image.Resampling.NEAREST)
        self.displayImg = ImageTk.PhotoImage(image=self.displayImg)
        self.currentTrans = self.transparentImg
        self.currentTrans.crop((0, 0, self.canvasw+100, self.canvash+100))
        self.currentTrans = ImageTk.PhotoImage(image=self.currentTrans)

        self.editarea.delete("all")
        self.editarea.create_image(-50, -50, image = self.currentTrans, anchor=tk.NW)
        self.editarea.create_image(0, 0, image = self.displayImg, anchor=tk.NW)

        self.editarea.create_rectangle(0, 0, self.canvasw, self.canvash, fill = None, outline = "black", width = 2, tag="OUTLINE")
        self.drawSelected()
    
    def paste(self, clip):
        cellsize = self.cellsize.get()
        old = self.currentImg()
        if not clip: return()
        if self.pasteSettings.get() == "expand":
            clip = base.enlarge(clip, cellsize)
        elif self.pasteSettings.get() == "repeat":
            clip2 = base.repeat(clip, math.ceil(cellsize/clip.width), math.ceil(cellsize/clip.height))
            clip = clip2.crop((0, 0, max(clip.width, cellsize), max(clip.height, cellsize)))
        startx  = self.select1[0]
        starty  = self.select1[1]
        finishx = startx + clip.width
        finishy = starty + clip.height
        if self.pasteChangeSize.get(): #元画像の大きさを変えるかどうか
            width = max(old.width, finishx); height = max(old.height, finishy)
        else:
            width = old.width; height = old.height
        old_resize  = Image.new("RGBA", (width, height))
        old_resize.paste(old,  (0, 0))
        clip_resize = Image.new("RGBA", (width, height))
        clip_resize.paste(clip, (startx, starty))
        new = Image.alpha_composite(old_resize, clip_resize)
        self.select2[0] = base.within(finishx - cellsize, 0 , finishx)
        self.select2[1] = base.within(finishy - cellsize, 0, finishy)
        self.editted(new)

    def drawSelected(self):
        cellsize = self.cellsize.get()
        mag = self.magnification / 100
        try:
            x1 , y1 = self.select1
            x2 , y2 = self.select2
        except TypeError:
            return()
        if x1 > x2: x1, x2 = (x2, x1 + cellsize)
        else:                 x2 = x2 + cellsize
        if y1 > y2: y1, y2 = (y2, y1 + cellsize)
        else:                 y2 = y2 + cellsize
        self.editarea.delete("SELECTED")
        self.editarea.create_rectangle(int(x1*mag), int(y1*mag), int(x2*mag), int(y2*mag), fill = None, outline = "#bb2222", width = 3, tag="SELECTED")

    def editarea_scroll(self, event):
        if event.delta > 0:
            self.editarea.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.editarea.yview_scroll(1, 'units')

    def editarea_button1(self, event = None):
        cellsize = self.cellsize.get()
        mag = self.magnification / 100
        x,y = (self.editarea.canvasx(event.x)/ mag, self.editarea.canvasy(event.y)/ mag)
        x = base.round("down", x, cellsize)
        y = base.round("down", y, cellsize)
        if not 0 <= x <= self.currentImg().width-cellsize :
            return()
        if not 0 <= y <= self.currentImg().height-cellsize :
            return()
        self.select1 = self.select2 = [x, y]
        self.drawSelected()

    def editarea_motion(self, event = None):
        cellsize = self.cellsize.get()
        mag = self.magnification / 100
        x,y = (self.editarea.canvasx(event.x)/ mag, self.editarea.canvasy(event.y)/ mag)
        x = base.within(x, 0 , self.currentImg().width-cellsize)
        y = base.within(y, 0 , self.currentImg().height-cellsize)
        x = base.round("down", x, cellsize)
        y = base.round("down", y, cellsize)
        self.select2 = [x, y]
        self.drawSelected()

    def ctrl_x(self, event = None):
        self.ctrl_c()
        self.delete()

    def ctrl_c(self, event = None):
        self.clipboard = self.currentCrop()
    
    def ctrl_v(self, event = None):
        self.paste(self.clipboard)

    def delete(self, event = None, save = True):
        cellsize = self.cellsize.get()
        startx = self.select1[0]
        starty = self.select1[1]
        width  = abs(self.select2[0] - startx) +cellsize
        height = abs(self.select2[1] - starty) +cellsize
        delPart = Image.new("RGBA", (width, height))
        new = self.currentImg().copy()
        new.paste(delPart, (min(startx, self.select2[0]), min(starty, self.select2[1])))
        if save:
            self.editted(new)

    def ctrl_delete(self, event = None):
        self.ImgsizeChanged()

    def ctrl_alt_s(self, event = None):
        filename = filedialog.asksaveasfilename(initialdir = base.settings("initial_dir"), defaultextension = "png", filetypes = [('画像ファイル',"*.png")])    
        self.currentCrop().save(filename)

    def key_r(self, event = None):
        crop = self.currentCrop()
        if crop.width == crop.height:
            rotate = crop.rotate(90, fillcolor=(127, 127, 127, 0), expand = True)
            self.delete(save = False)
            self.paste(rotate)
        
    def key_d(self, event = None):
        crop = self.currentCrop()
        self.clipboard = base.darken(crop)

    def key_b(self, event = None):
        self.paste(self.currentCrop())

    def key_F2(self, event = None):
        self.painter()

    def dropped(self, event = None):
        path = event.data[1: -1]
        try: image = Image.open(path)
        except OSError: print("error"); return(0)
        self.paste(image)
        
    def arrow(self, event = None):
        cellsize = self.cellsize.get()
        x      = base.round("down", self.select1[0],cellsize) 
        y      = base.round("down", self.select1[1],cellsize)
        width  = base.round("down", self.currentImg().width,cellsize)
        height = base.round("down", self.currentImg().height,cellsize)
        if event.keysym == "Up":
            y = base.within(y-cellsize, 0, height-cellsize)
        elif event.keysym == "Down":
            y = base.within(y+cellsize, 0, height-cellsize)
        elif event.keysym == "Left":
            x = base.within(x-cellsize, 0, width-cellsize)
        elif event.keysym == "Right":
            x = base.within(x+cellsize, 0, width-cellsize)
        self.select1  = self.select2 = [x, y]
        self.drawSelected()
    
    def ctrl_arrow(self, event = None):
        cellsize = self.cellsize.get()
        x      = base.round("down", self.select1[0],cellsize) 
        y      = base.round("down", self.select1[1],cellsize)
        width  = base.round("down", self.currentImg().width, cellsize)
        height = base.round("down", self.currentImg().height, cellsize)
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
        self.drawSelected()

    def shift_arrow(self, event = None):
        cellsize = self.cellsize.get()
        x      = base.round("down", self.select2[0],cellsize) 
        y      = base.round("down", self.select2[1],cellsize)
        width  = base.round("down", self.currentImg().width,cellsize)
        height = base.round("down", self.currentImg().height,cellsize)
        if event.keysym == "Up":
            y = base.within(y-cellsize, 0, height-cellsize)
        elif event.keysym == "Down":
            y = base.within(y+cellsize, 0, height-cellsize)
        elif event.keysym == "Left":
            x = base.within(x-cellsize, 0, width-cellsize)
        elif event.keysym == "Right":
            x = base.within(x+cellsize, 0, width-cellsize)
        self.select2 = [x, y]
        self.drawSelected()

    def ctrl_shift_arrow(self, event = None):
        cellsize = self.cellsize.get()
        x1     = base.round("down", self.select1[0],cellsize) 
        y1     = base.round("down", self.select1[1],cellsize)
        x      = base.round("down", self.select2[0],cellsize) 
        y      = base.round("down", self.select2[1],cellsize)
        width  = base.round("down", self.currentImg().width, cellsize)
        height = base.round("down", self.currentImg().height, cellsize)
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
        self.drawSelected()

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    mass = app(master = root)
    mass.window()
    mass.left_settings()
    mass.menubar()
    mass.editarea()
    mass.master.mainloop()