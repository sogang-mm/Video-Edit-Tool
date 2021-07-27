import os.path

import ffmpeg
import json

from core import *

import sys


class V(Video):
    def __init__(self, path):
        super(V, self).__init__(path)

    def build(self, target, transforms):
        stream = ffmpeg.input(self.path)
        ref = []

        iw, ih = self.meta['width'], self.meta['height']
        for t in transforms:
            name, param = t['name'], t['param']
            if name == 'brightness':
                stream = stream.filter('eq', brightness=param['value'] * 0.01)
            elif name == 'contrast':
                stream = stream.filter('eq', contrast=param['value'] * 0.01 + 1)
            elif name == 'flip':
                if param['value'] == 'horizontal':
                    stream = stream.hflip()
                elif param['value'] == 'vertical':
                    stream = stream.vflip()
                elif param['value'] == 'all':
                    stream = stream.hflip().vflip()
            elif name == 'rotation':
                if param['value'] == 90:
                    stream = stream.filter('transpose', 1)
                elif param['value'] == 180:
                    stream = stream.filter('transpose', 2).filter('transpose', 2)
                elif param['value'] == 270:
                    stream = stream.filter('transpose', 2)
            elif name == 'framerate':
                stream = stream.filter('fps', param['value'])
            elif name == 'grayscale' and param['value']:
                stream = stream.filter('hue', s=0)

            elif name == 'border':
                bw, bh = param['w'] * 0.01, param['h'] * 0.01
                _stream = ffmpeg.filter_multi_output(stream, 'split')
                pad = _stream[0].filter('pad',
                                        w=f'ceil(iw*{1 + bw}*0.5)*2',
                                        h=f'ceil(ih*{1 + bh}*0.5)*2',
                                        x='ceil((ow-iw)*0.5)',
                                        y='ceil((oh-ih)*0.5)',
                                        color='black')
                _stream = ffmpeg.filter_multi_output([pad, _stream[1]], 'scale2ref', w='iw', h='ih')

                ref.append(_stream[1])
                stream = _stream[0]

            elif name == 'crop':
                r = param['value'] * 0.01

                _stream = ffmpeg.filter_multi_output(stream, 'split')

                crop = _stream[0].filter('crop',
                                         w=f'ceil((1-{r})*iw*0.5)*2',
                                         h=f'ceil((1-{r})*ih*0.5)*2',
                                         x='(iw-ow)*0.5',
                                         y='(ih-oh)*0.5')

                _stream = ffmpeg.filter_multi_output([crop, _stream[1]],
                                                     'scale2ref',
                                                     w=f'iw',
                                                     h=f'ih')
                ref.append(_stream[1])
                stream = _stream[0]

            elif name == 'resolution':
                rw, rh = iw, ih
                if param['selector'] == 'ratio':
                    r = (param['value'] + 100) * 0.01
                    rw, rh = iw * r, ih * r
                elif param['selector'] == 'preset':
                    val = param['value']
                    if val == 'CIF':
                        rw, rh = 352, 240
                    elif val == 'QCIF':
                        rw, rh = 176, 144
                    elif val == 'SD':
                        rw, rh = 320, 240
                    elif val == 'HD':
                        rw, rh = 1280, 720
                    elif val == '4K-UHD':
                        rw, rh = 3840, 2160

                    rw, rh = (rw, rh) if iw > ih else (rh, rw)
                elif param['selector'] == 'value':
                    rw, rh = param['w'], param['h']
                stream = stream.filter('scale', w=f'ceil({rw}*0.5)*2', h=f'ceil({rh}*0.5)*2')

            elif name == 'caption':
                font_path = os.path.normpath(param['font_path'])
                x = param['x'] * 0.01
                y = param['y'] * 0.01
                stream = stream.filter('drawtext',
                                       text=param['text'],
                                       x=f'(W-tw)*{x}',
                                       y=f'(H-th)*{y}',
                                       fontcolor=param['font_color'],
                                       fontsize=param['pt'],
                                       fontfile=font_path)

            elif name == 'logo':
                r = param['size'] * 0.01
                x, y = param['x'] * 0.01, param['y'] * 0.01
                logo = ffmpeg.input(param['path'])
                _stream = ffmpeg.filter_multi_output([logo, stream],
                                                     'scale2ref',
                                                     w=f'oh*mdar',
                                                     h=f'sqrt(iw*ih*{r}/main_w/main_h)*main_h')

                stream = _stream[1].overlay(_stream[0],
                                            x=f'(main_w-overlay_w)*{x}',
                                            y=f'(main_h-overlay_h)*{y}')

            elif name == 'camcording':
                r = param['ratio'] * 0.01
                background = ffmpeg.input(param['path'])
                _stream = ffmpeg.filter_multi_output([background, stream],
                                                     'scale2ref',
                                                     w='iw',
                                                     h='ih')

                vid = _stream[1].filter('scale',
                                        w=f'ceil(iw*{r}*0.5)*2',
                                        h=f'ceil(ih*{r}*0.5)*2')

                stream = _stream[0].overlay(vid, x=f'(main_w-overlay_w)/2', y='(main_h-overlay_h)/2')

        if len(transforms):
            kwargs = {'q:v': 0,
                      'max_muxing_queue_size': 9999}
        else:
            kwargs = {'c': 'copy'}

        stream = stream.output(target, **kwargs)
        ref = [r.output('/dev/null', format='null') for r in ref]

        stream = ffmpeg.merge_outputs(stream, *ref)
        stream = stream.global_args('-hide_banner')
        stream = stream.overwrite_output()

        stream.run()
        stream.view(filename='graph.png')
        return stream.compile()


def test__multi_output_edge_label_order():
    scale2ref = ffmpeg.filter_multi_output([ffmpeg.input('a.mp4'), ffmpeg.input('a.jpg')], 'scale2ref')
    out = (
        ffmpeg.merge_outputs(
            scale2ref[1].filter('scale').output('a'),
            scale2ref[10000].filter('hflip').output('b')
        )
    )

    args = out.get_args()
    print(args)
    assert args == [
        '-i',
        'x',
        '-i',
        'y',
        '-filter_complex',
        '[0][1]scale2ref[s0][s1];[s0]scale[s2];[s1]hflip[s3]',
        '-map',
        '[s2]',
        'a',
        '-map',
        '[s3]',
        'b'
    ]


path = './a.mp4'
trn = json.load(open('./test2.json', 'r'))['transform']

video = V(path)
print(video)
c = video.build('test.mp4', transforms=trn)
print(c)

