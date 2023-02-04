#ver5
import math
from PIL.Image import *
from PIL import ImageEnhance
from PIL.ImageTk import PhotoImage
import numpy

from typing import List, Tuple, Optional, Union
TypeVec = Optional[List[int]]

def _repeatx(im: Image, column: int) -> Image:
    dst = new('RGBA', (im.width * column, im.height))
    for x in range(column):
        dst.paste(im, (x * im.width, 0))
    return dst

def _repeaty(im: Image, row: int) -> Image:
    dst = new('RGBA', (im.width, im.height * row))
    for y in range(row):
        dst.paste(im, (0, y * im.height))
    return dst

def repeat(im:Image, row: int = 0, column: int = 0, size: TypeVec = None) -> Image:
    if size:
        row    = math.ceil(im.height/ size[1])
        column = math.ceil(im.width / size[0])

    if row * column:
        dst_h = _repeatx(im, column)
        dst   = _repeaty(dst_h, row)
    
    if size:
        dst = dst.crop((0, 0, size[0], size[1]))
    
    return dst

def transparentImg(width: int = 0, height: int = 0, size: TypeVec = None, back: int = 255) -> Image:
    if size:
        width  = size[0]
        height = size[1]
    img: Image = new("L", (2, 2), back)
    img.putpixel((1, 0), 127)
    img.putpixel((0, 1), 127)#ここまでで2*2サイズの画像をつくる
    img = img.resize((4, 4),resample= Resampling.NEAREST)#4*4サイズに拡大

    dst: Image = new("L", (width, height), 255)
    for y in range(math.ceil(height/4)):
        for x in range(math.ceil(width/4)):
            dst.paste(img, [x*4, y*4])
    return(dst)

def alphaPaste(back: Image, front: Image, point: TypeVec, changeSize:bool = False) -> Image:
    if changeSize:
        new_width  = max(back.width, point[0]+front.width)
        new_height = max(back.height, point[1]+front.height)
        backN = new("RGBA", (new_width, new_height))
        backN.paste(back, (0, 0))
        frontN = new("RGBA", (new_width, new_height))
    else:
        backN = back
        frontN = new("RGBA", back.size)
    frontN.paste(front, (point[0], point[1]))
    dst = alpha_composite(backN, frontN)
    return(dst)

def darken(img: Image, brightness: float = 0.5) -> Image:
    img = ImageEnhance.Brightness(img)
    return img.enhance(brightness)

def skew(image: Image, h: float, v: float, rad:bool = False) -> Image:
    if not rad:
        h = math.radians(h)
        v = math.radians(v)
    '''imageを水平角度hと垂直角度vで平行四辺形化する'''

    # アフィン変換後の画像のサイズを求める
    add_width = abs(round(image.height * math.tan(h)))
    add_height = abs(round(image.width * math.tan(v)))
    size = (image.width + add_width, image.height + add_height)


    # 平行四辺形化用の行列を作成
    skew_matrix = numpy.array([
        [1, math.tan(h), 0],
        [math.tan(v), 1, 0],
        [0, 0, 1]
    ])

    # 画像の平行移動量を計算
    th = add_width if h < 0 else 0
    tv = add_height if v < 0 else 0

    # 平行移動用の行列を作成
    translate_matrix = numpy.array([
        [1, 0, th],
        [0, 1, tv],
        [0, 0, 1]
    ])

    # ２つの行列の積を取った結果をアフィン変換用の行列とする
    matrix = numpy.matmul(translate_matrix, skew_matrix)

    # アフィン変換用の行列の逆行列を作成する
    try:
        inv_matrix = numpy.linalg.inv(matrix)
    except numpy.linalg.LinAlgError:
        # 逆行列の作成に失敗したらNoneを返却
        return None

    # 逆行列を１次元の行列に変換する
    matrix_tupple = tuple(inv_matrix.flatten())

    # アフィン変換を行う
    skewed_image = image.transform(
        size=size,  # アフィン変換後に得られる画像のサイズ
        method=Transform.AFFINE,  # 行う変換（アフィン変換）
        data=matrix_tupple,  # アフィン変換時に用いる行列
        resample=Resampling.BILINEAR,  # 補間アルゴリズム（双線形補間）
        fillcolor=(0, 0, 0, 0)  # 余白を埋める画素の値（透明）
    )

    # 平行四辺形化後画像を返却
    return skewed_image

def resize2(im: Image, width = 0, height = 0, size:TypeVec = None, protrude = False, resample = Resampling.NEAREST) -> Image:
    if size:  width, height = size
    if width and height:
        magw = width  / im.width
        magh = height / im.height
        mag = max(magw, magh) if protrude else min(magw, magh)
        width = round(im.width * mag)
        height = round(im.height * mag)
    elif width:
        height = im.height * width  / im.width
    elif height:
        width  = im.width *  height / im.height
    else:
        raise ValueError("width, height or size is necessary.")
    
    dst = im.resize([width, height], resample=resample)
    return dst

def crop2(im: Image, box: List, width:int, height:int, size:TypeVec, startxy:TypeVec = (0, 0)):
    if box: return im.crop(box)
    finxy = [0, 0]
    if size:
        finxy[0] = min(size[0] + width,  im.width)
        finxy[1] = min(size[1] + height, im.height)
    else:
        finxy = [im.width, im.height]
        raise ValueError("box, width, height or size is necessary.")
    
    return im.crop(box = (startxy[0], startxy[1], finxy[0], finxy[1]))

def makeCube(top: Image, front:Image, side:Image, length:int = 0):
    if length:
        front = front.resize((length, length))
    else: 
        length = max(front.width, front.height)
    ln2 = int(length / 2)
    top  = skew(top.resize((length, ln2)), -45,   0)
    side = skew(side.resize((ln2, length)),  0, -45)
    dst = new("RGBA", size = (length + ln2, length + ln2))
    dst = alphaPaste(dst, top,   (     0, 0))
    dst = alphaPaste(dst, front, (     0, ln2))
    dst = alphaPaste(dst, side,  (length, 0))
    return dst

def N_classic(img:Image):
    width = img.width
    height = img.height
    np_img = numpy.asarray(img.convert("RGB"))
    palette= ( ( 39,  27, 143),
(  0,   0, 171),
( 71,   0, 159),
(  0, 115, 239),
( 35,  59, 239),
(131,   0, 243),
( 63, 191, 255),
( 95, 115, 255),
(167, 139, 253),
(255, 255, 255),
(171, 231, 255),
(199, 215, 255),
(215, 203, 255),
(143,   0, 119),
(171,   0,  19),
(167,   0,   0),
(127,  11,   0),
(191,   0, 191),
(231,   0,  91),
(219,  43,   0),
(203,  79,  15),
(247, 123, 255),
(255, 119, 183),
(255, 119,  99),
(255, 155,  59),
(255, 199, 255),
(255, 199, 219),
(255, 191, 179),
(255, 219, 171),
( 67,  47,   0),
(  0,  71,   0),
(  0,  81,   0),
(  0,  63,  23),
(139, 115,   0),
(  0, 151,   0),
(  0, 171,   0),
(  0, 147,  59),
(243, 191,  63),
(131, 211,  19),
( 79, 223,  75),
( 88, 248, 152),
(255, 231, 163),
(227, 255, 163),
(171, 243, 191),
(179, 255, 207),
( 27,  63,  95),
(  0,   0,   0),
(  0, 131, 139),
(  0, 235, 219),
(117, 117, 117),
(159, 255, 243),
(188, 188, 188),)
    for y in range(height):
        for x in range(width):
            mini = 100
            minicolor = None
            for color in palette:
                delta = numpy.linalg.norm(np_img[y][x] - color)
                if mini > delta :
                    delta = mini
                    minicolor = color
            np_img[y][x] = minicolor
    
    return fromarray(np_img)

