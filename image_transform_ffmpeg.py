from PIL import Image
from image_transform import time, time2

import subprocess
from io import BytesIO


def brightness_ffmpeg(im, v):
    cmd = ['ffmpeg', '-hide_banner', '-y', '-i', '-', '-filter_complex', f'eq=brightness={v}/ 100',
           '-q:v', '0',
           '-vcodec', 'rawvideo',
           '-pix_fmt', 'bgr24',
           '-f', 'image2pipe',
           'pipe:1']

    w, h = im.size

    in_stream = BytesIO()
    im.save(in_stream, format='JPEG')

    pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            bufsize=w * h * 3)

    stdout, stderr = pipe.communicate(input=in_stream.getvalue())

    if pipe.returncode == 0:
        image = Image.frombytes("RGB", im.size, stdout, "raw", 'BGR')
    else:
        print(f'Exception while changing brightness.')
        image = Image.new('RGB', im.size, color='gray')

    return image


if __name__ == '__main__':
    import image_transform as it

    im = Image.open('a.jpg')

    for _ in range(10):
        b = time2(it.brightness, im, 30)
        c = time2(brightness_ffmpeg, im, 30)
