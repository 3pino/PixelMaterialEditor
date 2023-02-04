#ver5
import PME5_base    as base
import PME5_slaves  as slaves
import PME5_Imgplus as Image
import PME5_tkplus  as tk
import os
from PIL import ImageTk
from math import ceil

from typing import List, Tuple, Optional, Union
OpVec = Optional[List[Union[int, int]]]

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
        self.select1 :OpVec = [0, 0]
        self.select2 :OpVec = [0, 0]
        self.sub_win = None
        self.transImg  = Image.transparentImg(10, 10, back = self.trans.get())
        self.currentTrans = None

        #prototype
        self.fileLabel     :tk.Label       = None
        self.Cellsizeframe :tk.Labelframe = None
        self.Imgsizeframe  :tk.Labelframe = None
        self.mag_label     :tk.Label       = None
        self.editarea      :tk.Canvas      = None
        self.TKtemp = None
        self.TKtrans = None

        try: self.history = [Image.open(self.currentFile).convert('RGBA')]
        except FileNotFoundError:
            self.ctrl_n(init = True)
        except AttributeError:
            self.ctrl_n(init = True)

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

    def currentImg(self) -> Image.Image:
        return super().currentHistory()

    def vaildSelect(self):
        cellsize = self.cellsize
        self.select1[0] = base.round2("down", base.within(self.select1[0], 0, self.currentImg().width - 1), cellsize)
        self.select1[1] = base.round2("down", base.within(self.select1[1], 0, self.currentImg().height- 1), cellsize)
        self.select2[0] = base.round2("down", base.within(self.select2[0], 0, self.currentImg().width - 1), cellsize)
        self.select2[1] = base.round2("down", base.within(self.select2[1], 0, self.currentImg().height- 1), cellsize)

    def selectedArea(self) -> tuple: #(x1, y1, x2, y2)
        cellsize = self.cellsize
        try:
            x1 , y1 = self.select1
            x2 , y2 = self.select2
        except TypeError: return 

        if x1 > x2: x1, x2 = (x2, base.within(x1 + cellsize, 0, self.currentImg().width)) #x1>x2のときはswap
        else:           x2 =      base.within(x2 + cellsize, 0, self.currentImg().width)
        if y1 > y2: y1, y2 = (y2, base.within(y1 + cellsize, 0, self.currentImg().height))
        else:           y2 =      base.within(y2 + cellsize, 0, self.currentImg().height)
        return((x1,y1,x2,y2))

    def currentCrop(self, cut = False) -> Image.Image:
        x1, y1, x2, y2 = self.selectedArea()
        im_crop = self.currentImg().crop((x1, y1, x2, y2))
        if cut:
            im_crop = im_crop.crop(im_crop.getbbox())
        return(im_crop)

    def update(self, init:bool = False,
               img     :Image.Image = None,
               overwrite:bool       = False,
               leftOnly:bool        = False,
               transOnly:bool       = False,
               cellOnly:bool        = False,
               selectedOnly:bool    = False,):
        """
        updates
        left_settings: fileLabel, Cellsizeframe, Imgsizeframe, mag_label
        calc: selectedarea, editarea(scrollregion, width, height)
        draw: transparentImg, currentImg, cellRect, borderRect, selectedRect
        """

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
            if overwrite:
                self.overwrite(img)
            else:
                self.editted(img)

        left_settings()
        if leftOnly:  return

        canvasw = int(self.currentImg().width  * self.magnification)
        canvash = int(self.currentImg().height * self.magnification)
        self.editarea["scrollregion"] = (-50, -50, canvasw+50, canvash+50)
        self.editarea["width"] = canvasw+100
        self.editarea["height"]= canvash+100

        if selectedOnly:
            drawSelected()
            return
        if transOnly:
            drawTrans(force=True)
            return
        
        if cellOnly:
            drawCell()
            drawSelected()
        else:
            drawTrans()
            drawImg()
            drawCell()
            drawSelected()

    def paste(self, clip:Image.Image, pasteSettings = "no", overwrite:bool = False):
        cellsize = self.cellsize
        old = self.currentImg()
        if not clip: return
        if not pasteSettings: pasteSettings = self.pasteSettings.get()

        if pasteSettings == "expand":
            if clip.width < cellsize and clip.height < cellsize:
                if clip.width > clip.height:
                    clip = clip.resize((cellsize, int(cellsize * clip.height/ clip.width)), resample=Image.Resampling.NEAREST)
                else:
                    clip = clip.resize((int(cellsize * clip.width/ clip.height), cellsize), resample=Image.Resampling.NEAREST)
        elif pasteSettings == "repeat":
            clip2 = Image.repeat(clip, ceil(cellsize/clip.width), ceil(cellsize/clip.height))
            clip = clip2.crop((0, 0, max(clip.width, cellsize), max(clip.height, cellsize)))
        startx  = min(self.select1[0], self.select2[0])
        starty  = min(self.select1[1], self.select2[1])
        finishx = startx + clip.width
        finishy = starty + clip.height
        new = Image.alphaPaste(old, clip, (startx, starty), self.pasteChangeSize.get())

        self.select1 = [startx, starty]
        self.select2 = [finishx-1, finishy-1]
        self.update(img = new, overwrite= overwrite)

#マウス
    def editarea_button1(self, event:tk.Event = None):
        cellsize = self.cellsize
        mag = self.magnification
        x,y = (self.editarea.canvasx(event.x)/ mag, self.editarea.canvasy(event.y)/ mag)
        if not 0 <= x <= self.currentImg().width  :  return
        if not 0 <= y <= self.currentImg().height :  return
        x = base.round2("down", x, cellsize)
        y = base.round2("down", y, cellsize)
        if event.state == 1 or event.state == 4: #1 = shift, 4 = ctrl
            self.select2 = [x, y]
        else: 
            self.select1 = [x, y]
            self.select2 = [x, y]
        self.update(selectedOnly=True)

    def editarea_motion(self, event:tk.Event = None):
        mag = self.magnification
        x,y = (int(self.editarea.canvasx(event.x)/ mag), int(self.editarea.canvasy(event.y)/ mag))
        self.select2 = [x, y]
        self.update(selectedOnly= True)

    def button2(self, event:tk.Event = None):
        x, y =(int(self.editarea.canvasx(event.x)/ self.magnification), int(self.editarea.canvasy(event.y)/ self.magnification))
        rgba = self.currentImg().getpixel((x, y))
        tk.messagebox.showinfo("マウスの座標の色", "( R, G, B, A ) = " +str(rgba) + "\n#" + base.colorHex(rgba))

#キー1つ
    def key_b(self, event = None):
        crop = self.currentCrop(cut = True)
        self.delete(save = False)
        self.paste(crop, pasteSettings="expand", overwrite=True)

    def key_d(self, event = None):
        crop = self.currentCrop(cut = False)
        self.clipboard = Image.darken(crop)

    def key_e(self, event = None):
        self.sub_win = slaves.Effect(container = self.master, nowCrop = self.currentCrop())
        effected = self.sub_win.start()
        self.delete()
        self.paste(effected, overwrite= True)

    def key_g(self, event = None):
        self.sub_win = slaves.GDWtool(container = self.master, nowImg=self.currentImg(), nowCrop=self.currentCrop())
        clip = self.sub_win.start()
        if clip:
            self.clipboard = clip

    def key_h(self, event = None):
        crop = self.currentCrop(cut=False)
        flip = None
        flip = crop.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        self.delete()
        self.paste(flip, overwrite= True)

    def key_p(self, event = None):
        self.sub_win = slaves.Preview(container = self.master, Img = self.currentCrop(cut=False), name = self.currentFile)
        self.sub_win.start()

    def key_r(self, event = None):
        crop = self.currentCrop(cut=False)
        if crop.width != crop.height: return
        flip = None
        flip = crop.rotate(90, fillcolor=(0, 0, 0, 0), expand = True)
        self.delete()
        self.paste(flip, overwrite= True)

    def key_s(self, event = None):
        filename = tk.filedialog.asksaveasfilename(initialdir = base.settings("initial_dir"), defaultextension = "png", filetypes = [('画像ファイル',"*.png")])
        if filename: 
            self.currentCrop(cut = False).save(filename)

    def key_v(self, event = None):
        crop = self.currentCrop(cut=False)
        flip = None
        flip = crop.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        self.delete()
        self.paste(flip, overwrite= True)

    def arrow(self, event:tk.Event = None, shift:bool = False, ctrl:bool = False):
        cellsize = self.cellsize
        ifshift = tk.shift(event) or shift
        ifctrl  = tk.ctrl(event)  or ctrl

        if ifshift: x, y = self.select2
        else:       x, y = self.select1

        width  = base.round2("down", self.currentImg().width,cellsize)
        height = base.round2("down", self.currentImg().height,cellsize)
        if event.keysym == "Up":
            if ifctrl:  y = 0
            else:       y = y-cellsize
        elif event.keysym == "Down":
            if ifctrl:  y = height
            else:       y = y+cellsize
        elif event.keysym == "Left":
            if ifctrl:  x = 0
            else:       x = x-cellsize
        elif event.keysym == "Right":
            if ifctrl:  x = width
            else:       x = x+cellsize
        
        if ifshift: self.select2 = [x, y]
        else:       self.select1 = self.select2 = [x, y]
        self.update(selectedOnly=True)

    def delete(self, event = None, save = True) -> Image.Image:
        x1, y1, x2, y2 = self.selectedArea()
        delPart = Image.new("RGBA", (x2-x1, y2-y1))
        new = self.currentImg().copy()
        new.paste(delPart, (x1, y1))
        if save:
            self.update(img = new)
        return new

    def key_F1(self, event = None):
        self.sub_win = slaves.Explanation(container = self.master)
        self.sub_win.start()

    def key_F2(self, event = None):
        if self.select1 == self.select2:
            self.sub_win = slaves.Painter(container = self.master, Img = self.currentCrop(cut=False), trans = self.trans.get())
            new = self.sub_win.start()
            self.paste(new)
        
        else:
            tk.messagebox.showerror(title="エラー",message="セルを一つだけ選択してください")


#キーの組み合わせ
    def ctrl_a(self, event = None):
        img = self.currentImg()
        self.select1 = [0, 0]
        self.select2 = [img.width, img.height]
        self.update(selectedOnly= True)

    def ctrl_c(self, event = None):
        self.clipboard = self.currentCrop(cut=False)

    def ctrl_n(self, event = None, init = False):
        self.currentFile = ""
        self.history = [Image.new("RGBA",(self.cellsize, self.cellsize) )]
        self.N_history = 0
        if not init:
            self.update()

    def ctrl_o(self, event = None, path:str = None):
        if not path:
            path = base.importDialog("image")
            if not path: return

        img = Image.open(path).convert('RGBA')
        self.currentFile = path
        self.history = [img]
        self.N_history = 0
        self.currentFile = path
        base.settings("initial_dir", os.path.dirname(path))
        self.update()

    def ctrl_r(self, event = None):
        self.sub_win = slaves.Resize(container = self.master, nowImg = self.currentImg())
        react = self.sub_win.start()
        if react:
            try:
                new = self.currentImg().resize(react[0], resample=react[1])
                self.update(img = new)
            except ValueError:
                return

    def ctrl_s(self, event = None):
        if self.currentFile:
            self.currentImg().save(self.currentFile)
        else:
            self.ctrl_shift_s()

    def ctrl_shift_s(self, event = None):
        filename = tk.filedialog.asksaveasfilename(initialdir = base.settings("initial_dir"), defaultextension = "png", filetypes = [('画像ファイル',"*.png")])
        if not filename: return

        base.settings("initial_dir", os.path.dirname(filename))
        self.currentImg().save(filename)
        self.currentFile = filename
        self.update(leftOnly=True)

    def ctrl_v(self, event = None):
        self.paste(self.clipboard)

    def ctrl_x(self, event = None):
        self.ctrl_c()
        self.delete()

    def ctrl_y(self, event = None):
        if self.redo():
            self.update()

    def ctrl_z(self, event = None):
        if self.undo():
            self.update()

    def ctrl_plus(self, event = None):
        self.magnification_choose.set(base.within(self.magnification_choose.get() + 1, 0, 22))
        self.magnificationChanged()

    def ctrl_minus(self, event = None):
        self.magnification_choose.set(base.within(self.magnification_choose.get() + -1, 0, 22))
        self.magnificationChanged()

    def ctrl_delete(self, event = None):
        self.ImgsizeChanged()

#左ウィジェット
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
        
        if value < 3: return

        base.settings("cellsize", value)
        self.cellsize = value
        #self.cellCustom["value"] = self.cellsize_custom.get()
        self.Cellsizeframe["text"] = "セルの大きさ：" + str(base.settings("cellsize"))
        self.cellCustom["value"] = self.cellsize_custom.get()
        self.update(cellOnly = True)
        
    def ImgsizeChanged(self, event:tk.Event = None, direction = None, expand = True):
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
                return
        
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

#その他
    def editarea_scroll(self, event: tk.Event):
        if event.delta > 0:
            self.editarea.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.editarea.yview_scroll(1, 'units')
        
    def dropped(self, event:tk.Event = None):
        path = event.widget.tk.splitlist(event.data)[0]
        try: image = Image.open(path).convert('RGBA')
        except OSError: print("error: cant import images. path: "+ path); return

        if self.currentFile:
            self.paste(image)
        else:
            self.ctrl_o(path=path)
