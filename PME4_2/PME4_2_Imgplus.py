#ver4.2
import math
from PIL.Image import *
from PIL import ImageEnhance
import numpy

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

def repeat(im:Image, row: int = 0, column: int = 0, size: list = []) -> Image:
    if size:
        row    = math.ceil(im.height/ size[1])
        column = math.ceil(im.width / size[0])

    if row * column:
        dst_h = _repeatx(im, column)
        dst   = _repeaty(dst_h, row)
    
    if size:
        dst = dst.crop((0, 0, size[0], size[1]))
    
    return dst

def transparentImg(width: int = 0, height: int = 0, size: list = [], back: int = 255) -> Image:
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

def alphaPaste(back: Image, front: Image, point: list, changeSize:bool = False) -> Image:
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

def darken(img: Image, brightness: int = 0.5) -> Image:
    img = ImageEnhance.Brightness(img)
    return img.enhance(brightness)

def skew(image: Image, h: int, v: int, rad:bool = False) -> Image:
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