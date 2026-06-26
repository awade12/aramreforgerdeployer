from __future__ import annotations

import io
import contextlib
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .backup import create_backup
from .config import load_config, normalize_config_ports, save_config, select_instances
from .management_commands import cmd_query
from .render import render_instances
from .services import control_service, systemd_state
from .status import print_status
from .web_auth import ensure_auth, make_csrf, make_session, valid_session, verify_password
from .web_views import dashboard, instance_panel, login


class WebState:
    def __init__(self, config: str, auth_file: Path):
        self.config = config
        self.auth_file = auth_file
        self.csrf: dict[str, str] = {}


def serve_web(config: str, host: str, port: int, password: str | None, auth_file: str) -> None:
    auth_path = Path(auth_file)
    generated = ensure_auth(auth_path, password)
    if generated:
        print(f"Generated dashboard password: {generated}")
    if host not in {"127.0.0.1", "localhost", "::1"}:
        print("WARNING: dashboard is exposed. Use a strong password and put HTTPS/reverse proxy in front of it.")
    server = ThreadingHTTPServer((host, port), _handler(WebState(config, auth_path)))
    print(f"ARDR dashboard listening on http://{host}:{port}")
    server.serve_forever()


def _handler(state: WebState):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path.startswith("/login"):
                return self._html(login())
            if self.path.startswith("/logout"):
                return self._redirect("/login", clear=True)
            if not self._authed():
                return self._redirect("/login")
            parsed = urlparse(self.path)
            if parsed.path == "/panel":
                return self._html(self._panel(_param(parsed.query, "instance")))
            return self._html(self._dashboard(_param(parsed.query, "instance")))

        def do_POST(self) -> None:
            if self.path == "/login":
                return self._login()
            if not self._authed() or not self._valid_csrf():
                return self._text("Forbidden", HTTPStatus.FORBIDDEN)
            if self.path == "/action":
                return self._html(self._action())
            if self.path == "/mods/add":
                return self._html(self._add_mod())
            return self._text("Not found", HTTPStatus.NOT_FOUND)

        def _dashboard(self, selected: str | None) -> str:
            _, config = _config()
            instances = select_instances(config, None)
            selected = selected or instances[0]["name"]
            csrf = make_csrf()
            state.csrf[self._session()] = csrf
            return dashboard(instances, selected, csrf, self._panel(selected, csrf=csrf))

        def _panel(self, selected: str | None, output: str = "", csrf: str | None = None) -> str:
            config_path, config = _config()
            instance = select_instances(config, selected)[0]
            status = _capture(lambda: print_status(config_path, config, instance)).strip()
            if not csrf:
                csrf = state.csrf.get(self._session()) or make_csrf()
                state.csrf[self._session()] = csrf
            return instance_panel(instance, status, systemd_state(instance), csrf, output)

        def _action(self) -> str:
            form = self._form()
            instance = form.get("instance", [""])[0]
            action = form.get("action", [""])[0]
            output = _capture(lambda: _run_action(action, instance))
            return self._panel(instance, output)

        def _add_mod(self) -> str:
            from .mods import add_mod

            form = self._form()
            instance_name = form.get("instance", [""])[0]
            mod_id = form.get("mod_id", [""])[0]
            mod_name = form.get("mod_name", [""])[0]
            config_path, config = _config()
            output = _capture(lambda: add_mod(config_path, config, instance_name, mod_id, mod_name, ""))
            return self._panel(instance_name, output)

        def _login(self) -> None:
            password = self._form().get("password", [""])[0]
            if not verify_password(state.auth_file, password):
                return self._html(login("Invalid password"), HTTPStatus.UNAUTHORIZED)
            session = make_session(state.auth_file)
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/")
            self.send_header("Set-Cookie", f"ardr_session={session}; HttpOnly; SameSite=Lax; Path=/")
            self.end_headers()

        def _authed(self) -> bool:
            return valid_session(state.auth_file, self._session())

        def _valid_csrf(self) -> bool:
            form = self._form()
            return state.csrf.get(self._session()) == form.get("csrf", [""])[0]

        def _session(self) -> str | None:
            cookie = SimpleCookie(self.headers.get("Cookie"))
            morsel = cookie.get("ardr_session")
            return morsel.value if morsel else None

        def _form(self) -> dict[str, list[str]]:
            if hasattr(self, "_cached_form"):
                return self._cached_form
            length = int(self.headers.get("Content-Length", "0"))
            self._cached_form = parse_qs(self.rfile.read(length).decode())
            return self._cached_form

        def _html(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode())

        def _text(self, body: str, status: HTTPStatus) -> None:
            self.send_response(status)
            self.end_headers()
            self.wfile.write(body.encode())

        def _redirect(self, target: str, clear: bool = False) -> None:
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", target)
            if clear:
                self.send_header("Set-Cookie", "ardr_session=; Max-Age=0; Path=/")
            self.end_headers()

    def _config():
        config_path, config = load_config(state.config)
        if normalize_config_ports(config):
            save_config(config_path, config)
        return config_path, config

    def _run_action(action: str, instance_name: str) -> None:
        config_path, config = _config()
        instance = select_instances(config, instance_name)[0]
        if action in {"start", "stop", "restart"}:
            control_service(instance, action)
        elif action == "backup":
            create_backup(config_path, config, instance_name, False)
        elif action == "render":
            render_instances(config_path, config, instance_name)
        elif action == "query":
            args = type("Args", (), {"instance": instance_name, "host": None, "timeout": 2.0})()
            cmd_query(args, lambda *_: (config_path, config, instance))

    return Handler


def _capture(fn) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            fn()
        except BaseException as exc:
            print(f"ERROR: {exc}")
    return buf.getvalue()


def _param(query: str, key: str) -> str | None:
    return parse_qs(query).get(key, [None])[0]
