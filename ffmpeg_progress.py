"""
This is based on ffmpeg-progress.sh by Rupert Plumridge
https://gist.github.com/pruperting/397509/1068d4ced44ded986d0f52ddb4253cfee40921a7
"""
from datetime import datetime
from os.path import basename, isdir, join as path_join, splitext
from time import sleep
from tempfile import mkstemp
from typing import Any, BinaryIO, Callable, Dict, Optional
import json
import os
import re
import subprocess as sp
import sys

OnMessageCallback = Callable[[float, int, int, float], None]


def ffprobe(infile: str) -> Dict[str, Any]:
    """ffprobe front-end."""
    proc = sp.run(['ffprobe',
                   '-v', 'quiet',
                   '-print_format', 'json',
                   '-show_format',
                   '-show_streams',
                   infile], encoding='utf-8', stdout=sp.PIPE)
    return json.loads(proc.stdout)


def _default_on_message(percent: float,
                        fr_cnt: int,
                        total_frames: int,
                        elapsed: float):
    bar = list('|' + (20 * ' ') + '|')
    to_fill = int(round((fr_cnt / total_frames) * 20)) or 1
    for x in range(1, to_fill):
        bar[x] = '░'
    bar[to_fill] = '░'
    bar = ''.join(bar)

    sys.stdout.write('\r{}  {:5.1f}%   {:d} / {:d} frames;   '
                     'elapsed time: {:.2f} seconds'.format(
                        bar, percent, fr_cnt, total_frames, elapsed))
    sys.stdout.flush()


def _display(total_frames: int,
             vstats_handle: BinaryIO,
             on_message: Optional[OnMessageCallback] = None,
             wait_time: int = 1):
    start = datetime.now()
    fr_cnt = eta = elapsed = percent = 0
    if not on_message:
        on_message = _default_on_message

    while fr_cnt < total_frames:
        sleep(wait_time)

        vstats_handle.seek(-2, os.SEEK_END)
        while vstats_handle.read(1) != b'\n':
            vstats_handle.seek(-2, os.SEEK_CUR)
        last = vstats_handle.readline().decode('utf-8').strip()
        try:
            vstats = int(re.sub(r'\s+', ' ', last).split(' ')[5])
        except IndexError:
            vstats = 0
        if vstats > fr_cnt:
            fr_cnt = vstats
            percent = 100 * (fr_cnt / total_frames)
            elapsed = (datetime.now() - start).total_seconds()

        on_message(percent, fr_cnt, total_frames, elapsed)


def start(infile: str,
          outfile: str,
          ffmpeg_func: Callable[[str, str, str], int],
          on_message: Optional[OnMessageCallback] = None,
          on_done: Optional[Callable[[], None]] = None,
          index: int = 0,
          wait_time: int = 1):
    """
    The starting point.

    Pass an input file path, an output file path, and a callable.

    The callable (signature: (infile, outfile, vstats_file) -> int) passed in
    is expected to start the ffmpeg process and pass the given stats path to
    the process (last argument):

    ffmpeg -y -vstats_file ... -i ...

    The callable must return the PID of the ffmpeg process.

    The on_message argument may be used to override the messaging, which by
    default writes to sys.stdout with basic information on the progress. It
    receives 4 arguments: percentage, frame count, total_frames, elapsed time
    in seconds.

    If the FPS or the total number of frames cannot be calculated from
    the input file with ffprobe, a ValueError will be raised.

    The wait_time (seconds) argument may be used to slow down the number of
    messages. A higher wait time will mean fewer messages. Very small values
    may not work.

    Only Linux is supported at this time.
    """
    probe = ffprobe(infile)
    try:
        probe['streams'][index]
    except (IndexError, KeyError):
        raise ValueError('Probe failed')
    try:
        fps = eval(probe['streams'][index]['avg_frame_rate'])
    except ZeroDivisionError:
        raise ValueError('Cannot use input FPS')
    if fps == 0:
        raise ValueError('Unexpected zero FPS')
    dur = float(probe['format']['duration'])
    total_frames = int(dur * fps)

    if total_frames <= 0:
        raise ValueError('Unexpected total frames value')

    prefix = 'ffprog-{}'.format(splitext(basename(infile))[0])
    vstats_fd, vstats_path = mkstemp(suffix='.vstats', prefix=prefix)
    pid = ffmpeg_func(infile, outfile, vstats_path)
    sleep(wait_time)

    with open(vstats_fd, 'rb') as f:
        _display(total_frames,
                 f,
                 wait_time=wait_time,
                 on_message=on_message)

    if on_done:
        on_done()


def _main():
    def ffmpeg(infile: str, outfile: str, vstats_path: str):
        p = sp.Popen(['ffmpeg',
                      '-y',
                      '-vstats_file', vstats_path,
                      '-i', infile] + sys.argv[2:] + [
                      outfile], stdout=sp.PIPE, stderr=sp.PIPE)
        return p.pid

    try:
        prefix = splitext(basename(sys.argv[1]))[0]
    except IndexError:
        print('Usage: {} INFILE [FFMPEG OUTPUT ARGS]'.format(sys.argv[0]),
              file=sys.stderr)
        return 1
    outfile = '{}.mp4'.format(prefix)
    try:
        start(sys.argv[1], outfile, ffmpeg, on_done=lambda: print(''))
    except (KeyboardInterrupt, ValueError) as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(_main())
