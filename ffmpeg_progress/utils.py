import sys

__all__ = ('default_on_message',)


def default_on_message(percent: float, fr_cnt: int, total_frames: int, elapsed: float) -> None:
    """Default callback for ``display()``.

    Parameters
    ----------
    percent : float
        Percentage completed.

    fr_cnt : int
        Frame count.

    total_frames : int
        Total frame count.

    elapsed : float
        Elapsed time in seconds.
    """
    bar_ = list('|' + (20 * ' ') + '|')
    to_fill = int(round((fr_cnt / total_frames) * 20)) or 1
    for x in range(1, to_fill):
        bar_[x] = '░'
    bar_[to_fill] = '░'
    s_bar = ''.join(bar_)
    sys.stdout.write(f'\r{s_bar}  {percent:5.1f}%   {fr_cnt:d} / {total_frames:d} frames;   '
                     f'elapsed time: {elapsed:.2f} seconds')
    sys.stdout.flush()
