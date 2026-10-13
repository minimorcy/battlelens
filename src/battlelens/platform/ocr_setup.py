"""Instalación guiada del paquete de OCR de Windows (Add-WindowsCapability con elevación)."""

from __future__ import annotations

import ctypes
import subprocess
from ctypes import wintypes
from dataclasses import dataclass
from enum import Enum

# Idiomas soportados por la app → etiqueta del paquete de OCR de Windows
SUPPORTED_OCR_TAGS = {"es": "es-ES", "en": "en-US", "fr": "fr-FR", "de": "de-DE", "it": "it-IT"}
FALLBACK_TAG = "en-US"
ERROR_CANCELLED = 1223

MANUAL_INSTRUCTIONS = (
    "Instálalo a mano en Configuración > Hora e idioma > Idioma y región: añade (o abre las opciones de) "
    "tu idioma y marca «Reconocimiento óptico de caracteres»."
)


def ui_language_tag() -> str:
    """Etiqueta BCP-47 del idioma de la interfaz de Windows (p. ej. "es-ES")."""
    kernel32 = ctypes.windll.kernel32
    langid = kernel32.GetUserDefaultUILanguage()
    buf = ctypes.create_unicode_buffer(85)
    if kernel32.LCIDToLocaleName(langid, buf, len(buf), 0):
        return buf.value
    return FALLBACK_TAG


def proposed_ocr_tag(ui_tag: str) -> str:
    primary = ui_tag.split("-")[0].lower()
    return SUPPORTED_OCR_TAGS.get(primary, FALLBACK_TAG)


def capability_name(tag: str) -> str:
    return f"Language.OCR~~~{tag}~0.0.1.0"


def powershell_arguments(tag: str) -> str:
    script = (
        f"try {{ Add-WindowsCapability -Online -Name '{capability_name(tag)}' -ErrorAction Stop | Out-Null; exit 0 }} "
        "catch { exit 1 }"
    )
    return subprocess.list2cmdline(
        ["-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-Command", script]
    )


class InstallOutcome(Enum):
    SUCCESS = "success"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass(frozen=True)
class InstallResult:
    outcome: InstallOutcome
    tag: str
    exit_code: int | None = None


class _SHELLEXECUTEINFOW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("fMask", ctypes.c_ulong),
        ("hwnd", wintypes.HWND),
        ("lpVerb", wintypes.LPCWSTR),
        ("lpFile", wintypes.LPCWSTR),
        ("lpParameters", wintypes.LPCWSTR),
        ("lpDirectory", wintypes.LPCWSTR),
        ("nShow", ctypes.c_int),
        ("hInstApp", wintypes.HINSTANCE),
        ("lpIDList", ctypes.c_void_p),
        ("lpClass", wintypes.LPCWSTR),
        ("hkeyClass", wintypes.HKEY),
        ("dwHotKey", wintypes.DWORD),
        ("hIconOrMonitor", wintypes.HANDLE),
        ("hProcess", wintypes.HANDLE),
    ]


_SEE_MASK_NOCLOSEPROCESS = 0x00000040
_SEE_MASK_NOASYNC = 0x00000100
_SW_HIDE = 0
_INFINITE = 0xFFFFFFFF


def _run_elevated(executable: str, parameters: str) -> tuple[bool, int]:
    """Lanza un proceso con UAC y espera a que termine. Devuelve (lanzado, código o error)."""
    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    shell32.ShellExecuteExW.argtypes = [ctypes.POINTER(_SHELLEXECUTEINFOW)]
    kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

    info = _SHELLEXECUTEINFOW()
    info.cbSize = ctypes.sizeof(info)
    info.fMask = _SEE_MASK_NOCLOSEPROCESS | _SEE_MASK_NOASYNC
    info.lpVerb = "runas"
    info.lpFile = executable
    info.lpParameters = parameters
    info.nShow = _SW_HIDE
    if not shell32.ShellExecuteExW(ctypes.byref(info)):
        return False, ctypes.get_last_error()
    try:
        kernel32.WaitForSingleObject(info.hProcess, _INFINITE)
        code = wintypes.DWORD()
        kernel32.GetExitCodeProcess(info.hProcess, ctypes.byref(code))
        return True, code.value
    finally:
        kernel32.CloseHandle(info.hProcess)


def install_ocr(tag: str) -> InstallResult:
    """Bloquea hasta que termina la instalación: llamar desde un hilo de trabajo."""
    launched, code = _run_elevated("powershell.exe", powershell_arguments(tag))
    if not launched:
        if code == ERROR_CANCELLED:
            return InstallResult(InstallOutcome.CANCELLED, tag)
        return InstallResult(InstallOutcome.FAILED, tag, code)
    if code != 0:
        return InstallResult(InstallOutcome.FAILED, tag, code)
    return InstallResult(InstallOutcome.SUCCESS, tag, 0)
