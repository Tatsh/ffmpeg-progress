# ffmpeg-progress

[![Python versions](https://img.shields.io/pypi/pyversions/ffmpeg-progress.svg?color=blue&logo=python&logoColor=white)](https://www.python.org/)
[![PyPI - Version](https://img.shields.io/pypi/v/ffmpeg-progress)](https://pypi.org/project/ffmpeg-progress/)
[![GitHub tag (with filter)](https://img.shields.io/github/v/tag/Tatsh/ffmpeg-progress)](https://github.com/Tatsh/ffmpeg-progress/tags)
[![License](https://img.shields.io/github/license/Tatsh/ffmpeg-progress)](https://github.com/Tatsh/ffmpeg-progress/blob/master/LICENSE.txt)
[![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/Tatsh/ffmpeg-progress/v0.0.6/master)](https://github.com/Tatsh/ffmpeg-progress/compare/v0.0.6...master)
[![CodeQL](https://github.com/Tatsh/ffmpeg-progress/actions/workflows/codeql.yml/badge.svg)](https://github.com/Tatsh/ffmpeg-progress/actions/workflows/codeql.yml)
[![QA](https://github.com/Tatsh/ffmpeg-progress/actions/workflows/qa.yml/badge.svg)](https://github.com/Tatsh/ffmpeg-progress/actions/workflows/qa.yml)
[![Tests](https://github.com/Tatsh/ffmpeg-progress/actions/workflows/tests.yml/badge.svg)](https://github.com/Tatsh/ffmpeg-progress/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/Tatsh/ffmpeg-progress/badge.svg?branch=master)](https://coveralls.io/github/Tatsh/ffmpeg-progress?branch=master)
[![Documentation Status](https://readthedocs.org/projects/ffmpeg-progress/badge/?version=latest)](https://ffmpeg-progress.readthedocs.org/?badge=latest)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pydocstyle](https://img.shields.io/badge/pydocstyle-enabled-AD4CD3)](http://www.pydocstyle.org/en/stable/)
[![pytest](https://img.shields.io/badge/pytest-zz?logo=Pytest&labelColor=black&color=black)](https://docs.pytest.org/en/stable/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Downloads](https://static.pepy.tech/badge/ffmpeg-progress/month)](https://pepy.tech/project/ffmpeg-progress)
[![Stargazers](https://img.shields.io/github/stars/Tatsh/ffmpeg-progress?logo=github&style=flat)](https://github.com/Tatsh/ffmpeg-progress/stargazers)

[![@Tatsh](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpublic.api.bsky.app%2Fxrpc%2Fapp.bsky.actor.getProfile%2F%3Factor%3Ddid%3Aplc%3Auq42idtvuccnmtl57nsucz72%26query%3D%24.followersCount%26style%3Dsocial%26logo%3Dbluesky%26label%3DFollow%2520%40Tatsh&query=%24.followersCount&style=social&logo=bluesky&label=Follow%20%40Tatsh)](https://bsky.app/profile/Tatsh.bsky.social)
[![Mastodon Follow](https://img.shields.io/mastodon/follow/109370961877277568?domain=hostux.social&style=social)](https://hostux.social/@Tatsh)

## Deprecated

I am no longer maintaining this project. Please seek alternatives:

- [ffmpeg-progress-yield](https://github.com/slhck/ffmpeg-progress-yield)
- [better-ffmpeg-progress](https://github.com/CrypticSignal/better-ffmpeg-progress)

## Overview

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
