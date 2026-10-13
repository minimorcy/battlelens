"""Atajos de teclado globales con RegisterHotKey en un hilo con bucle de mensajes propio."""

from __future__ import annotations

import ctypes
import logging
import threading
from ctypes import wintypes
from dataclasses import dataclass

from PyQt6.QtCore import QObject, pyqtSignal

log = logging.getLogger(__name__)

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

_MODIFIERS = {
    "CTRL": MOD_CONTROL,
    "CONTROL": MOD_CONTROL,
    "ALT": MOD_ALT,
    "SHIFT": MOD_SHIFT,
    "MAYUS": MOD_SHIFT,
    "WIN": MOD_WIN,
}
_NAMED_KEYS = {
    "SPACE": 0x20, "ESPACIO": 0x20,
    "PAGEUP": 0x21, "PAGEDOWN": 0x22, "END": 0x23, "HOME": 0x24,
    "LEFT": 0x25, "UP": 0x26, "RIGHT": 0x27, "DOWN": 0x28,
    "INSERT": 0x2D, "DELETE": 0x2E,
}


class HotkeyParseError(ValueError):
    pass


@dataclass(frozen=True)
class Hotkey:
    text: str
    modifiers: int
    vk: int


def parse_hotkey(text: str) -> Hotkey:
    """Convierte "Ctrl+Alt+P" en modificadores y código de tecla virtual."""
    parts = [p.strip().upper() for p in text.split("+") if p.strip()]
    if not parts:
        raise HotkeyParseError("Atajo vacío")
    *mod_parts, key = parts
    modifiers = 0
    for m in mod_parts:
        if m not in _MODIFIERS:
            raise HotkeyParseError(f"Modificador desconocido «{m}» en «{text}»")
        modifiers |= _MODIFIERS[m]

    if len(key) == 1 and ("A" <= key <= "Z" or "0" <= key <= "9"):
        vk = ord(key)
    elif key.startswith("F") and key[1:].isdigit() and 1 <= int(key[1:]) <= 24:
        vk = 0x70 + int(key[1:]) - 1
    elif key in _NAMED_KEYS:
        vk = _NAMED_KEYS[key]
    else:
        raise HotkeyParseError(f"Tecla desconocida «{key}» en «{text}»")

    if not modifiers:
        raise HotkeyParseError(
            f"«{text}» necesita al menos un modificador (Ctrl, Alt, Shift o Win); "
            "las teclas solas, como las F, las usa el emulador."
        )
    return Hotkey(text, modifiers, vk)


_user32 = ctypes.WinDLL("user32", use_last_error=True)
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
_user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
_user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
_user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]


class HotkeyManager(QObject):
    """Registra los atajos en un hilo dedicado y emite `triggered(nombre)` al pulsarlos."""

    triggered = pyqtSignal(str)

    def __init__(self, bindings: dict[str, Hotkey]) -> None:
        super().__init__()
        self._bindings = list(bindings.items())
        self._thread: threading.Thread | None = None
        self._thread_id = 0
        self._ready = threading.Event()
        self.failed: list[str] = []

    def start(self) -> list[str]:
        """Arranca el hilo y devuelve los nombres de los atajos que no se pudieron registrar."""
        self._thread = threading.Thread(target=self._run, name="hotkeys", daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5)
        return list(self.failed)

    def stop(self) -> None:
        if self._thread and self._thread.is_alive():
            _user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
            self._thread.join(timeout=2)

    def _run(self) -> None:
        self._thread_id = _kernel32.GetCurrentThreadId()
        registered: dict[int, str] = {}
        for idx, (name, hk) in enumerate(self._bindings, start=1):
            if _user32.RegisterHotKey(None, idx, hk.modifiers | MOD_NOREPEAT, hk.vk):
                registered[idx] = name
            else:
                log.warning("No se pudo registrar %s (%s): error %s", name, hk.text, ctypes.get_last_error())
                self.failed.append(name)
        self._ready.set()

        msg = wintypes.MSG()
        try:
            while _user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                if msg.message == WM_HOTKEY and msg.wParam in registered:
                    self.triggered.emit(registered[msg.wParam])
        finally:
            for idx in registered:
                _user32.UnregisterHotKey(None, idx)
