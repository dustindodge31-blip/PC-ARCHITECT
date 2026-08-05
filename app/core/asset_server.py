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


class _NoCacheRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Disables HTTP caching so the WebView always re-fetches current assets.

    The ephemeral port picked by ``start()`` can be reused across app
    launches, which let the WebView's disk cache silently serve a stale
    ``case_viewer.html`` (a 304) instead of picking up code changes.
    """

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

    def send_head(self):
        # Strip conditional-request headers so a stale WebView cache can
        # never make us answer with 304 (and thus its stale cached body).
        if "If-Modified-Since" in self.headers:
            del self.headers["If-Modified-Since"]
        if "If-None-Match" in self.headers:
            del self.headers["If-None-Match"]
        return super().send_head()


def start() -> int:
    """Starts the local asset server once (idempotent); returns its port."""
    global _server, _port
    if _server is not None:
        return _port

    handler = functools.partial(_NoCacheRequestHandler, directory=str(ASSETS_DIR))
    _server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    _port = _server.server_address[1]
    threading.Thread(target=_server.serve_forever, daemon=True).start()
    return _port


def url_for(relative_path: str) -> str:
    port = start()
    return f"http://127.0.0.1:{port}/{relative_path.lstrip('/')}"
