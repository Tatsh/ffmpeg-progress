"""Constants."""
import os

__all__ = ('LINESEP_BYTES', 'PERCENT_100')

LINESEP_BYTES = os.linesep.encode('utf-8')
"""Line separator in bytes."""
PERCENT_100 = 100.0
"""100% constant float."""
