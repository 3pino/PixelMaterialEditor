#ver5
import PME5_tkplus  as tk
from PIL import ImageTk, ImageEnhance
from PIL.ImageTk import PhotoImage
import PME5_base    as base
import PME5_Imgplus as Image
import math, platform


class SubWindows():
    def __init__(self, container:tk.Widget, title:str = None):
        self.toplevel = tk.Toplevel(container)
        self.title = title
        if title:  self.toplevel.title(title)
        self.toplevel.bind("<Escape>", self._destroy)

    def _destroy(self, event = None):
        self.toplevel.destroy()

    def start(self):
        self.start_before()
        self.toplevel.grab_set()
        self.toplevel.wait_window()
        return self.start_after()
    
    def start_before(self):
        pass

    def start_after(self):
        pass

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
        label_frame = tk.Labelframe(self.toplevel, text='画像規格', padding=(10))
        wre_auto  = tk.Radiobutton(label_frame, text='(WRE)オートタイル', value='wre_auto',  variable=self.preview_type).grid(row = 0, column= 0)
        wre_chara = tk.Radiobutton(label_frame, text='(WRE)キャラチップ', value='wre_chara', variable=self.preview_type).grid(row = 1, column= 0)
        gdw_auto  = tk.Radiobutton(label_frame, text='(GDW)オートブロック', value='gdw_auto', variable=self.preview_type).grid(row = 0, column= 1 ,sticky= tk.W)
        gdw_water = tk.Radiobutton(label_frame, text='(GDW)アニメーション(水)', value='gdw_water', variable=self.preview_type).grid(row = 1, column= 1 ,sticky= tk.W)
        gdw_fall  = tk.Radiobutton(label_frame, text='(GDW)アニメーション(滝)', value='gdw_fall', variable=self.preview_type).grid(row = 2, column= 1 ,sticky= tk.W)
        label_frame.grid(row = 1, column = 0, columnspan= 4)

        labelframe2 = tk.Labelframe(self.toplevel, text='追加設定', padding=(10))
        wre_4  = tk.Radiobutton(labelframe2, text='4方向', value=4, variable=self.chara_dir).grid(row = 0, column= 0)
        wre_8  = tk.Radiobutton(labelframe2, text='8方向', value=8, variable=self.chara_dir).grid(row = 1, column= 0)
        wre_3  = tk.Radiobutton(labelframe2, text='3パターン', value=3, variable=self.chara_patterns).grid(row = 0, column= 1)
        wre_5 = tk.Radiobutton(labelframe2, text='5パターン', value=5, variable=self.chara_patterns).grid(row = 1, column= 1)
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


        tk.Button(self.toplevel, text = "開始", command = self.preview).grid(row = 3, column = 0)
        b1 = tk.Button(self.toplevel, text = "100%").grid(row = 3, column = 1)
        b1.bind("<Button-1>", self.magChanged)
        b1 = tk.Button(self.toplevel, text = "200%").grid(row = 3, column = 2)
        b1.bind("<Button-1>", self.magChanged)
        b1 = tk.Button(self.toplevel, text = "300%").grid(row = 3, column = 3)
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
            patterns = self.chara_patterns.get()
            dir = self.chara_dir.get()
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
                





            tk.messagebox.showinfo(title = "非対応", message="キャラチップは現在非対応です")

            pass

        elif self.preview_type.get() == "gdw_auto":
            def interpolated(y) -> Image.Image:
                self.img = self.img.convert("RGBA")
                new = self.img.crop((0  , 96*y,       96, 96*(y+1)))
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
        self.toplevel.grab_set()
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
        self.resampling = tk.StringVar(value=base.settings("resize_resampling"))


        label = tk.Label(self.toplevel, text="整数を入力するとピクセル単位、\n小数を入力すると倍数として処理します。\n片方を空欄にすることで縦横比が保たれます", justify="left", pady = 5)
        label.grid(row=0, column=0, columnspan = 3)
        label1 = tk.Label(self.toplevel, text='横幅 ('+str(self.Owidth)+"): ")
        label1.grid(row=1, column=0, sticky=tk.E)
        width_entry = tk.Entry(self.toplevel, textvariable=self.Nwidth, width=15)
        width_entry.grid(row=1, column=1)
        label2 = tk.Label(self.toplevel, text='高さ ('+str(self.Oheight)+"): ")
        label2.grid(row=2, column=0, sticky=tk.E)
        height_entry = tk.Entry(self.toplevel, textvariable=self.Nheight, width=15)
        height_entry.grid(row=2, column=1)
        button = tk.Button(self.toplevel, text ="開始", width = 15, command = self.toplevel.destroy).grid(row = 4, column = 0, columnspan = 2)
        labelframe = tk.Labelframe(self.toplevel, text = "補間").grid(row = 3, column = 0, columnspan = 2)
        nearest = tk.Radiobutton(labelframe, text = "最近傍(ドット絵向け)", value = "nearest", variable = self.resampling).pack(anchor = tk.W)
        bilinear = tk.Radiobutton(labelframe, text = "バイリニア", value = "bilinear", variable = self.resampling).pack(anchor = tk.W)

        self.toplevel.bind("<Escape>", self.destroy)
    
    def destroy(self, event = None):
        self.toplevel.destroy()

    def start(self, event = None) -> tuple: #[[width, height], resampling]
        self.toplevel.grab_set()
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

        base.settings("resize_resampling", self.resampling.get())
        resampling = Image.Resampling.NEAREST if self.resampling.get() == "nearest" else Image.Resampling.BILINEAR
        self.react = [[Nwidth, Nheight], resampling]
        
        return (self.react)


class Painter(base.history):
    def __init__(self, container, Img: Image.Image = None, trans: int = 255):
        super().__init__()
        self.history = [Img]
        self.toplevel = tk.Toplevel(container)
        self.toplevel.title("描く")

        self.image = Img
        self.color = base.settings("color")
        self.mag = base.within(int(128 / Img.height),1, 10)
        self.saved:Image.Image = None
        self.trans = trans
        self.transImg = Image.transparentImg(10,10, back = self.trans)

        self.toplevel.bind("<Escape>", self.destroy)
        self.toplevel.bind("<Control-z>", self.ctrl_z)
        self.toplevel.bind("<Control-y>", self.ctrl_y)
        self.toplevel.bind("<Button-4>", self.ctrl_z)
        self.toplevel.bind("<Button-5>", self.ctrl_y)
        if   platform.system() == "Linux":
            self.toplevel.bind("<Control-semicolon>", self.ctrl_plus)
        elif platform.system() == "Windows":
            self.toplevel.bind("<Control-;>", self.ctrl_plus)
        self.toplevel.bind("<Control-minus>", self.ctrl_minus)

        self.up_settings()
        self.drawEditarea()
        self.update()


    def up_settings(self):
        self.USframe = tk.ScrollableFrame(self.toplevel, bar_x = False, width= 100)
        self.USframe.grid(row=0, column=0, sticky=tk.NS)
        self.mag_label = tk.Label(self.USframe.scrollable_frame, text='拡大率：'+str(self.mag * 100)+"%").grid(row = 1, column = 0, sticky = tk.EW)
        magplus        = tk.Button(self.USframe.scrollable_frame, text ="拡大").grid(row = 0, column = 0, sticky = tk.EW)
        magplus.bind("<Button-1>", self.ctrl_plus)
        magminus       = tk.Button(self.USframe.scrollable_frame, text ="縮小").grid(row = 2, column = 0, sticky = tk.EW)
        magminus.bind("<Button-1>", self.ctrl_minus)
        mag100       = tk.Button(self.USframe.scrollable_frame, text ="100%").grid(row = 3, column = 0, sticky = tk.EW)
        mag100.bind("<Button-1>", self.mag100)
        self.colorbtn = tk.Button(self.USframe.scrollable_frame, text = self.color[1]).grid(row = 4, column = 0, sticky = tk.EW)
        self.colorbtn.bind("<Button-1>", self.colorChooser)
        self.alpha = tk.IntVar(value = 255)
    
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


    def update(self, editted:Image.Image = None, overwrite:Image.Image = None, upsettingsOnly = False):

        def upsettings():
            self.mag_label["text"] = '拡大率：'+str(self.mag * 100)+"%"
            self.colorbtn["text"]  = "#" + base.colorHex(self.color)
        
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
        if upsettingsOnly: return
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
        color = tk.simpledialog.askstring("色を入力", "16進数の、3,4,6,8桁のいずれかで入力してください。")
        if not color: return
        try:
            color = base.getRGBA(color)
        except ValueError:  return
        self.color = color
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
            new.putpixel((x, y), tuple(self.color))
            self.update(editted = new)
        elif tk.button1(event):
            new.putpixel((x, y), tuple(self.color))
            self.update(overwrite = new)

        elif event.num ==2:
            color = self.currentImg().getpixel((x, y))
            if color:
                self.color = color
                self.update(upsettingsOnly=True)

        elif event.num == 3:
            new.putpixel((x, y), (0, 0, 0, 0))
            self.update(editted = new)
        elif tk.button3(event):
            new.putpixel((x, y), (0, 0, 0, 0))
            self.update(overwrite = new)

    def start(self):
        self.toplevel.grab_set()
        self.toplevel.wait_window()
        return self.currentImg()


class Explanation(SubWindows):
    def __init__(self, container):
        super().__init__(container = container, title = "説明")
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
    
    def start_before(self):
        self.label["text"] = self.exp
    

class GDWtool(SubWindows):
    def __init__(self, container, nowImg: Image.Image = None, nowCrop: Image.Image = None):
        super().__init__(container, "GDW用素材合成ツール")
        self.nowImg  :Image.Image = nowImg
        self.nowCrop :Image.Image = nowCrop
        self.mode : str = "no"
        self.dst:Image.Image = None
        self.preview:Image.Image = None
        self.ifclip = False

        self.hint        = tk.Label(self.toplevel, text = "作りたいブロックを選択してください").pack()
        self.buttonAuto  = tk.Button(self.toplevel, text = "オートブロックを作る").pack()
        self.buttonAuto.usrval("auto").bind("<Button-1>", self.modeButton)
        self.buttonFall  = tk.Button(self.toplevel, text = "アニメーションブロック(滝)を作る").pack()
        self.buttonFall.usrval("fall").bind("<Button-1>", self.modeButton)
        
        self.top    = self.ImgEntry(self.toplevel, text = "上面").reset(self, "top")
        self.side   = self.ImgEntry(self.toplevel, text = "側面").reset(self, "side")
        self.bottom = self.ImgEntry(self.toplevel, text = "底面(任意)").reset(self, "bottom")
        self.startBtn = tk.Button(self.toplevel, text = "作成(プレビュー)")

    class ImgEntry(tk.Labelframe):
        def reset(self, commander, direction):
            self.Img :Image.Image = None
            self.ImgBtn   = tk.Button(self, text = "現在の画像を使用").pack()
            self.ImgBtn.usrval(direction).bind("<Button-1>", commander._ImgButton)
            self.CropBtn  = tk.Button(self, text = "現在の選択範囲を使用").pack()
            self.CropBtn.usrval(direction).bind("<Button-1>", commander._CropButton)
            self.CropBtn  = tk.Button(self, text = "ファイルを選択").pack()
            self.CropBtn.usrval(direction).bind("<Button-1>", commander._FileButton)
            self.ImgCanvas= tk.ImgCanvas(self, img=self.Img, width = 96, height = 96).pack()

            self.usrval(direction).drop_target_register(tk.DND_FILES)
            self.dnd_bind("<<Drop>>", commander._dropped)
            return self

    def _classof(self, direction):
        if   direction == "top":
            return self.top
        elif direction == "side":
            return self.side
        elif direction == "bottom":
            return self.bottom

    def modeButton(self, event:tk.Event = None):
        if event:
            self.mode = event.widget.usrval()
        self.buttonAuto.destroy()
        self.buttonFall.destroy()
        self.hint["text"] = "ドラッグアンドドロップまたはボタンで選択"
        self.top.pack(side = tk.LEFT)
        self.side.pack(side = tk.LEFT)
        if self.mode == "auto":
            self.bottom.pack(side = tk.LEFT)
        self.startBtn.pack(side = tk.BOTTOM)
        self.startBtn.bind("<Button-1>", self.create)
    
    def _ImgButton(self, event:tk.Event):
        evClass = self._classof(event.widget.usrval())
        evClass.Img = self.nowImg
        evClass.ImgCanvas.updateImg(img = evClass.Img)

    def _CropButton(self, event:tk.Event):
        evClass = self._classof(event.widget.usrval())
        evClass.Img = self.nowCrop
        evClass.ImgCanvas.updateImg(img = evClass.Img)

    def _FileButton(self, event:tk.Event):
        path = base.importDialog("image")
        if not path: return
        try:    img = Image.open(path).convert('RGBA')
        except FileNotFoundError:   return

        evClass = self._classof(event.widget.usrval())
        evClass.Img = img
        evClass.ImgCanvas.updateImg(img = evClass.Img)
        
    def _dropped(self, event):
        evClass = self._classof(event.widget.usrval())
        path = event.widget.tk.splitlist(event.data)[0]
        try: image = Image.open(path).convert('RGBA')
        except OSError: print("error: cant import images. path: "+ path); return

        evClass.Img = image
        evClass.ImgCanvas.updateImg(img = evClass.Img)

    def create(self, event = None):
        top    = self.top.Img
        side   = self.side.Img
        bottom = self.bottom.Img
        if top and side: pass
        else: return
        if self.mode == "auto":
            topDark = Image.darken(top)
            sideDark = Image.darken(side)
            if  not bottom: bottom = topDark
            top     = Image.repeat(top,     size = [96, 96])
            side    = Image.repeat(side,    size = [96, 96])
            bottom  = Image.repeat(bottom,  size = [96, 96])
            topDark = Image.repeat(topDark, size = [96, 96])
            sideDark= Image.repeat(sideDark,size = [96, 96])
            self.dst = Image.new("RGBA", [160, 480])
            self.dst.paste(side,    (0, 0))
            self.dst.paste(top,     (0, 96))
            self.dst.paste(bottom,  (0, 192))
            self.dst.paste(sideDark,(0, 288))
            self.dst.paste(topDark, (0, 384))
            self.preview = Image.makeCube(top, side, sideDark)
        elif self.mode == "fall":
            topDark  = Image.darken(top)
            sideDark = Image.darken(side)
            self.dst = Image.new("RGBA", (max(top.width, side.width), 128))
            self.dst.paste(top,      (0, 0))
            self.dst.paste(topDark,  (0, 32))
            self.dst.paste(side,     (0, 64))
            self.dst.paste(sideDark, (0, 96))
            self.preview = Image.makeCube(top.crop((0, 0, 32, 32)), 
                                          side.crop((0, 0, 32, 32)), 
                                          sideDark.crop((0, 0, 32, 32)))
        
        self.saveWidget()

    def saveWidget(self): #createから直接呼び出し
        self.top.pack_forget()
        self.side.pack_forget()
        self.bottom.pack_forget()
        self.startBtn.pack_forget()

        self.hint["text"] = ""
        self.previewCanvas = tk.ImgCanvas(self.toplevel, img=self.preview, width = 144, height = 144).pack(side = tk.LEFT)
        self.saveBtn  = tk.Button(self.toplevel, text = "作成して保存").pack()
        self.saveBtn.usrval("save").bind("<Button-1>", self._saveButton)
        self.copyBtn  = tk.Button(self.toplevel, text = "作成してクリップボードにコピー").pack()
        self.copyBtn.usrval("clip").bind("<Button-1>", self._saveButton)
        self.cancelBtn  = tk.Button(self.toplevel, text = "キャンセル").pack()
        self.cancelBtn.usrval("cancel").bind("<Button-1>", self._saveButton)
    
    def _saveButton(self, event: tk.Event):
        val = event.widget.usrval()
        if val == "save":
            filename = tk.filedialog.asksaveasfilename(initialdir = base.settings("initial_dir"), defaultextension = "png", filetypes = [('画像ファイル',"*.png")])
            if filename:
                self.dst.save(filename)
                self._destroy()
            else: 
                self.previewCanvas.pack_forget()
                self.saveBtn.pack_forget()
                self.saveBtn.pack_forget()
                self.cancelBtn.pack_forget()
                self.modeButton()
        
        elif val == "cancel":
            self.previewCanvas.pack_forget()
            self.saveBtn.pack_forget()
            self.saveBtn.pack_forget()
            self.cancelBtn.pack_forget()
            self.modeButton()
        
        elif val == "clip":
            self.ifclip = True
            self._destroy()
    
    def start_after(self):
        if self.ifclip:
            return self.dst


class Effect(SubWindows):
    def __init__(self, container, nowCrop):
        super().__init__(container, "エフェクト")
        self.nowCrop = nowCrop
        self.effected = nowCrop
        self.imgShow = tk.ImgCanvas(self.toplevel, img = self.effected, trans=True).pack(side=tk.RIGHT, fill = tk.Y)
        self.Effects = [self.EffectEntry(self.toplevel).reset(self, "コントラスト", ImageEnhance.Color),
                        self.EffectEntry(self.toplevel).reset(self, "彩度", ImageEnhance.Contrast),
                        self.EffectEntry(self.toplevel).reset(self, "明るさ", ImageEnhance.Brightness),
                        self.EffectEntry(self.toplevel).reset(self, "シャープネス", ImageEnhance.Sharpness),
                        ]
        
        self.colorEffect = self.colorEntry(self.toplevel, text="色数").init_color(commander=self)
        self.alphaEffect = self.alphaEntry(self.toplevel, text="アルファチャンネル").init_alpha(commander=self)
        self.finBtn = tk.Button(self.toplevel, text = "終了", command=self._destroy).pack()

    class EffectEntry(tk.Frame):
        def reset(self, commander, name, enhance):
            self.commander = commander
            self.name = name
            self.enhance = enhance
            self.degreeTK = tk.IntVar(value = 0)

            self.pack(side = tk.TOP, fill = tk.X)
            self.title    = tk.Label( self).pack(anchor = tk.W)
            self.titleSet()
            self.resetBtn = tk.Button(self, text = "リセット", command= self.resetButton).pack(side = tk.RIGHT)
            self.scale    = tk.Scale( self, from_ = -100, to = 100, variable=self.degreeTK, command=self.changeDegree).pack(side=tk.RIGHT)


            return self
        
        def titleSet(self):
            self.title["text"] = self.name + " " + str(self.degreeTK.get() / 100)
            
        def changeDegree(self, event = None):
            self.titleSet()
            self.commander.re_effect()
            
        def resetButton(self, event = None):
            self.degreeTK.set(0)
            self.changeDegree()
    
    class colorEntry(tk.LabelFrame):# 0->no, 1->black, 2->gray, 3->quantize(colors) 4->332, 5->444, 6->555, 7->565
        def init_color(self, commander):
            self.commander = commander

            self.pack(side=tk.TOP, fill=tk.X)
            self.colorTypeTK = tk.IntVar(value=0)
            self.nothing = tk.Radiobutton(self, value = 0, variable=self.colorTypeTK, command=self.button, text = "変更なし").grid(row = 0, column = 0, sticky = tk.W)
            self.black   = tk.Radiobutton(self, value = 1, variable=self.colorTypeTK, command=self.button, text = "二値化"  ).grid(row = 1, column = 0, sticky = tk.W)
            self.gray    = tk.Radiobutton(self, value = 2, variable=self.colorTypeTK, command=self.button, text = "グレー"  ).grid(row = 2, column = 0, sticky = tk.W)
            self.quantize= tk.Radiobutton(self, value = 3, variable=self.colorTypeTK, command=self.button, text = "減色"    ).grid(row = 3, column = 0, sticky = tk.W)
            self.quantize= tk.Radiobutton(self, value = 4, variable=self.colorTypeTK, command=self.button, text = "RGB332"  ).grid(row = 0, column = 1, sticky = tk.W)
            self.quantize= tk.Radiobutton(self, value = 5, variable=self.colorTypeTK, command=self.button, text = "RGB444"  ).grid(row = 1, column = 1, sticky = tk.W)
            self.quantize= tk.Radiobutton(self, value = 6, variable=self.colorTypeTK, command=self.button, text = "RGB555"  ).grid(row = 2, column = 1, sticky = tk.W)
            self.quantize= tk.Radiobutton(self, value = 7, variable=self.colorTypeTK, command=self.button, text = "RGB565"  ).grid(row = 3, column = 1, sticky = tk.W)
            self.colorsTK   = tk.IntVar(value = 127)
            self.colorLabel = tk.Label(self)
            self.colorBar = tk.Scale(self, from_ = 2, to=255, variable=self.colorsTK, command=self.button)
            return self

        def labelUpdate(self):
            if self.colorTypeTK.get() == 1:
                self.colorLabel["text"] = "基準の明るさ" + str(self.colorsTK.get())
            else:
                self.colorLabel["text"] = "色数：" + str(self.colorsTK.get())
        def button(self, event = None):
            if self.colorTypeTK.get() in [1, 3]:
                self.labelUpdate()
                self.colorLabel.grid()
                self.colorBar.grid()
            else:
                self.colorLabel.grid_forget()
                self.colorBar.grid_forget()

            self.commander.re_effect()

    class alphaEntry(tk.Labelframe):# 0-> no, 1-> black, 2-> 4bit
        def init_alpha(self, commander):
            self.commander = commander

            self.pack(side=tk.TOP, fill=tk.X)
            self.alphaTypeTK = tk.IntVar(value=0)
            self.nothing = tk.Radiobutton(self, value = 0, variable=self.alphaTypeTK, command = commander.re_effect, text = "変更なし").grid(row = 0, column = 0, sticky = tk.W)
            self.nothing = tk.Radiobutton(self, value = 1, variable=self.alphaTypeTK, command = commander.re_effect, text = "二値化"  ).grid(row = 1, column = 0, sticky = tk.W)
            self.nothing = tk.Radiobutton(self, value = 2, variable=self.alphaTypeTK, command = commander.re_effect, text = "4bit"   ).grid(row = 2, column = 0, sticky = tk.W)

            return self

    def re_effect(self, event = None):
        self.effected = self.nowCrop
        for effect in self.Effects:
            enhancer = effect.enhance(self.effected)
            self.effected = enhancer.enhance(effect.degreeTK.get() / 100 + 1)

        ct = self.colorEffect.colorTypeTK.get()
        cc = self.colorEffect.colorsTK.get()
        at = self.alphaEffect.alphaTypeTK.get()
        if ct or at:
            r, g, b, a = self.effected.split()
            if   ct == 1:
                l = Image.merge('RGB', (r, g, b)).convert("L")
                l = l.point(lambda x: 0 if x <= cc else 255)
                r = g = b = l
            elif ct == 2:
                l = Image.merge('RGB', (r, g, b)).convert("L")
                r = g = b = l
            elif ct == 3:
                r, g, b, a  = self.effected.quantize(cc).convert("RGBA").split()
            elif ct == 4:
                r = r.point(lambda x: base.bit8to(3, x))
                g = g.point(lambda x: base.bit8to(3, x))
                b = b.point(lambda x: base.bit8to(2, x))
            elif ct == 5:
                r = r.point(lambda x: base.bit8to(4, x))
                g = g.point(lambda x: base.bit8to(4, x))
                b = b.point(lambda x: base.bit8to(4, x))
            elif ct == 6:
                r = r.point(lambda x: base.bit8to(5, x))
                g = g.point(lambda x: base.bit8to(5, x))
                b = b.point(lambda x: base.bit8to(5, x))
            elif ct == 7:
                r = r.point(lambda x: base.bit8to(5, x))
                g = g.point(lambda x: base.bit8to(6, x))
                b = b.point(lambda x: base.bit8to(5, x))

            if   at == 1:
                a = a.point(lambda x: 0 if x == 0  else 255)
            elif at == 2:
                a = a.point(lambda x: base.bit8to(4, x))

            self.effected = Image.merge('RGBA', (r, g, b, a))
        
        self.imgShow.updateImg(img = self.effected)
    
    def start_after(self):
        return self.effected



