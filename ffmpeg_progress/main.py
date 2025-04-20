from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryFile
import subprocess as sp

import click

from .exceptions import FFMPEGProgressError
from .lib import start

__all__ = ('main',)


@click.command(name='ffmpeg-progress',
               context_settings={
                   'allow_extra_args': True,
                   'help_option_names': ('-h', '--help'),
                   'ignore_unknown_options': True
               })
@click.argument('file',
                type=click.Path(exists=True, dir_okay=False, resolve_path=True, path_type=Path),
                required=True)
@click.pass_context
def main(context: click.Context, file: Path) -> None:
    """Entry point for shell use."""
    def ffmpeg(in_file: str | Path, outfile: str | Path,
               vstats_path: str) -> int:  # pragma: no cover
        return sp.Popen(('ffmpeg', '-nostats', '-loglevel', '0', '-y', '-vstats_file', vstats_path,
                         '-i', in_file, *context.args[2:], outfile)).pid

    with TemporaryFile('wb', prefix=file.stem, suffix=file.suffix) as tf:
        outfile = tf.name
    try:
        start(file, outfile, ffmpeg, on_done=print)
    except FFMPEGProgressError as e:
        click.echo(str(e), err=True)
        raise click.Abort from e
