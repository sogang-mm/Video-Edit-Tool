from core import *

import sys
import json
import os


if __name__ == '__main__':
    argv = sys.argv
    argc = len(argv)

    assert argc == 5, f'{argc} {argv}'

    _, path, target, trn, suffix = argv
    assert os.path.exists(path), f'{path} isn\'t exist'

    assert os.path.isdir(target), f'{target} is not directory'
    if not os.path.exists(target):
        os.makedirs(target)
    assert os.path.exists(trn), f'{trn} isn\'t exist'

    path=os.path.normpath(os.path.normcase(path))
    target=os.path.normpath(os.path.normcase(target))
    name, ext = os.path.splitext(os.path.basename(path))
    output = os.path.join(target, f'{name}{suffix}{ext}')

    video = Video(path)
    transform = json.load(open(trn, 'r'))

    cmd = video.build_ffmpeg_transform_command(output, transforms=transform['transform'])

    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
    line = [l.decode('utf8').strip() for l in pipe.stdout.readlines()]

    pipe.wait()

    if pipe.returncode == 0:
        log = os.path.join(target, f'{name}{suffix}_END.log')
    else:
        log = os.path.join(target, f'{name}{suffix}_FAIL.log')

    text = f'input : {os.path.normcase(path).capitalize()}\n'
    text += f'output : {os.path.normcase(output).capitalize()}\n'
    text += f'command: {cmd}\n'
    text += 'log : \n\t\t'
    text += '\n\t\t'.join(line)

    with open(log, 'w') as f:
        f.write(text)

