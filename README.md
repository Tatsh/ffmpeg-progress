# ffmpeg-progress

This script is based on the work of [Rupert Plumridge](https://gist.github.com/pruperting/397509/1068d4ced44ded986d0f52ddb4253cfee40921a7).

## Basic use

```python
import subprocess as sp
import sys

from ffmpeg_progress import start


def ffmpeg_callback(infile: str, outfile: str, vstats_path: str):
    return sp.Popen(['ffmpeg',
                     '-nostats',
                     '-loglevel', '0',
                     '-y',
                     '-vstats_file', vstats_path,
                     '-i', infile,
                      outfile]).pid


def on_message_handler(percent: float,
                       fr_cnt: int,
                       total_frames: int,
                       elapsed: float):
    sys.stdout.write('\r{:.2f}%'.format(percent))
    sys.stdout.flush()


start('my input file.mov',
      'some output file.mp4',
      ffmpeg_callback,
      on_message=on_message_handler,
      on_done=lambda: print(''),
      wait_time=1)  # seconds
```

`start()` is the main function to use. If `on_message` is not passed, a default function is used. The `on_done` argument is optional. The `initial_wait_time` keyword argument can be used to specify a time to wait before processing the log.

The ffmpeg callback _must_ return a PID (`int`). It is recommended to pass `-nostats -loglevel 0` to your ffmpeg process. The ffmpeg callback also must pass `-vstats_file` given the path from the callback argument.

## ffprobe

An ffprobe front-end function is included. Usage:

```python
from ffmpeg_progress import ffprobe


ffprobe('my file.mp4')  # returns a dict()
```
