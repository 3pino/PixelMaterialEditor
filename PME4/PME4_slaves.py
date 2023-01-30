#ver4
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import tk_expander as tke
from PIL import ImageTk
import PME4_base    as base
import PME4_Imgplus as Image
import math

class Preview(object):
    def __init__(self, container, Img: Image.Image, name):
        self.toplevel = tk.Toplevel(container)
        self.toplevel.title("プレビュー")
        self.container = container
        self.x, self.y = Img.size
        self.img = Img
        self.mag = 1
        self.name = name
        x,y = self.x, self.y 
        self.preview_type = tk.StringVar()
        self.chara_dir = tk.IntVar(value = base.settings("wre_chara_dir"))
        self.chara_patterns = tk.IntVar(value = base.settings("wre_chara_patterns"))
        self.displayImg = []
        self.repeatN = 0


        self.toplevel.bind("<Escape>", self.destroy)
        label_frame = ttk.Labelframe(self.toplevel, text='画像規格', padding=(10))
        wre_auto  = tke.RadiobuttonE(label_frame, text='(WRE)オートタイル', value='wre_auto',  variable=self.preview_type).grid(row = 0, column= 0)
        wre_chara = tke.RadiobuttonE(label_frame, text='(WRE)キャラチップ', value='wre_chara', variable=self.preview_type).grid(row = 1, column= 0)
        gdw_auto  = tke.RadiobuttonE(label_frame, text='(GDW)オートブロック', value='gdw_auto', variable=self.preview_type).grid(row = 0, column= 1 ,sticky= tk.W)
        gdw_water = tke.RadiobuttonE(label_frame, text='(GDW)アニメーション(水)', value='gdw_water', variable=self.preview_type).grid(row = 1, column= 1 ,sticky= tk.W)
        gdw_fall  = tke.RadiobuttonE(label_frame, text='(GDW)アニメーション(滝)', value='gdw_fall', variable=self.preview_type).grid(row = 2, column= 1 ,sticky= tk.W)
        label_frame.grid(row = 1, column = 0, columnspan= 4)

        labelframe2 = ttk.Labelframe(self.toplevel, text='追加設定', padding=(10))
        wre_4  = tke.RadiobuttonE(labelframe2, text='4方向', value=4, variable=self.chara_dir).grid(row = 0, column= 0)
        wre_8  = tke.RadiobuttonE(labelframe2, text='8方向', value=8, variable=self.chara_dir).grid(row = 1, column= 0)
        wre_3  = tke.RadiobuttonE(labelframe2, text='3パターン', value=3, variable=self.chara_patterns).grid(row = 0, column= 1)
        wre_5 = tke.RadiobuttonE(labelframe2, text='5パターン', value=5, variable=self.chara_patterns).grid(row = 1, column= 1)
        labelframe2.grid(row = 2, column = 0, columnspan= 4)

        if not y in [80, 160, 200, 240]:wre_auto.  state(['disabled'])
        if x*5 % y != 0:                wre_auto.  state(['disabled'])
        if y % 4 != 0:                  wre_chara. state(['disabled'])
        if x != 160 or y != 480:        gdw_auto.  state(['disabled'])
        if x % 32 != 0 or y != 64:      gdw_water. state(['disabled'])
        if x % 32 != 0 or y != 128:     gdw_fall.  state(['disabled'])

        if self.preview_type.get() != "wre_chara":
            wre_3.state(["disabled"])
            wre_5.state(["disabled"])
            wre_4.state(["disabled"])
            wre_8.state(["disabled"])


        tke.ButtonE(self.toplevel, text = "開始", command = self.preview).grid(row = 3, column = 0)
        b1 = tke.ButtonE(self.toplevel, text = "100%").grid(row = 3, column = 1)
        b1.bind("<Button-1>", self.magChanged)
        b1 = tke.ButtonE(self.toplevel, text = "200%").grid(row = 3, column = 2)
        b1.bind("<Button-1>", self.magChanged)
        b1 = tke.ButtonE(self.toplevel, text = "300%").grid(row = 3, column = 3)
        b1.bind("<Button-1>", self.magChanged)

        self.display = tk.Canvas(self.toplevel)
        self.display.grid(row=4, column=0, columnspan = 4, sticky=tk.NW)

    def destroy(self, event = None):
        base.settings("wre_chara_dir", self.chara_dir.get())
        base.settings("wre_chara_patterns", self.chara_patterns.get())
        self.toplevel.destroy()

    def magChanged(self, event = None):
        self.mag = int(event.widget["text"][0])
        
    def repeat(self):
        if not self.displayImg:
            self.repeatN = 0
        else:
            self.repeatN = (self.repeatN + 1) % len(self.displayImg)
            mag = self.mag

            img = self.displayImg[self.repeatN]
            img = img.resize((img.width * mag, img.height * mag))
            self.TKImg = ImageTk.PhotoImage(image=img)
            self.display.create_image(0, 0, image = self.TKImg, anchor=tk.NW, tag = "IMG")

        #if self.sub_win == None or not self.sub_win.winfo_exists():
        self.toplevel.after(300, self.repeat)

    def preview(self):
        self.displayImg = []

        def make333(top, front, side):
            top  = Image.skew(top.resize((96, 48)), -45,   0)
            side = Image.skew(side.resize((48, 96)),  0, -45)
            new = Image.new("RGBA", size = (144,144))
            new = Image.alphaPaste(new, top,   (0, 0))
            new = Image.alphaPaste(new, front, (0, 48))
            new = Image.alphaPaste(new, side,  (96, 0))
            return new

        if   self.preview_type.get() == "wre_auto":
            cellsize = int(self.y / 10)
            loop = int(self.x / (2*cellsize))
            def crop(n, loop):
                col = n % 2 + 2*loop
                row = int(n/2)
                return self.img.crop((col * cellsize, row * cellsize, (col+1)*cellsize, (row+1)*cellsize))
            def cropList(img, map, loop):
                for indexY, y in enumerate(map):
                    for indexX, x in enumerate(y):
                        if map[indexY][indexX] != 20:
                            img.paste(crop(map[indexY][indexX], loop),(indexX * cellsize, indexY * cellsize))
                return img

            for l in range(loop):
                new = Image.new('RGB', (cellsize * 14, cellsize * 10))
                new.paste(Image.transparentImg(cellsize * 14, cellsize * 10), (0, 0))
                new = cropList(new, [
                    [ 0, 9, 8, 9, 8, 9, 8, 9, 8, 9, 8, 9, 8, 1],
                    [ 2,11,10,11,14,15,10,11,14,19,18,19,18, 7],
                    [20,20,20,20, 4, 5,20,20, 4,17,16,17,16, 5],
                    [20,20,20,20, 6, 7,20,20, 6,19,18,19,18, 7],
                    [ 0, 1,20,20, 4,13, 8, 9,12,17,16,17,16, 5],
                    [ 6, 7,20,20, 2,11,10,11,10,11,10,11,14, 7],
                    [ 4, 5,20,20,20,20,20,20,20,20,20,20, 4, 5],
                    [ 6, 7,20,20,20,20,20,20,20,20,20,20, 6, 7],
                    [ 4,13, 8, 9, 8, 1,20,20, 0, 1,20,20, 4, 5],
                    [ 2,11,10,11,10, 3,20,20, 2, 3,20,20, 2, 3]], l)
                self.displayImg.append(new)
        
        elif self.preview_type.get() == "wre_chara":
            patterns = self.chara_patterns
            dir = self.chara_dir
            T  = False
            TX = False

            if dir == 8:
                patterns = patterns * 2
            if   "T.png"  in self.name:
                T = True
                patterns = patterns + 1
            elif "TX.png" in self.name:
                TX = True
                patterns = patterns * 2

            cellx = int(self.x / patterns)
            celly = int(self.x / 4)

            def crop(x):
                dst = []
                for y in range(4):
                    dst.append(self.img.crop((x*cellx, y*celly, (x+1)*cellx, (y+1)*celly)))
                return(dst)
            
            stop = []
            if dir == 4:
                if T:
                    stop = [crop(0)] * patterns
                
                if TX:
                    img = []
                





            messagebox.showinfo(title = "非対応", message="キャラチップは現在非対応です")

            pass

        elif self.preview_type.get() == "gdw_auto":
            def interpolated(y) -> Image.Image:
                self.img = self.img.convert("RGBA")
                new = self.img.crop((0  , 96*y,       96, 96*(y+1)))
                #RU  = self.img.crop((96 , 96*y,      128, 96*y + 32))
                #LU  = self.img.crop((128, 96*y,      160, 96*y + 32))
                #LD  = self.img.crop((96 , 96*y + 32, 128, 96*y + 64))
                #RD  = self.img.crop((128, 96*y + 32, 160, 96*y + 64))
                #new = Image.alphaPaste(new, LU,(  0, 0))
                #new = Image.alphaPaste(new, RU,( 64, 0))
                #new = Image.alphaPaste(new, LD,(  0, 64))
                #new = Image.alphaPaste(new, RD,( 64, 64))
                return new

            top   = interpolated(1)
            front = interpolated(0)
            side  = interpolated(3)
            self.displayImg.append(make333(top, front, side))

        elif self.preview_type.get() == "gdw_water":
            for N in range(int(self.x/32)):
                light = self.img.crop((N*32,  0, (N+1)*32, 32))
                dark  = self.img.crop((N*32, 32, (N+1)*32, 64))
                top   = Image.repeat(light, 3, 3)
                front = Image.repeat(light, 3, 3)
                side  = Image.repeat(dark,  3, 3)

                self.displayImg.append(make333(top, front, side))
        
        elif self.preview_type.get() == "gdw_fall":
            for N in range(int(self.x/32)):
                top   = Image.repeat(self.img.crop((N*32,  0, (N+1)*32,  32)), 3, 3)
                front = Image.repeat(self.img.crop((N*32, 64, (N+1)*32,  96)), 3, 3)
                side  = Image.repeat(self.img.crop((N*32, 96, (N+1)*32, 128)),  3, 3)

                self.displayImg.append(make333(top, front, side))

    def start(self):
        self.repeat()
        self.toplevel.deiconify()
        self.toplevel.wait_window()
        return None


class Resize(object):
    def __init__(self, container, nowImg: Image.Image = None):
        self.toplevel = tk.Toplevel(container)
        self.toplevel.title("リサイズ")

        self.nowImg = nowImg
        self.Owidth  = nowImg.width
        self.Oheight = nowImg.height
        self.Nwidth = tk.StringVar()
        self.Nheight = tk.StringVar()
        self.react = []


        label = tk.Label(self.toplevel, text="整数を入力するとピクセル単位、\n小数を入力すると倍数として処理します。\n片方を空欄にすることで縦横比が保たれます", pady = 5)
        label.grid(row=0, column=0, columnspan = 3)
        label1 = tk.Label(self.toplevel, text='横幅 ('+str(self.Owidth)+"): ")
        label1.grid(row=1, column=0, sticky=tk.E)
        width_entry = ttk.Entry(self.toplevel, textvariable=self.Nwidth, width=15)
        width_entry.grid(row=1, column=1)
        label2 = tk.Label(self.toplevel, text='高さ ('+str(self.Oheight)+"): ")
        label2.grid(row=2, column=0, sticky=tk.E)
        height_entry = ttk.Entry(self.toplevel, textvariable=self.Nheight, width=15)
        height_entry.grid(row=2, column=1)
        button = tke.ButtonE(self.toplevel, text ="開始", width = 15, command = self.toplevel.destroy).grid(row = 3, column = 0, columnspan = 2)
        button.bind("<Escape>", self.destroy)
    
    def destroy(self, event = None):
        self.toplevel.destroy()

    def start(self, event = None):
        self.toplevel.deiconify()
        self.toplevel.wait_window()

        Nwidth  = self.Nwidth.get()
        Nheight = self.Nheight.get()
        Owidth  = self.Owidth
        Oheight = self.Oheight
        try: Nwidth = int(Nwidth)
        except ValueError: 
            try: Nwidth = float(Nwidth)
            except:  
                if Nwidth != "": return

        
        try: Nheight = int(Nheight)
        except ValueError: 
            try: Nheight = float(Nheight)
            except:
                if Nheight != "": return

        if   type(Nwidth) == str :
            if   type(Nheight) == str:
                return
            elif type(Nheight) == int:
                Nwidth = Owidth * Nheight / Oheight 
            elif type(Nheight) == float:
                Nwidth  = Owidth  * Nheight
                Nheight = Oheight * Nheight 
        
        elif type(Nwidth) == int:
            if   type(Nheight) == str:
                Nheight = Oheight * Nwidth / Owidth 
            elif type(Nheight) == int:
                pass
            elif type(Nheight) == float:
                Nheight = Oheight * Nheight
        
        elif type(Nwidth) == float:
            if   type(Nheight) == str:
                Nheight = Oheight * Nwidth
                Nwidth  = Owidth  * Nwidth
            elif type(Nheight) == int:
                Nwidth = Owidth * Nwidth
            elif type(Nheight) == float:
                Nwidth  = Owidth  * Nwidth
                Nheight = Oheight * Nheight
        
        Nwidth  = int(Nwidth)
        Nheight = int(Nheight)
        self.react = [Nwidth, Nheight]
        
        return (self.react)


class Painter(base.history):
    def __init__(self, container, Img: Image.Image = None, trans: int = 255):
        super().__init__()
        self.history = [Img]
        self.toplevel = tk.Toplevel(container)
        self.toplevel.title("描く")

        self.image = Img
        self.color = tuple(base.settings("color"))
        self.mag = base.within(int(128 / Img.height),1, 10)
        self.saved:Image.Image = None
        self.trans = trans
        self.transImg = Image.transparentImg(10,10, back = self.trans)

        self.toplevel.bind("<Escape>", self.destroy)
        self.toplevel.bind("<Control-z>", self.ctrl_z)
        self.toplevel.bind("<Control-y>", self.ctrl_y)
        self.toplevel.bind("<Button-4>", self.ctrl_z)
        self.toplevel.bind("<Button-5>", self.ctrl_y)
        self.toplevel.bind("<Control-;>", self.ctrl_plus)
        self.toplevel.bind("<Control-minus>", self.ctrl_minus)

        self.up_settings()
        self.drawEditarea()
        self.update()


    def up_settings(self):
        self.USframe = tke.ScrollableFrame(self.toplevel, bar_x = False, width= 100)
        self.USframe.grid(row=0, column=0, sticky=tk.NS)
        self.mag_label = tke.Label(self.USframe.scrollable_frame, text='拡大率：'+str(self.mag * 100)+"%").grid(row = 1, column = 0, sticky = tk.EW)
        magplus        = tke.ButtonE(self.USframe.scrollable_frame, text ="拡大").grid(row = 0, column = 0, sticky = tk.EW)
        magplus.bind("<Button-1>", self.ctrl_plus)
        magminus       = tke.ButtonE(self.USframe.scrollable_frame, text ="縮小").grid(row = 2, column = 0, sticky = tk.EW)
        magminus.bind("<Button-1>", self.ctrl_minus)
        mag100       = tke.ButtonE(self.USframe.scrollable_frame, text ="100%").grid(row = 3, column = 0, sticky = tk.EW)
        mag100.bind("<Button-1>", self.mag100)
        self.colorbtn = tke.ButtonE(self.USframe.scrollable_frame, text = self.color[1]).grid(row = 4, column = 0, sticky = tk.EW)
        self.colorbtn.bind("<Button-1>", self.colorChooser)
    
    def drawEditarea(self):
        self.editarea = tk.Canvas(self.toplevel)
        self.editarea.grid(row=0, column=1, sticky= tk.NSEW)
        self.editarea.bind("<MouseWheel>",self.editarea_scroll)
        self.toplevel.grid_rowconfigure(0, weight=1)
        self.toplevel.grid_columnconfigure(1, weight=1)
        xbar = tk.Scrollbar(self.toplevel,  orient=tk.HORIZONTAL)
        ybar = tk.Scrollbar(self.toplevel,  orient=tk.VERTICAL)
        xbar.grid(row = 1, column = 1, sticky = tk.EW)
        ybar.grid(row = 0, column = 2, sticky = tk.NS)
        xbar.config(command= self.editarea.xview)
        ybar.config(command= self.editarea.yview)
        self.editarea.config(xscrollcommand= xbar.set)
        self.editarea.config(yscrollcommand= ybar.set)
        self.editarea.bind("<ButtonPress-1>", self.button)
        self.editarea.bind("<Button1-Motion>", self.button)
        self.editarea.bind("<ButtonPress-3>", self.button)
        self.editarea.bind("<Button3-Motion>", self.button)
        self.editarea.bind("<ButtonPress-2>", self.button)

    #処理
    def currentImg(self) -> Image.Image:
        return super().currentHistory()


    def update(self, editted:Image.Image = None, overwrite:Image.Image = None):

        def upsettings():
            self.mag_label["text"] = '拡大率：'+str(self.mag * 100)+"%"
            self.colorbtn["text"]  = self.color[1]
        
        def drawTrans(force:bool = False):
            self.editarea.delete("TRANS")
            if canvasw > self.transImg.width or canvash > self.transImg.height or force:
                self.transImg = Image.transparentImg(canvasw, canvash, back = self.trans)
            self.TKtrans = self.transImg.crop((0, 0, canvasw, canvash))
            self.TKtrans = ImageTk.PhotoImage(image=self.TKtrans)
            self.editarea.create_image(0, 0, image = self.TKtrans, anchor=tk.NW, tag = "TRANS")
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
            if self.mag == 1: return
            for x in range(self.currentImg().width):
                self.editarea.create_line(x*self.mag, 0, x * self.mag, canvash, fill = "gray", tag = "CELL")
            for y in range(self.currentImg().height):
                self.editarea.create_line(0, y*self.mag, canvasw, y * self.mag, fill = "gray", tag = "CELL")

        if editted:
            self.editted(editted)
        if overwrite:
            self.overwrite(overwrite)
        upsettings()
        canvasw = self.currentImg().width  * self.mag
        canvash = self.currentImg().height * self.mag
        self.editarea["scrollregion"] = (-50, -50, canvasw+50, canvash+50)
        self.editarea["width"] = canvasw+100
        self.editarea["height"]= canvash+100
        drawTrans()
        drawImg()
        drawCell()

    #ショートカット
    def ctrl_z(self, event = None):
        if self.undo():
            self.update()
    def ctrl_y(self, event = None):
        if self.redo():
            self.update()
    def ctrl_s(self, event = None):
        self.saved = self.currentImg()
    def destroy(self, event = None):
        base.settings("color", self.color)
        self.toplevel.destroy()

    def ctrl_plus(self, event = None):
        self.mag = base.within(self.mag + 1, 1, 10)
        self.update()
    def ctrl_minus(self, event = None):
        self.mag = base.within(self.mag - 1, 1, 10)
        self.update()
    def mag100(self, event = None):
        self.mag = 1
        self.update()  
    def colorChooser(self, event = None):
        self.color = colorchooser.askcolor()   #colorchooser呼び出し
        self.update()

    def editarea_scroll(self, event: tk.Event):
        if event.delta > 0:
            self.editarea.yview_scroll(-1, 'units')
        elif event.delta < 0:
            self.editarea.yview_scroll(1, 'units')

    def button(self, event:tk.Event = None):
        x,y = (int(self.editarea.canvasx(event.x)/ self.mag), int(self.editarea.canvasy(event.y)/ self.mag))
        if not 0 <= x < self.currentImg().width  :  return()
        if not 0 <= y < self.currentImg().height :  return()
        new = self.currentImg().copy()
        if   event.num == 1:
            new.putpixel((x, y), tuple(self.color[0]))
            self.update(editted = new)
        elif event.state == 256:
            new.putpixel((x, y), tuple(self.color[0]))
            self.update(overwrite = new)

        elif event.num ==2:
            color = self.currentImg().getpixel((x, y))
            if color:
                self.color = (color, "#" + base.colorHex(color))
        elif event.num == 3:
            new.putpixel((x, y), (0, 0, 0, 0))
            self.update(editted = new)
        elif event.state == 1024:
            new.putpixel((x, y), (0, 0, 0, 0))
            self.update(overwrite = new)


    def start(self):
        self.toplevel.deiconify()
        self.toplevel.wait_window()
        return self.currentImg()


class Explanation(object):
    def __init__(self, container, nowImg: Image.Image = None):
        self.toplevel = tk.Toplevel(container)
        self.toplevel.title("説明")
        self.toplevel.bind("<Escape>", self.destroy)
        self.label = tk.Label(self.toplevel, justify="left")
        self.label.pack(fill="both")

        self.exp = """
このソフトは主に、個々の画像を画像規格に従うように組み合わせて素材画像を作成したり、素材画像を分解して個々の画像に変換するために作られました。
素材画像の作成については、Wolf RPG Editor(以下WRE)またはGame Designer World (以下GDW)向けの利用を想定しています。

●主な使い方1：差分画像を組み合わせて一つの素材画像を作りたい
1.差分画像の大きさを正方形にすることを推奨します。画面左側のメニューで、セルの大きさを差分画像の大きさに設定します。
2.素材画像の大きさを、画面左側のボタンなどで十分大きく設定しましょう(後から変えられます)。
3.差分画像を貼り付けたいセルをマウスで選択してから、差分画像をドラッグ&ドロップします。
4.3を繰り返すと、一つの素材画像が完成します。空白部分はCtrl+Deleteを押すことでカットできます。
5.自動保存機能は無いので、Ctrl+Sなどで保存しましょう。
間違えた場合は慌てずにCtrl+Zを押して戻り、
Ctrl+Aなどで素材画像を選択し、Pキーを押すことでプレビューを確認できます。
GDWの為の機能として、明部の画像を選択してDキーを押すと、暗部を自動的にクリップボードに生成できます。

●主な使い方2：素材画像を分解して差分画像を抽出したい
※差分画像が正方形でないとうまくできません。
1.画面左側のメニューで、セルの大きさを差分画像の大きさに設定します。
2.保存したい差分画像をマウスで選択し、Sキーを押して保存します。
        """
    
    def start(self):
        self.label["text"] = self.exp
        self.toplevel.deiconify()
        self.toplevel.wait_window()
        return None

    def destroy(self):
        self.toplevel.destroy()