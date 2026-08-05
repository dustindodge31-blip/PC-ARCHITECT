"""Serves app/assets over local HTTP so the embedded 3D viewer (case_viewer.html)
can use fetch()/XHR to load the glTF model -- file:// URLs block those via CORS
in Chromium-based WebViews, regardless of platform."""
import functools
import http.server
import socketserver
import threading
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

_server: socketserver.TCPServer | None = None
_port: int | None = None


def start() -> int:
    """Starts the local asset server once (idempotent); returns its port."""
    global _server, _port
    if _server is not None:
        return _port

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ASSETS_DIR))
    _server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    _port = _server.server_address[1]
    threading.Thread(target=_server.serve_forever, daemon=True).start()
    return _port


def url_for(relative_path: str) -> str:
    port = start()
    return f"http://127.0.0.1:{port}/{relative_path.lstrip('/')}"
