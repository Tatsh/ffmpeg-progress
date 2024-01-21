"""
This is based on ffmpeg-progress.sh by Rupert Plumridge
https://gist.github.com/pruperting/397509/1068d4ced44ded986d0f52ddb4253cfee40921a7
"""
from .exceptions import FFMPEGProgressError
from .lib import ffprobe, start

__all__ = ('FFMPEGProgressError', 'ffprobe', 'start')
