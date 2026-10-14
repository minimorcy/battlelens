"""Servidor local de la fuente para OBS (add-stream-mode D2).

Solo escucha en 127.0.0.1, solo responde a GET, comprueba la cabecera Host (contra el DNS rebinding
desde páginas web) y solo sirve una lista fija de archivos del paquete.
"""

from __future__ import annotations

import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources

log = logging.getLogger(__name__)

HOST = "127.0.0.1"
DEFAULT_PORT = 17320
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/card.css": ("card.css", "text/css; charset=utf-8"),
    "/card.js": ("card.js", "text/javascript; charset=utf-8"),
}
SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:",
    "Referrer-Policy": "no-referrer",
}


def read_static(name: str) -> bytes:
    return (resources.files("battlelens.stream") / "static" / name).read_bytes()


class StreamState:
    """Lo que muestra la fuente para OBS; seguro entre hilos. `seq` cambia con cada actualización."""

    def __init__(self, mode: str = "normal") -> None:
        self._lock = threading.Lock()
        self._seq = 0
        self._visible = False
        self._cards: list[dict] = []
        self.mode = mode

    def publish(self, cards: list[dict]) -> None:
        with self._lock:
            self._cards = list(cards)
            self._visible = bool(cards)
            self._seq += 1

    def set_visible(self, visible: bool) -> None:
        with self._lock:
            visible = visible and bool(self._cards)
            if visible != self._visible:
                self._visible = visible
                self._seq += 1

    @property
    def visible(self) -> bool:
        with self._lock:
            return self._visible

    def snapshot(self) -> dict:
        with self._lock:
            return {"seq": self._seq, "visible": self._visible, "mode": self.mode, "cards": self._cards}


def _handler(state: StreamState):
    class Handler(BaseHTTPRequestHandler):
        server_version = "BattleLens"
        sys_version = ""

        def log_message(self, format, *args):  # noqa: A002 - sin registro por petición
            pass

        def _send(self, status: int, body: bytes = b"", content_type: str = "text/plain; charset=utf-8") -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            for name, value in SECURITY_HEADERS.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            port = self.server.server_address[1]
            if (self.headers.get("Host") or "").lower() not in {f"localhost:{port}", f"127.0.0.1:{port}"}:
                self._send(403, b"Forbidden")
                return
            path = self.path.split("?", 1)[0]
            if path == "/state":
                body = json.dumps(state.snapshot(), ensure_ascii=False).encode("utf-8")
                self._send(200, body, "application/json; charset=utf-8")
            elif path in STATIC_FILES:
                name, content_type = STATIC_FILES[path]
                self._send(200, read_static(name), content_type)
            else:
                self._send(404, b"Not found")

    return Handler


class StreamServer:
    """Arranca y para el servidor en un hilo aparte."""

    def __init__(self, state: StreamState) -> None:
        self.state = state
        self._httpd: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port: int | None = None

    @property
    def running(self) -> bool:
        return self._httpd is not None

    @property
    def url(self) -> str | None:
        return f"http://localhost:{self.port}/" if self.running else None

    def start(self, port: int = DEFAULT_PORT) -> bool:
        """False si el puerto está ocupado (se registra el motivo)."""
        self.stop()
        try:
            httpd = ThreadingHTTPServer((HOST, port), _handler(self.state))
        except OSError as exc:
            log.warning("No se pudo abrir el puerto %s para el modo stream: %s", port, exc)
            return False
        httpd.daemon_threads = True
        self._httpd, self.port = httpd, httpd.server_address[1]
        self._thread = threading.Thread(target=httpd.serve_forever, name="battlelens-stream", daemon=True)
        self._thread.start()
        log.info("Modo stream: fuente para OBS en %s", self.url)
        return True

    def stop(self) -> None:
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None
            self.port = None
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None
