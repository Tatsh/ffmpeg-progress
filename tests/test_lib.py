from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
import os
import subprocess as sp

from ffmpeg_progress.constants import LINESEP_BYTES
from ffmpeg_progress.exceptions import (
    InvalidFPS,
    InvalidPID,
    NoDuration,
    ProbeFailed,
    TotalFramesLTEZero,
    UnexpectedZeroFPS,
)
from ffmpeg_progress.lib import display, ffprobe, start
import psutil
import pytest

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_ffprobe_success(mocker: MockerFixture) -> None:
    mock_check_output = mocker.patch('subprocess.check_output')
    mock_check_output.return_value = '{"streams": [], "format": {}}'

    result = ffprobe('test.mp4')

    mock_check_output.assert_called_once_with(('ffprobe', '-v', 'quiet', '-print_format', 'json',
                                               '-show_format', '-show_streams', 'test.mp4'),
                                              encoding='utf-8')
    assert result == {'streams': [], 'format': {}}


def test_ffprobe_failure(mocker: MockerFixture) -> None:
    mock_check_output = mocker.patch('subprocess.check_output')
    mock_check_output.side_effect = sp.CalledProcessError(1, 'ffprobe')

    with pytest.raises(sp.CalledProcessError):
        ffprobe('test.mp4')


def test_start_invalid_fps(mocker: MockerFixture) -> None:
    mock_ffprobe = mocker.patch('ffmpeg_progress.lib.ffprobe')
    mock_ffprobe.return_value = {
        'streams': [{
            'avg_frame_rate': '1/0'
        }],
        'format': {
            'duration': '10'
        }
    }

    with pytest.raises(InvalidFPS):
        start('input.mp4', 'output.mp4', lambda _x, _y, _z: 123)


def test_start_unexpected_zero_fps(mocker: MockerFixture) -> None:
    mock_ffprobe = mocker.patch('ffmpeg_progress.lib.ffprobe')
    mock_ffprobe.return_value = {
        'streams': [{
            'avg_frame_rate': '0/1'
        }],
        'format': {
            'duration': '10'
        }
    }

    with pytest.raises(UnexpectedZeroFPS):
        start('input.mp4', 'output.mp4', lambda _x, _y, _z: 123)


def test_start_no_duration(mocker: MockerFixture) -> None:
    mock_ffprobe = mocker.patch('ffmpeg_progress.lib.ffprobe')
    mock_ffprobe.return_value = {'streams': [{'avg_frame_rate': '25/1'}], 'format': {}}

    with pytest.raises(NoDuration):
        start('input.mp4', 'output.mp4', lambda _x, _y, _z: 123)


def test_start_total_frames_lte_zero(mocker: MockerFixture) -> None:
    mock_ffprobe = mocker.patch('ffmpeg_progress.lib.ffprobe')
    mock_ffprobe.return_value = {
        'streams': [{
            'avg_frame_rate': '25/1'
        }],
        'format': {
            'duration': '0'
        }
    }

    with pytest.raises(TotalFramesLTEZero):
        start('input.mp4', 'output.mp4', lambda _x, _y, _z: 123)


def test_start_invalid_pid(mocker: MockerFixture) -> None:
    mock_ffprobe = mocker.patch('ffmpeg_progress.lib.ffprobe')
    mock_ffprobe.return_value = {
        'streams': [{
            'avg_frame_rate': '25/1'
        }],
        'format': {
            'duration': '10'
        }
    }
    mock_mkstemp = mocker.patch('tempfile.mkstemp')
    mock_mkstemp.return_value = (123, 'vstats_path')
    mock_ffmpeg_func = mocker.Mock(return_value=0)

    with pytest.raises(InvalidPID):
        start('input.mp4', 'output.mp4', mock_ffmpeg_func)


def test_start_success(mocker: MockerFixture) -> None:
    mock_ffprobe = mocker.patch('ffmpeg_progress.lib.ffprobe')
    mock_ffprobe.return_value = {
        'streams': [{
            'avg_frame_rate': '25/1'
        }],
        'format': {
            'duration': '10'
        }
    }
    mock_mkstemp = mocker.patch('ffmpeg_progress.lib.mkstemp')
    mock_mkstemp.return_value = (123, 'vstats_path')
    mock_ffmpeg_func = mocker.Mock(return_value=456)
    mock_display = mocker.patch('ffmpeg_progress.lib.display')
    mock_os_close = mocker.patch('os.close')
    mock_on_done = mocker.Mock()
    mocker.patch('ffmpeg_progress.lib.sleep')

    start('input.mp4', 'output.mp4', mock_ffmpeg_func, on_done=mock_on_done)

    mock_ffmpeg_func.assert_called_once_with(Path('input.mp4'), 'output.mp4', 'vstats_path')
    mock_display.assert_called_once()
    mock_os_close.assert_called_once_with(123)
    mock_on_done.assert_called_once()


def test_display_success(mocker: MockerFixture) -> None:
    mock_os_kill = mocker.patch('ffmpeg_progress.lib.os.kill')
    mock_psutil_process = mocker.patch('ffmpeg_progress.lib.psutil.Process')
    mock_psutil_process.return_value.status.return_value = psutil.STATUS_RUNNING
    mock_os_lseek = mocker.patch('ffmpeg_progress.lib.os.lseek', side_effect=[-2, -2, 0])
    mock_os_read = mocker.patch(
        'ffmpeg_progress.lib.os.read',
        side_effect=[LINESEP_BYTES, b'frame=  10', LINESEP_BYTES, b'0 0 0 0 0 100'])
    mock_sleep = mocker.patch('ffmpeg_progress.lib.sleep')
    mock_on_message = mocker.Mock()

    display(100, 123, 456, mock_on_message, 0.1)

    mock_os_kill.assert_called_with(456, 0)
    mock_psutil_process.assert_called_with(456)
    mock_os_lseek.assert_any_call(123, -2, os.SEEK_END)
    mock_os_read.assert_any_call(123, 1)
    mock_on_message.assert_called_with(100.0, 100, 100, mocker.ANY)
    mock_sleep.assert_called()


def test_display_process_terminated(mocker: MockerFixture) -> None:
    mock_os_kill = mocker.patch('os.kill', side_effect=ProcessLookupError)
    mock_sleep = mocker.patch('ffmpeg_progress.lib.sleep')
    mock_on_message = mocker.Mock()

    display(100, 123, 456, on_message=mock_on_message, wait_time=0.1)

    mock_os_kill.assert_called_with(456, 0)
    mock_on_message.assert_not_called()
    mock_sleep.assert_called()


def test_display_zombie_process(mocker: MockerFixture) -> None:
    mock_os_kill = mocker.patch('os.kill')
    mock_psutil_process = mocker.patch('psutil.Process')
    mock_psutil_process.return_value.status.return_value = psutil.STATUS_ZOMBIE
    mock_sleep = mocker.patch('ffmpeg_progress.lib.sleep')
    mock_on_message = mocker.Mock()

    display(100, 123, 456, on_message=mock_on_message, wait_time=0.1)

    mock_os_kill.assert_called_with(456, 0)
    mock_psutil_process.assert_called_with(456)
    mock_on_message.assert_not_called()
    mock_sleep.assert_called()


def test_display_invalid_vstats_line(mocker: MockerFixture) -> None:
    mock_os_kill = mocker.patch('os.kill')
    mock_psutil_process = mocker.patch('psutil.Process')
    mock_psutil_process.return_value.status.return_value = psutil.STATUS_RUNNING
    mock_os_lseek = mocker.patch('os.lseek', side_effect=[-2, -2, 0, -2, -2, 0])
    mock_os_read = mocker.patch('os.read',
                                side_effect=[
                                    b'invalid line', LINESEP_BYTES, b'invalid line',
                                    b'0 0 0 0 0 100', LINESEP_BYTES, b'0 0 0 0 0 100'
                                ])
    mock_sleep = mocker.patch('ffmpeg_progress.lib.sleep')
    mock_on_message = mocker.Mock()

    display(100, 123, 456, on_message=mock_on_message, wait_time=0.1)

    mock_os_kill.assert_called_with(456, 0)
    mock_psutil_process.assert_called_with(456)
    mock_os_lseek.assert_any_call(123, -2, os.SEEK_END)
    mock_os_read.assert_any_call(123, 1)
    assert mock_on_message.call_count == 2
    mock_sleep.assert_called()


def test_start_invalid_stream_index(mocker: MockerFixture) -> None:
    mock_ffprobe = mocker.patch('ffmpeg_progress.lib.ffprobe')
    mock_ffprobe.return_value = {
        'streams': [{
            'avg_frame_rate': '25/1'
        }],
        'format': {
            'duration': '10'
        }
    }

    with pytest.raises(ProbeFailed):
        start('input.mp4', 'output.mp4', lambda _x, _y, _z: 123, index=5)
