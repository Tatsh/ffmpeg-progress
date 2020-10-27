"""
This is based on ffmpeg-progress.sh by Rupert Plumridge
https://gist.github.com/pruperting/397509/1068d4ced44ded986d0f52ddb4253cfee40921a7
"""
from datetime import datetime
from os.path import basename, splitext
from tempfile import mkstemp
from time import sleep
from typing import Callable, Optional, Sequence, cast
import json
import os
import re
import subprocess as sp
import sys

from typing_extensions import TypedDict
import psutil

__all__ = (
    'OnMessageCallback',
    'ffprobe',
    'start',
)

OnMessageCallback = Callable[[float, int, int, float], None]
LINESEP_BYTES = os.linesep.encode('utf-8')


class ProbeStreamDict(TypedDict):
    avg_frame_rate: str


class ProbeFormatDict(TypedDict):
    duration: float


class ProbeDict(TypedDict, total=False):
    format: ProbeFormatDict
    streams: Sequence[ProbeStreamDict]


def ffprobe(in_file: str) -> ProbeDict:
    """ffprobe front-end."""
    return cast(
        ProbeDict,
        json.loads(
            sp.check_output(('ffprobe', '-v', 'quiet', '-print_format', 'json',
                             '-show_format', '-show_streams', in_file),
                            encoding='utf-8')))


def default_on_message(percent: float, fr_cnt: int, total_frames: int,
                       elapsed: float) -> None:
    """Default callback for display()."""
    bar_ = list('|' + (20 * ' ') + '|')
    to_fill = int(round((fr_cnt / total_frames) * 20)) or 1
    for x in range(1, to_fill):
        bar_[x] = '░'
    bar_[to_fill] = '░'
    s_bar = ''.join(bar_)
    sys.stdout.write('\r{}  {:5.1f}%   {:d} / {:d} frames;   '
                     'elapsed time: {:.2f} seconds'.format(
                         s_bar, percent, fr_cnt, total_frames, elapsed))
    sys.stdout.flush()


def display(total_frames: int,
            vstats_fd: int,
            pid: int,
            on_message: Optional[OnMessageCallback] = None,
            wait_time: float = 1.0) -> None:
    """
    Generates messages for display of progress. Call on_message argument when
    one is available.
    """
    start_time = datetime.now()
    fr_cnt = 0
    elapsed = percent = 0.0
    if not on_message:
        on_message = default_on_message
    while fr_cnt < total_frames and percent < 100.0:
        sleep(wait_time)
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            break
        if psutil.Process(pid).status() == psutil.STATUS_ZOMBIE:
            break
        try:
            pos_end = os.lseek(vstats_fd, -2, os.SEEK_END)
        except OSError:
            continue  # Not enough data in file
        pos_start = None
        while os.read(vstats_fd, 1) != LINESEP_BYTES:
            pos_start = os.lseek(vstats_fd, -2, os.SEEK_CUR)
        if pos_start is None:
            continue
        last = os.read(vstats_fd, pos_end - pos_start).decode('utf-8').strip()
        try:
            vstats = int(re.split(r'\s+', last)[5])
        except IndexError:
            vstats = 0
        if vstats > fr_cnt:
            fr_cnt = vstats
            percent = 100 * (fr_cnt / total_frames)
        elapsed = (datetime.now() - start_time).total_seconds()
        on_message(percent, fr_cnt, total_frames, elapsed)


def start(in_file: str,
          outfile: str,
          ffmpeg_func: Callable[[str, str, str], int],
          on_message: Optional[OnMessageCallback] = None,
          on_done: Optional[Callable[[], None]] = None,
          index: int = 0,
          wait_time: float = 1.0,
          initial_wait_time: float = 2.0) -> None:
    """
    The starting point.

    Pass an input file path, an output file path, and a callable.

    The callable (signature: (in_file, outfile, vstats_file) -> Any) passed in
    is expected to start the ffmpeg process and pass the given stats path to
    the process (last argument):

    ffmpeg -y -vstats_file ... -i ...

    The on_message argument may be used to override the messaging, which by
    default writes to sys.stdout with basic information on the progress. It
    receives 4 arguments: percentage, frame count, total_frames, elapsed time
    in seconds.

    If the FPS or the total number of frames cannot be calculated from
    the input file with ffprobe, a ValueError will be raised.

    The wait_time (seconds) argument may be used to slow down the number of
    messages. A higher wait time will mean fewer messages. Very small values
    may not work.

    The initial_wait_time (seconds) argument may be used to set an initial
    interval to wait before processing the log file.

    Only Linux is supported at this time.
    """
    probe = ffprobe(in_file)
    try:
        probe['streams'][index]
    except (IndexError, KeyError) as e:
        raise ValueError('Probe failed') from e
    try:
        fps = cast(float, eval(probe['streams'][index]['avg_frame_rate']))  # pylint: disable=eval-used
    except ZeroDivisionError as e:
        raise ValueError('Cannot use input FPS') from e
    if fps == 0:
        raise ValueError('Unexpected zero FPS')
    dur = float(probe['format']['duration'])
    total_frames = int(dur * fps)
    if total_frames <= 0:
        raise ValueError('Unexpected total frames value')
    prefix = 'ffprog-{}'.format(splitext(basename(in_file))[0])
    vstats_fd, vstats_path = mkstemp(suffix='.vstats', prefix=prefix)
    pid = ffmpeg_func(in_file, outfile, vstats_path)
    if not pid:
        raise TypeError('ffmpeg callback must return a valid PID')
    sleep(initial_wait_time)
    display(total_frames,
            vstats_fd,
            pid,
            wait_time=wait_time,
            on_message=on_message)
    os.close(vstats_fd)
    if on_done:
        on_done()


def main() -> int:
    """Entry point for shell use."""
    def ffmpeg(in_file: str, outfile: str, vstats_path: str) -> int:
        return sp.Popen([
            'ffmpeg', '-nostats', '-loglevel', '0', '-y', '-vstats_file',
            vstats_path, '-i', in_file
        ] + sys.argv[2:] + [outfile]).pid

    try:
        prefix, ext = splitext(basename(sys.argv[1]))
    except IndexError:
        print(f'Usage: {sys.argv[0]} IN_FILE [FFMPEG ARGS]', file=sys.stderr)
        return 1
    fd, outfile = mkstemp(dir='.', prefix=prefix, suffix=ext)
    os.close(fd)
    try:
        start(sys.argv[1], outfile, ffmpeg, on_done=lambda: print(''))
    except (KeyboardInterrupt, ValueError) as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
