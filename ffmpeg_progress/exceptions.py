"""Exceptions."""
__all__ = ('FFMPEGProgressError', 'InvalidFPS', 'InvalidPID', 'NoDuration', 'ProbeFailed',
           'TotalFramesLTEZero', 'UnexpectedZeroFPS')


class FFMPEGProgressError(Exception):
    """General error."""


class ProbeFailed(FFMPEGProgressError):
    """Raised when ffprobe fails."""
    def __init__(self) -> None:
        super().__init__('Probe failed.')


class InvalidFPS(FFMPEGProgressError):
    """Raised when the FPS string is invalid."""
    def __init__(self) -> None:
        super().__init__('Cannot use input FPS.')


class UnexpectedZeroFPS(FFMPEGProgressError):
    """Raised when the FPS is calculated to be zero."""
    def __init__(self) -> None:
        super().__init__('Unexpected zero FPS.')


class NoDuration(FFMPEGProgressError):
    """Raised when duration cannot be determined."""
    def __init__(self) -> None:
        super().__init__('Unable to determine duration.')


class TotalFramesLTEZero(FFMPEGProgressError):
    """Raised when total frames is calculated to be less than or equal to zero."""
    def __init__(self) -> None:
        super().__init__('Total frames is less than or equal to zero.')


class InvalidPID(FFMPEGProgressError):
    """Raised when the ffmpeg callback does not return a valid PID."""
    def __init__(self) -> None:
        super().__init__('ffmpeg callback must return a valid PID.')
