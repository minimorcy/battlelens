"""Captura del área cliente de la ventana objetivo."""

from __future__ import annotations

import mss
import numpy as np

from . import windows


class CaptureError(RuntimeError):
    pass


class WindowUnavailable(CaptureError):
    def __init__(self) -> None:
        super().__init__("La ventana del emulador ya no está disponible. Selecciónala de nuevo.")


class WindowMinimized(CaptureError):
    def __init__(self) -> None:
        super().__init__("La ventana del emulador está minimizada.")


def capture_client(hwnd: int) -> np.ndarray:
    """Devuelve el área cliente como array RGB (alto, ancho, 3)."""
    if not windows.is_window(hwnd):
        raise WindowUnavailable()
    if windows.is_minimized(hwnd):
        raise WindowMinimized()
    left, top, width, height = windows.client_rect_on_screen(hwnd)
    if width <= 0 or height <= 0:
        raise WindowMinimized()
    # mss no es seguro entre hilos: una instancia por captura.
    with mss.MSS() as sct:
        shot = sct.grab({"left": left, "top": top, "width": width, "height": height})
    return np.asarray(shot)[:, :, 2::-1].copy()  # BGRA → RGB
