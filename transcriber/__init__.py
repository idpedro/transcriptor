"""Transcriber — transcrição local de vídeos usando faster-whisper."""

import ctypes as _ctypes
import os as _os

# Pré-carrega as libs NVIDIA instaladas via pip para que o CTranslate2 as encontre.
try:
    import nvidia.cublas.lib
    import nvidia.cudnn.lib

    for _dir in [nvidia.cublas.lib.__path__[0], nvidia.cudnn.lib.__path__[0]]:
        for _lib in sorted(_os.listdir(_dir)):
            if _lib.endswith(".so") or ".so." in _lib:
                try:
                    _ctypes.CDLL(_os.path.join(_dir, _lib), mode=_ctypes.RTLD_GLOBAL)
                except OSError:
                    pass
except ImportError:
    pass

__version__ = "0.1.0"
