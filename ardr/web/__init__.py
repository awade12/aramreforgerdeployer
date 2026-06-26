from __future__ import annotations

from http.server import ThreadingHTTPServer
from pathlib import Path

from .auth import ensure_auth
from .handler import build_handler
from .state import WebState


def serve_web(config: str, host: str, port: int, password: str | None, auth_file: str) -> None:
    auth_path = Path(auth_file)
    generated = ensure_auth(auth_path, password)
    if generated:
        print(f"Generated dashboard password: {generated}")
    if host not in {"127.0.0.1", "localhost", "::1"}:
        print("WARNING: dashboard is exposed. Use a strong password and put HTTPS/reverse proxy in front of it.")
    state = WebState(config, auth_path)
    server = ThreadingHTTPServer((host, port), build_handler(state))
    print(f"Reforger dashboard listening on http://{host}:{port}")
    server.serve_forever()
