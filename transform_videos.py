from core import *

import sys
import json
import os
import traceback
import shutil

if __name__ == '__main__':
    argv = sys.argv
    argc = len(argv)

    assert argc == 5, f'{argc} {argv}'
    msg = ' '.join(argv)
    _, path, target, trn, suffix = argv
    path = os.path.normpath(os.path.normcase(path))
    name, ext = os.path.splitext(os.path.basename(path))

    target = os.path.normpath(os.path.normcase(target))
    log = os.path.join(target, f'{name}{suffix}_END.log')
    try:

        if not os.path.exists(path):
            raise Exception(f'{path} doesn\'t exist.')

        if not os.path.exists(trn):
            raise Exception(f'{trn} doesn\'t exist.')

        if not os.path.exists(target):
            os.makedirs(target)

        output = os.path.join(target, f'{name}{suffix}{ext}')

        msg += '\n'
        msg += f'input : {os.path.normcase(path).capitalize()}\n'
        msg += f'output : {os.path.normcase(output).capitalize()}\n'

        video = Video(path)
        transform = json.load(open(trn, 'r'))['transform']

        if len(transform):
            cmd = video.build_ffmpeg_transform_command(output, transforms=transform)

            pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)
            line = [l.decode('utf8').strip() for l in pipe.stdout.readlines()]

            pipe.wait()

            msg += f'command: {cmd}\n'
            msg += 'log : \n\t\t'
            msg += '\n\t\t'.join(line)

            if pipe.returncode != 0:
                raise Exception('Fail to execute ffmpeg Command.')
        else:
            shutil.copy2(path, output)

    except Exception as e:
        log = os.path.join(target, f'{name}{suffix}_FAIL.log')
        msg += '\n'
        msg += traceback.format_exc()

    finally:
        print(log)
        with open(log, 'w') as f:
            f.write(msg)
