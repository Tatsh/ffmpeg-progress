# ffmpeg-progress

[![QA](https://github.com/Tatsh/ffmpeg-progress/actions/workflows/qa.yml/badge.svg)](https://github.com/Tatsh/ffmpeg-progress/actions/workflows/qa.yml)
[![Tests](https://github.com/Tatsh/ffmpeg-progress/actions/workflows/tests.yml/badge.svg)](https://github.com/Tatsh/ffmpeg-progress/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Tatsh/ffmpeg-progress/badge.svg?branch=master)](https://coveralls.io/github/Tatsh/ffmpeg-progress?branch=master)
[![Documentation Status](https://readthedocs.org/projects/ffmpeg-progress/badge/?version=latest)](https://ffmpeg-progress.readthedocs.org/?badge=latest)
[![PyPI - Version](https://img.shields.io/pypi/v/ffmpeg-progress)](https://pypi.org/project/ffmpeg-progress/)
[![GitHub tag (with filter)](https://img.shields.io/github/v/tag/Tatsh/ffmpeg-progress)](https://github.com/Tatsh/ffmpeg-progress/tags)
[![License](https://img.shields.io/github/license/Tatsh/ffmpeg-progress)](https://github.com/Tatsh/ffmpeg-progress/blob/master/LICENSE.txt)
[![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/Tatsh/ffmpeg-progress/v0.0.5/master)](https://github.com/Tatsh/ffmpeg-progress/compare/v0.0.5...master)

Get progress information for an ffmpeg process.

This script is based on the work of [Rupert Plumridge](https://gist.github.com/pruperting/397509/1068d4ced44ded986d0f52ddb4253cfee40921a7).

## Installation

### Poetry

```shell
poetry add ffmpeg-progress
```

### Pip

```shell
pip install ffmpeg-progress
```

## Usage

```plain
Usage: ffmpeg-progress [OPTIONS] FILE

  Entry point for shell use.

Options:
  -h, --help  Show this message and exit.
```

All unknown arguments passed to `ffmpeg-progress` are passed on to `ffmpeg`.

## Library usage

```python
import subprocess as sp
import sys

from ffmpeg_progress import start


def ffmpeg_callback(in_file: str, outfile: str, vstats_path: str):
    return sp.Popen(['ffmpeg',
                     '-nostats',
                     '-loglevel', '0',
                     '-y',
                     '-vstats_file', vstats_path,
                     '-i', in_file,
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

`start()` is the main function to use. If `on_message` is not passed, a default function is used.
The `on_done` argument is optional. The `initial_wait_time` keyword argument can be used to specify
a time to wait before processing the log.

The ffmpeg callback _must_ return a PID (`int`). It is recommended to pass `-nostats -loglevel 0`
to your ffmpeg process. The ffmpeg callback also must pass `-vstats_file` given the path from the
callback argument.

## ffprobe

An ffprobe front-end function is included. Usage:

```python
from ffmpeg_progress import ffprobe


ffprobe('my file.mp4')  # returns a dict()
```
