from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ffmpeg_progress.exceptions import FFMPEGProgressError
from ffmpeg_progress.main import main
import pytest

if TYPE_CHECKING:
    from click.testing import CliRunner
    from pytest_mock import MockType, MockerFixture


@pytest.fixture
def mock_start(mocker: MockerFixture) -> MockType:
    return mocker.patch('ffmpeg_progress.main.start')


@pytest.fixture
def mock_subprocess_popen(mocker: MockerFixture) -> MockType:
    return mocker.patch('subprocess.Popen')


@pytest.fixture
def mock_temporary_file(mocker: MockerFixture) -> MockType:
    mock_tempfile = mocker.patch('tempfile.TemporaryFile')
    mock_tempfile.return_value.__enter__.return_value.name = '/mocked/tempfile'
    return mock_tempfile


def test_main_success(mocker: MockerFixture, mock_start: MockType, mock_subprocess_popen: MockType,
                      mock_temporary_file: MockType, runner: CliRunner) -> None:
    mocker.patch('ffmpeg_progress.main.click.Path.convert', return_value=Path('test.mp4'))
    mock_start.side_effect = lambda _in_file, _outfile, _ffmpeg, on_done: on_done('Done')
    mock_subprocess_popen.return_value.pid = 1234
    result = runner.invoke(main, ['test.mp4'])
    assert result.exit_code == 0
    mock_start.assert_called_once()


def test_main_ffmpeg_progress_error(mocker: MockerFixture, mock_start: MockType,
                                    mock_subprocess_popen: MockType, mock_temporary_file: MockType,
                                    runner: CliRunner) -> None:
    mocker.patch('ffmpeg_progress.main.click.Path.convert', return_value=Path('test.mp4'))
    mock_start.side_effect = FFMPEGProgressError('Mocked error')
    result = runner.invoke(main, ['test.mp4'])
    assert result.exit_code != 0
    assert 'Mocked error' in result.output
    mock_start.assert_called_once()
    mock_subprocess_popen.assert_not_called()


def test_main_invalid_file(mocker: MockerFixture, mock_start: MockType,
                           mock_subprocess_popen: MockType, mock_temporary_file: MockType,
                           runner: CliRunner) -> None:
    result = runner.invoke(main, ['nonexistent.mp4'])
    assert result.exit_code != 0
    assert "Invalid value for 'FILE'" in result.output
    mock_start.assert_not_called()
    mock_subprocess_popen.assert_not_called()
