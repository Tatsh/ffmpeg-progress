from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from tempfile import mkstemp
from time import sleep
from typing import TYPE_CHECKING, cast
import json
import os
import re
import subprocess as sp

import psutil

from .constants import LINESEP_BYTES, PERCENT_100
from .exceptions import (
    InvalidFPS,
    InvalidPID,
    NoDuration,
    ProbeFailed,
    TotalFramesLTEZero,
    UnexpectedZeroFPS,
)
from .utils import default_on_message

if TYPE_CHECKING:
    from .types import OnMessageCallback, ProbeDict

__all__ = ('ffprobe', 'start')


def ffprobe(in_file: Path | str) -> ProbeDict:
    """Ffprobe front-end.

    Parameters
    ----------
    in_file : str
        Input file.

    Returns
    -------
    ProbeDict
        Dictionary.
    """
    return cast(
        'ProbeDict',
        json.loads(
            sp.check_output(
                ('ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams',
                 str(in_file)),
                encoding='utf-8')))


def display(total_frames: int,
            vstats_fd: int,
            pid: int,
            on_message: OnMessageCallback | None = None,
            wait_time: float = 1.0) -> None:
    """
    Generate messages for display of progress.

    Call ``on_message`` argument when one is available.

    Parameters
    ----------
    total_frames : int
        Total frames processed.

    vstats_fd : int
        Video statistics file descriptor.

    pid : int
        ffmpeg PID.

    on_message : OnMessageCallback | None
        The on-message callback.

    wait_time : float
        Wait time between messages. Seconds.
    """
    start_time = datetime.now(tz=timezone.utc)
    fr_cnt = 0
    elapsed = percent = 0.0
    len_linesep = len(LINESEP_BYTES)
    if not on_message:  # pragma: no cover
        on_message = default_on_message
    while fr_cnt < total_frames and percent < PERCENT_100:
        sleep(wait_time)
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            break
        if psutil.Process(pid).status() == psutil.STATUS_ZOMBIE:
            break
        try:
            pos_end = os.lseek(vstats_fd, -2, os.SEEK_END)
        except OSError:  # pragma: no cover
            continue  # Not enough data in file
        pos_start = None
        while os.read(vstats_fd, len_linesep) != LINESEP_BYTES:
            pos_start = os.lseek(vstats_fd, -2, os.SEEK_CUR)
        if pos_start is None:
            continue
        last = os.read(vstats_fd, pos_end - pos_start).decode().strip()
        try:
            vstats = int(re.split(r'\s+', last)[5])
        except IndexError:
            vstats = 0
        if vstats > fr_cnt:
            fr_cnt = vstats
            percent = 100 * (fr_cnt / total_frames)
        elapsed = (datetime.now(tz=timezone.utc) - start_time).total_seconds()
        on_message(percent, fr_cnt, total_frames, elapsed)


FFMPEGCallingFunction = Callable[[str | Path, str | Path, str], int]


def start(in_file: str | Path,
          outfile: str | Path,
          ffmpeg_func: FFMPEGCallingFunction,
          on_message: OnMessageCallback | None = None,
          on_done: Callable[[], None] | None = None,
          index: int = 0,
          wait_time: float = 1.0,
          initial_wait_time: float = 2.0) -> None:
    """
    Start the process.

    Pass an input file path, an output file path, and a callable.

    The callable ``(signature: (in_file, outfile, vstats_file) -> Any)`` passed in is expected to
    start the ffmpeg process and pass the given stats path to the process (last argument):

    .. code-block::

       ffmpeg -y -vstats_file ... -i ...

    The on_message argument may be used to override the messaging, which by default writes to
    ``sys.stdout`` with basic information on the progress. It receives 4 arguments: percentage,
    frame count, total_frames, elapsed time in seconds (float).

    If the FPS or the total number of frames cannot be calculated from
    the input file with ffprobe, an ``FFMPEGProgressError`` will be raised.

    The ``wait_time`` (seconds) argument may be used to slow down the number of messages. A higher
    wait time will mean fewer messages. Very small values may not work.

    The ``initial_wait_time`` (seconds) argument may be used to set an initial interval to wait
    before processing the log file.

    Only Linux is supported at this time.

    Parameters
    ----------
    in_file : str | Path
        Input file.

    outfile : str | Path
        Output file.

    ffmpeg_func : FFMPEGCallingFunction
        The function running ffmpeg.

    on_message : OnMessageCallback | None
        The on-message callback.

    on_done : Callable[[], None] | None
        Completion callback.

    index : int
        Stream index.

    wait_time : float
        Wait time between messages. Seconds.

    initial_wait_time : float
        Wait time before processing log file. Seconds.
    """
    in_file = Path(in_file)
    probe = ffprobe(in_file)
    try:
        probe['streams'][index]
    except (IndexError, KeyError) as e:
        raise ProbeFailed from e
    try:
        fps = cast('float', eval(probe['streams'][index]['avg_frame_rate']))  # noqa: S307
    except ZeroDivisionError as e:
        raise InvalidFPS from e
    if fps == 0:
        raise UnexpectedZeroFPS
    try:
        dur = float(probe['format']['duration'])
    except KeyError as e:
        raise NoDuration from e
    total_frames = int(dur * fps)
    if total_frames <= 0:
        raise TotalFramesLTEZero
    vstats_fd, vstats_path = mkstemp(suffix='.vstats', prefix=f'ffprog-{in_file.stem}')
    if not (pid := ffmpeg_func(in_file, outfile, vstats_path)):
        raise InvalidPID
    sleep(initial_wait_time)
    display(total_frames, vstats_fd, pid, wait_time=wait_time, on_message=on_message)
    os.close(vstats_fd)
    if on_done:  # pragma: no cover
        on_done()
