from __future__ import annotations

from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from ..config import load_config, normalize_config_ports, save_config, select_instances
from .actions import capture_output, run_action
from .auth import make_csrf, make_session, valid_session, verify_password
from .models import instance_details
from .state import WebState
from .views import dashboard, instance_panel, login


def build_handler(state: WebState):
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
                return self._html(self._panel(query_param(parsed.query, "instance")))
            return self._html(self._dashboard(query_param(parsed.query, "instance")))

        def do_POST(self) -> None:
            if self.path == "/login":
                return self._login()
            if not self._authed() or not self._valid_csrf():
                return self._text("Forbidden", HTTPStatus.FORBIDDEN)
            if self.path == "/action":
                return self._html(self._action())
            if self.path == "/mods/add":
                return self._html(self._add_mod())
            if self.path == "/settings":
                return self._html(self._save_settings())
            return self._text("Not found", HTTPStatus.NOT_FOUND)

        def _dashboard(self, selected: str | None) -> str:
            _, config = _config()
            instances = select_instances(config, None)
            selected = selected or instances[0]["name"]
            csrf = make_csrf()
            state.csrf[self._session()] = csrf
            return dashboard(instances, selected, csrf, self._panel(selected, csrf=csrf))

        def _panel(
            self,
            selected: str | None,
            output: str = "",
            csrf: str | None = None,
            action: str = "",
        ) -> str:
            config_path, config = _config()
            instance = select_instances(config, selected)[0]
            if not csrf:
                csrf = state.csrf.get(self._session()) or make_csrf()
                state.csrf[self._session()] = csrf
            details = instance_details(config_path, config, instance)
            return instance_panel(instance, details, csrf, output, action)

        def _action(self) -> str:
            form = self._form()
            instance = form.get("instance", [""])[0]
            action = form.get("action", [""])[0]
            output = capture_output(lambda: run_action(action, instance, state))
            return self._panel(instance, output, action=action)

        def _add_mod(self) -> str:
            from ..server.mods import add_mod

            form = self._form()
            instance_name = form.get("instance", [""])[0]
            mod_id = form.get("mod_id", [""])[0]
            mod_name = form.get("mod_name", [""])[0]
            config_path, config = _config()
            output = capture_output(lambda: add_mod(config_path, config, instance_name, mod_id, mod_name, ""))
            return self._panel(instance_name, output, action="add mod")

        def _save_settings(self) -> str:
            form = self._form()
            instance_name = form.get("instance", [""])[0]
            config_path, config = _config()
            try:
                instance = select_instances(config, instance_name)[0]
                server = instance.setdefault("server", {})
                instance["port"] = _valid_port(form.get("port", [""])[0], "Game port")
                instance["queryPort"] = _valid_port(form.get("query_port", [""])[0], "Query port")
                max_players = int(form.get("max_players", [""])[0])
                if not 1 <= max_players <= 256:
                    raise ValueError("Player slots must be between 1 and 256.")
                server["name"] = _required(form.get("server_name", [""])[0], "Server name")
                server["scenarioId"] = _required(form.get("scenario_id", [""])[0], "Scenario ID")
                server["maxPlayers"] = max_players
                server["visible"] = form.get("visible", [""])[0] == "yes"
                password = form.get("password", [""])[0]
                if password:
                    server["password"] = password
                save_config(config_path, config)
                output = "Your server settings were saved. Render the server setup before the next start if it is already installed."
                return self._panel(instance_name, output, action="settings saved")
            except (ValueError, SystemExit) as exc:
                return self._panel(instance_name, f"ERROR: {exc}", action="settings saved")

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

    return Handler


def query_param(query: str, key: str) -> str | None:
    return parse_qs(query).get(key, [None])[0]


def _required(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{label} cannot be empty.")
    return value


def _valid_port(value: str, label: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be a number.") from exc
    if not 1024 <= port <= 65535:
        raise ValueError(f"{label} must be between 1024 and 65535.")
    return port
