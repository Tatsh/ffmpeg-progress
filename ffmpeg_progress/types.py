__all__ = ('OnMessageCallback', 'ProbeStreamDict', 'ProbeFormatDict', 'ProbeDict')

from collections.abc import Callable, Sequence
from typing import TypedDict

OnMessageCallback = Callable[[float, int, int, float], None]


class ProbeStreamDict(TypedDict):
    """Used only to get the average frame rate string."""
    avg_frame_rate: str


class ProbeFormatDict(TypedDict):
    """Used only to get the duration."""
    duration: float


class ProbeDict(TypedDict, total=False):
    """Minimal representation of what ffprobe returns in its JSON output."""
    format: ProbeFormatDict
    streams: Sequence[ProbeStreamDict]
