"""Captura del área cliente de la ventana objetivo.

Primero se usa PrintWindow con PW_RENDERFULLCONTENT, que obtiene el contenido de la ventana
aunque esté tapada por otras (también en emuladores que dibujan con Vulkan/OpenGL a través de DWM).
Si falla o devuelve una imagen negra, se recurre a copiar esa zona de la pantalla con mss.
"""

from __future__ import annotations

import ctypes
import logging
from ctypes import wintypes

import mss
import numpy as np

from . import windows

log = logging.getLogger(__name__)

_PW_CLIENTONLY = 0x1
_PW_RENDERFULLCONTENT = 0x2
_BLACK_THRESHOLD = 8  # valor máximo de píxel por debajo del cual la captura se considera vacía


class CaptureError(RuntimeError):
    pass


class WindowUnavailable(CaptureError):
    def __init__(self) -> None:
        super().__init__("La ventana del emulador ya no está disponible. Selecciónala de nuevo.")


class WindowMinimized(CaptureError):
    def __init__(self) -> None:
        super().__init__("La ventana del emulador está minimizada.")


class _BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", ctypes.c_long),
        ("biHeight", ctypes.c_long),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


_user32 = ctypes.WinDLL("user32", use_last_error=True)
_gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
_user32.GetDC.argtypes = [wintypes.HWND]
_user32.GetDC.restype = wintypes.HDC
_user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
_user32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
_gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
_gdi32.CreateCompatibleDC.restype = wintypes.HDC
_gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
_gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
_gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
_gdi32.SelectObject.restype = wintypes.HGDIOBJ
_gdi32.GetDIBits.argtypes = [
    wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT, ctypes.c_void_p,
    ctypes.POINTER(_BITMAPINFOHEADER), wintypes.UINT,
]
_gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
_gdi32.DeleteDC.argtypes = [wintypes.HDC]


def _print_window(hwnd: int, width: int, height: int) -> np.ndarray | None:
    """Contenido del área cliente vía PrintWindow; None si la llamada falla."""
    hdc = _user32.GetDC(hwnd)
    if not hdc:
        return None
    mem_dc = _gdi32.CreateCompatibleDC(hdc)
    bitmap = _gdi32.CreateCompatibleBitmap(hdc, width, height)
    previous = _gdi32.SelectObject(mem_dc, bitmap)
    try:
        if not _user32.PrintWindow(hwnd, mem_dc, _PW_CLIENTONLY | _PW_RENDERFULLCONTENT):
            return None
        header = _BITMAPINFOHEADER(ctypes.sizeof(_BITMAPINFOHEADER), width, -height, 1, 32, 0, 0, 0, 0, 0, 0)
        buffer = (ctypes.c_ubyte * (width * height * 4))()
        if not _gdi32.GetDIBits(mem_dc, bitmap, 0, height, buffer, ctypes.byref(header), 0):
            return None
        bgra = np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)
        return bgra[:, :, 2::-1].copy()  # BGRA → RGB
    finally:
        _gdi32.SelectObject(mem_dc, previous)
        _gdi32.DeleteObject(bitmap)
        _gdi32.DeleteDC(mem_dc)
        _user32.ReleaseDC(hwnd, hdc)


def _screen_copy(left: int, top: int, width: int, height: int) -> np.ndarray:
    # mss no es seguro entre hilos: una instancia por captura.
    with mss.MSS() as sct:
        shot = sct.grab({"left": left, "top": top, "width": width, "height": height})
    return np.asarray(shot)[:, :, 2::-1].copy()  # BGRA → RGB


def capture_client(hwnd: int) -> np.ndarray:
    """Devuelve el área cliente como array RGB (alto, ancho, 3)."""
    if not windows.is_window(hwnd):
        raise WindowUnavailable()
    if windows.is_minimized(hwnd):
        raise WindowMinimized()
    left, top, width, height = windows.client_rect_on_screen(hwnd)
    if width <= 0 or height <= 0:
        raise WindowMinimized()

    image = _print_window(hwnd, width, height)
    if image is not None and image.max() > _BLACK_THRESHOLD:
        return image
    log.debug("PrintWindow no devolvió contenido; se copia la zona de la pantalla")
    return _screen_copy(left, top, width, height)
