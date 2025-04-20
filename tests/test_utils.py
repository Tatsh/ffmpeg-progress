from __future__ import annotations

from typing import TYPE_CHECKING
import sys

from ffmpeg_progress.utils import default_on_message

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


def test_default_on_message(mocker: MockerFixture) -> None:
    mock_write = mocker.patch.object(sys.stdout, 'write')
    mock_flush = mocker.patch.object(sys.stdout, 'flush')
    percent = 50.0
    fr_cnt = 500
    total_frames = 1000
    elapsed = 12.34
    default_on_message(percent, fr_cnt, total_frames, elapsed)
    expected_bar = ('|░░░░░░░░░░          |   50.0%   500 / 1000 frames;   elapsed time: 12.34 '
                    'seconds')
    mock_write.assert_called_once_with(f'\r{expected_bar}')
    mock_flush.assert_called_once()
