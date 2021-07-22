from PIL import Image, ImageEnhance, ImageOps, ImageFont, ImageDraw
from datetime import datetime
import math


# decorator
def time(func):
    def wrap(*args, **kwargs):
        t1 = datetime.now()
        func(*args, **kwargs)
        t2 = datetime.now()
        print(t2 - t1)

    return wrap


# function pointer
def time2(func, *args, **kwargs):
    t1 = datetime.now()
    o = func(*args, **kwargs)
    t2 = datetime.now()
    print(t2 - t1)
    return o


def brightness(im, v):
    factor = (100 + v) / 100
    enhancer = ImageEnhance.Brightness(im)

    t_im = enhancer.enhance(factor)
    return t_im


def contrast(im, v):
    factor = (100 + v) / 100
    enhancer = ImageEnhance.Contrast(im)

    t_im = enhancer.enhance(factor)
    return t_im


def resize(im, w, h):
    return im.resize((w, h))


def flip(im, level):
    if level == 'horizontal':
        t_im = ImageOps.mirror(im)
    elif level == 'vertical':
        t_im = ImageOps.flip(im)
    elif level == 'all':
        t_im = ImageOps.mirror(ImageOps.flip(im))
    else:
        t_im = im
    return t_im


def rotate(im, level):
    if level == 90:
        level = 270
    elif level == 270:
        level = 90
    return im.rotate(level, expand=True)


def grayscale(im):
    return im.convert('L').convert('RGB')


def logo(im, logo, size, x, y):
    l = Image.open(logo).convert('RGB')
    t_im = im.copy()

    lw, lh = l.size
    w, h = im.size

    r = math.sqrt(w * h * size * 0.01 / lw / lh)
    nlw, nlh = int(r * lw), int(r * lh)

    lx = int((w - nlw) * x * 0.01)
    ly = int((h - nlh) * y * 0.01)

    nl = l.resize((nlw, nlh))
    t_im.paste(nl, (lx, ly))

    return t_im


def camcording(im, bg, ratio, frame_meta):
    l = Image.open(bg).convert('RGB')
    t_im = im.copy().resize((frame_meta['width'], frame_meta['height']))

    r = ratio / 100

    t_w, t_h = t_im.size

    l = l.resize((int(frame_meta['width'] * (1 + r)), int(frame_meta['height'] * (1 + r))))

    lw, lh = l.size
    # print(f'lw : {lw}, lh : {lh}')
    l.paste(t_im, (int((lw - t_w) / 2), int((lh - t_h) / 2)))

    return l


def caption(im, text, font_path, pt, font_color, x, y, v_w):
    l = im.copy()  # fg
    w, h = l.size

    pt = int(pt / v_w * w)

    font = ImageFont.truetype(font_path, pt)
    t_w, t_h = font.getsize(text)
    draw = ImageDraw.Draw(l)
    draw.text(((w - t_w) * x / 100, (h - t_h) * y / 100), text, fill=font_color, font=font, align='center')

    return l


def border(im, bw, bh):
    w, h = im.size
    nw = int(w * (100 + bw) / 100)
    nh = int(h * (100 + bh) / 100)

    mx = int((nw - w) / 2)
    my = int((nh - h) / 2)
    t_im = Image.new('RGB', (nw, nh))
    t_im.paste(im, (mx, my))
    return t_im


def crop(im, v):
    w, h = im.size

    nw = w * (100 - v) / 100
    nh = h * (100 - v) / 100
    left = int((w - nw) / 2)
    top = int((h - nh) / 2)
    right = int((w + nw) / 2)
    bottom = int((h + nh) / 2)

    t_im = im.crop((left, top, right, bottom))
    return t_im

# def show(im):
#     import matplotlib.pyplot as plt
#     plt.imshow(im)
#     plt.show()
