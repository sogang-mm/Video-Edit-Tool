from pymediainfo import MediaInfo
from PIL import Image as Image
from PIL import ImageQt
import subprocess
import image_transform as itrn
from queue import Queue
import json
import pickle as pkl


# import matplotlib.pyplot as plt


class Core:
    def __init__(self):
        self.transforms = []
        self.videos = []
        self.video = None
        self.thumbnail = None

    def clear_videos(self):
        self.videos = []

    def add_video(self, path):
        result = False
        idx = self.find_video_idx(path)
        if idx is None:
            v = Video(path)
            if v.valid:
                self.videos.append(v)
                result = True
        return result

    def remove_video_by_idx(self, idx):
        self.videos.pop(idx)

    def find_video_idx(self, path):
        idx = None
        indice = list(filter(lambda i: self.videos[i].path == path, range(len(self.videos))))
        if len(indice):
            idx = indice[0]
        return idx

    def select_video(self, idx):
        if idx is not None:
            self.video = self.videos[idx]
        return self.video

    def release_video(self):
        self.video = None

    def post_thumbnail(self, im):
        self.thumbnail = im

    def release_thumbnail(self):
        self.thumbnail = None

    def add_transform(self, trn):
        self.transforms.append(trn)

    def remove_transform(self, key):
        for n in range(len(self.transforms)):
            if self.transforms[n]['name'] == key:
                self.transforms.pop(n)
                break

    def clear_transforms(self):
        self.transforms = []

    def save_transforms(self, path):
        # with open(path, 'wb') as preset:
        #     pkl.dump(self.core.transforms, preset)
        json.dump({'transform': self.transforms}, open(path, 'w'), indent=2)

    def apply_thumbnail_transform(self, max_w, max_h):
        tt = ImageHelper.run_transform_with_PIL(self.thumbnail.copy(), self.transforms, self.video)
        tt = ImageHelper.thumbnail(tt, max_w, max_h)

        return tt

    def get_ffmpeg_transform_command(self, target):
        cmd = self.video.build_ffmpeg_transform_command(target, self.transforms)
        return cmd

    def get_ffmpeg_transform_command_format(self):
        return self.video.build_ffmpeg_transform_command_format(self.transforms)


class Video:
    def __init__(self, path):
        self.valid, self.meta = self.parse_video(path)

    # common
    def parse_video(self, path):
        meta = dict()
        valid = False
        try:
            media_info = MediaInfo.parse(path)
            for track in media_info.tracks:
                if track.track_type == 'General':
                    meta['duration'] = float(track.duration) / 1000 if track.duration is not None else 0.
                    meta['frame_rate'] = float(track.frame_rate) if track.frame_rate is not None else 0.
                    meta['frame_count'] = int(track.frame_count) if track.frame_count is not None else 0


                elif track.track_type == 'Video':
                    valid = True
                    meta['path'] = path
                    meta['rotation'] = float(track.rotation) if track.rotation is not None else 0.
                    meta['width'] = track.width if meta['rotation'] == 0 or meta['rotation'] == 180 else track.height
                    meta['height'] = track.height if meta['rotation'] == 0 or meta['rotation'] == 180 else track.width

            if meta['duration'] == 0. and meta['frame_rate'] != 0 and meta['frame_count'] != 0:
                meta['duration'] = meta['frame_count'] / meta['frame_rate']

            if meta['frame_count'] == 0 and meta['duration'] != 0 and meta['frame_rate'] != 0:
                meta['frame_count'] = int(meta['duration'] * meta['frame_rate'])

            if meta['frame_rate'] == 0 and meta['frame_count'] != 0 and meta['frame_rate'] != 0:
                meta['frame_rate'] = meta['frame_count'] / meta['duration']
        except Exception as e:
            print(f'Fail to parse video - {path} {e}')

        return valid, meta

    @property
    def path(self):
        return self.meta['path'] if self.valid else None

    def build_ffmpeg_thumbnail_command(self, w, h):
        cmd = ['ffmpeg',
               '-hide_banner', '-loglevel', 'panic',
               '-vsync', '2',
               '-ss', str(self.meta['duration'] / 2),
               '-i', self.meta["path"],
               '-vframes', '1',
               '-pix_fmt', 'bgr24',
               '-vf', f'scale={w}:{h}',
               '-q:v', '0',
               '-vcodec', 'rawvideo',
               '-f', 'image2pipe',
               'pipe:1'
               ]
        return cmd

    def get_thumbnail_with_subprocess(self, max_w, max_h):
        w, h = ImageHelper.get_maximum_size(self.meta['width'], self.meta['height'], max_w, max_h)
        cmd = self.build_ffmpeg_thumbnail_command(w, h)

        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=w * h * 3)
        stdout, stderr = pipe.communicate()

        if pipe.returncode == 0:
            im = Image.frombytes('RGB', (w, h), stdout, "raw", 'BGR')
        else:
            print(f'Exception while creating thumbnail.')
            im = Image.new('RGB', (w, h), color='gray')

        return im

    # transform
    def build_ffmpeg_transform_command_format(self, transforms):
        options = []
        extra_input = None
        for t in transforms:
            name, param = t['name'], t['param']
            if name == 'brightness':
                options += [f'eq=brightness={param["value"] / 100}']

            elif name == 'contrast':
                options += [f'eq=contrast={param["value"] * 0.03 + 1}']

            elif name == 'flip':
                if param['value'] == 'horizontal':
                    options += ['hflip']
                elif param['value'] == 'vertical':
                    options += ['vflip']
                elif param['value'] == 'all':
                    options += ['vflip,hflip']

            elif name == 'rotation':
                if param['value'] == 90:
                    options += ['transpose=1']
                elif param['value'] == 180:
                    options += ['transpose=2,transpose=2']
                elif param['value'] == 270:
                    options += ['transpose=2']

            elif name == 'framerate':
                options += [f'fps={param["value"]}']

            elif name == 'grayscale' and param['value']:
                options += ['format=gray']

            elif name == 'border':
                bw = param['w'] / 100
                bh = param['h'] / 100
                # options += [f'pad=w=(1+{bw})*iw:h=(1+{bh})*ih:x={bw}*iw/2:y={bh}*ih/2:color=black'] --> original(50%) 960x540 => 1440x810
                options += [
                    f'scale=iw*(1-{bw}):ih*(1-{bh}), pad=w=iw/(1-{bw}):h=ih/(1-{bh}):x=iw/(1-{bw})*{bw}/2:y=ih/(1-{bh})*{bh}/2:color=black']

            elif name == 'crop':
                r = param['value'] / 100
                # options += [f'crop=(1-{r})*iw:(1-{r})*ih:{r}*iw/2:{r}*ih/2'] --> original(50%) 950x540 => 480x270
                options += [
                    f'scale=iw*(1+{r}):ih*(1+{r}), crop=iw/(1+{r}):ih/(1+{r}):(iw/(1+{r}))*{r}/2:(ih/(1+{r}))*{r}/2']

            elif name == 'resolution':
                if param['selector'] == 'ratio':
                    r = (param['value'] + 100) / 100
                    options += [f'scale=ceil({r}*iw):ceil({r}*ih)']
                elif param['selector'] == 'preset':
                    if param['value'] == 'CIF':
                        options += ["scale = 'if(gte(iw\,ih)\,352\,240)':'if(gte(iw\,ih)\,240\,352)'"]

                    elif param['value'] == 'QCIF':
                        options += ["scale = 'if(gte(iw\,ih)\,176\,144)':'if(gte(iw\,ih)\,144\,176)'"]

                    elif param['value'] == 'SD':
                        options += ["scale = 'if(gte(iw\,ih)\,320\,240)':'if(gte(iw\,ih)\,240\,320)'"]

                    elif param['value'] == 'HD':
                        options += ["scale = 'if(gte(iw\,ih)\,1280\,720)':'if(gte(iw\,ih)\,720\,1280)'"]

                    elif param['value'] == '4K-UHD':
                        options += ["scale = 'if(gte(iw\,ih)\,3840\,2160)':'if(gte(iw\,ih)\,2160\,3840)'"]

                elif param['selector'] == 'value':
                    options += [f'scale={param["w"]}:{param["h"]}']

            elif name == 'caption':
                text = param['text']
                font_path = param['font_path'].replace('\\', '/')
                pt = param['pt']
                font_color = param['font_color']

                x = param['x']
                y = param['y']

                options += [
                    f"drawtext=text='{text}':x=(W-tw)*{x}/100:y=(H-th)*{y}/100:fontfile={font_path}:fontsize={pt}:fontcolor={font_color}"]

            elif name == 'logo':
                logo_path = param['path']
                size = param['size'] / 100
                x = param['x'] / 100
                y = param['y'] / 100

                extra_input = logo_path

                # resize logo
                prefix = f'[1][0]scale2ref=w=oh*mdar:h=main_h*sqrt((iw*ih*{size})/(main_w*main_h))[logo][input];'

                # apply previous transform
                if len(options):
                    prefix += f"[input]{','.join(options)}[input];"

                options = [f'{prefix}[input][logo]overlay=(main_w-overlay_w)*{x}:(main_h-overlay_h)*{y}']

        filter_complex_param = ','.join(options)
        format = ['ffmpeg', '-hide_banner', '-y', '-i', 'input_video_path']

        if extra_input is not None:
            format += ['-i', extra_input]
        format += ['-filter_complex', f'{filter_complex_param}', 'target_video_path']

        return format

    def fill_out_transform_command_format(self, target, format):
        return [self.meta['path'] if c == 'input_video_path' else target if c == 'target_video_path' else c for c in
                format]

    def build_ffmpeg_transform_command(self, target, transforms):
        format = self.build_ffmpeg_transform_command_format(transforms)
        cmd = self.fill_out_transform_command_format(target, format)
        return cmd

    def run_transform_with_subprocess(self, target, transforms):
        def yield_process(p):
            while p.poll() is None:
                line = p.stdout.readline().decode("utf8").strip()
                if line != '':
                    yield line

        cmd = self.build_ffmpeg_transform_command(target, transforms)

        pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)

        # for l in yield_process(pipe):
        #     print(l)

        line = [l.decode('utf8').strip() for l in pipe.stdout.readlines()]
        pipe.wait()

        return pipe.returncode, line


class ImageHelper:

    @classmethod
    def get_maximum_size(cls, w, h, max_w, max_h):

        r1, r2 = (max_w / w, max_h / h)
        nw, nh = (int(w * r1), int(h * r1)) if r1 < r2 else (int(w * r2), int(h * r2))

        return nw, nh

    @classmethod
    def thumbnail(cls, im, max_w, max_h):
        w, h = cls.get_maximum_size(*im.size, max_w, max_h)

        return im.resize((w, h))

    # @classmethod
    # def show(cls, im):
    #     plt.imshow(im)
    #     plt.show()

    @classmethod
    def run_transform_with_PIL(cls, im, transforms, vi):
        for t in transforms:
            name, param = t['name'], t['param']
            if name == 'brightness':
                im = itrn.brightness(im, param['value'])

            elif name == 'contrast':
                im = itrn.contrast(im, param['value'])

            elif name == 'flip':
                im = itrn.flip(im, param['value'])

            elif name == 'rotation':
                im = itrn.rotate(im, param['value'])

            elif name == 'framerate':
                im = im

            elif name == 'grayscale' and param['value']:
                im = itrn.grayscale(im)

            elif name == 'border':
                im = itrn.border(im, param['w'], param['h'])

            elif name == 'crop':
                im = itrn.crop(im, param['value'])

            elif name == 'resolution':
                nw, nh = w, h = im.size
                if param['selector'] == 'ratio':
                    r = (param['value'] + 100) / 100
                    nw, nh = int(r * w), int(r * h)

                if param['selector'] == 'preset':
                    if param['value'] == 'CIF':
                        nw, nh = (352, 240) if w > h else (240, 352)

                    elif param['value'] == 'QCIF':
                        nw, nh = (176, 144) if w > h else (144, 176)

                    elif param['value'] == 'SD':
                        nw, nh = (320, 240) if w > h else (240, 320)

                    elif param['value'] == 'HD':
                        nw, nh = (1280, 720) if w > h else (720, 1280)

                    elif param['value'] == '4K-UHD':
                        nw, nh = (3840, 2160) if w > h else (2160, 3840)

                if param['selector'] == 'value':
                    nw, nh = int(param['w']), int(param['h'])

                im = itrn.resize(im, nw, nh)

            elif name == 'caption':
                v_w = vi.meta['width']
                im = itrn.caption(im, param['text'], param['font_path'], param['pt'], param['font_color'], param['x'],
                                  param['y'], v_w)

            elif name == 'logo':
                im = itrn.logo(im,
                               param['path'],
                               param['size'],
                               param['x'], param['y'])

        return im

    @classmethod
    def to_pixmap(cls, im):
        return ImageQt.toqpixmap(im)


class pQueue(Queue):
    def __init__(self, items, maxsize=0):
        super(pQueue, self).__init__(maxsize)
        for item in items:
            self.put(item)

    def peek(self):
        return self.queue[0] if not self.empty() else None


if __name__ == '__main__':
    v = Video('a.mp4')
    thumb = v.get_thumbnail_with_subprocess(100, 200)
    # ImageHelper.show(thumb)

    trn = {'transform': [
        {'name': 'logo',
         'param':
             {'path': 'C:\\Users\\ms\\Documents\\ShareX\\Screenshots\\2021-04\\b.jpg',
              'x': 30,
              'y': 50,
              'size': 10}},
        {'name': 'brightness', 'param': {'value': 20}}]}

    o = v.build_ffmpeg_transform_command('o.mp4', transforms=trn['transform'])
    print(o)

    v.run_transform_with_subprocess('p.mp4', transforms=trn['transform'])
