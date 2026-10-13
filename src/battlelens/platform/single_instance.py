"""Impide ejecutar dos instancias a la vez mediante un mutex con nombre de Win32."""

from __future__ import annotations

import ctypes
from ctypes import wintypes

from .. import APP_NAME

_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
_kernel32.CreateMutexW.restype = wintypes.HANDLE
_kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
_ERROR_ALREADY_EXISTS = 183


class SingleInstance:
    def __init__(self, name: str = APP_NAME) -> None:
        self._handle = _kernel32.CreateMutexW(None, False, name)
        self.already_running = ctypes.get_last_error() == _ERROR_ALREADY_EXISTS

    def release(self) -> None:
        if self._handle:
            _kernel32.CloseHandle(self._handle)
            self._handle = None
