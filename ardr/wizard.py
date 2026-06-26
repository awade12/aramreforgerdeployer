from __future__ import annotations

from typing import Any

from .ports import next_port_pair


def prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{text}{suffix}: ").strip()
    return value if value else default


def prompt_bool(text: str, default: bool = True) -> bool:
    marker = "Y/n" if default else "y/N"
    value = input(f"{text} [{marker}]: ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes", "true", "1", "on"}


def prompt_int(text: str, default: int) -> int:
    while True:
        value = prompt(text, str(default))
        try:
            return int(value)
        except ValueError:
            print("Enter a number.")


def next_default_ports(config: dict[str, Any]) -> tuple[int, int]:
    return next_port_pair(config)


def build_instance(config: dict[str, Any], existing: dict[str, Any] | None = None) -> dict[str, Any]:
    existing = existing or {}
    server = dict(existing.get("server", {}))
    default_port, default_query = next_default_ports(config)
    name = prompt("Instance name", str(existing.get("name", f"reforger-{len(config.get('instances', [])) + 1}")))
    return {
        "name": name,
        "branch": prompt("Branch: stable or experimental", str(existing.get("branch", "stable"))),
        "port": prompt_int("Game UDP port", int(existing.get("port", default_port))),
        "queryPort": prompt_int("Query/A2S UDP port", int(existing.get("queryPort", default_query))),
        "maxFPS": prompt_int("Max FPS", int(existing.get("maxFPS", 60))),
        "profileDir": str(existing.get("profileDir", f"./profiles/{name}")),
        "server": _server_block(name, server),
        "mods": existing.get("mods", []),
    }


def _server_block(name: str, server: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": prompt("Public server name", str(server.get("name", name))),
        "password": prompt("Join password, blank for public", str(server.get("password", ""))),
        "adminPassword": prompt("Admin password", str(server.get("adminPassword", "change-this-admin-password"))),
        "scenarioId": prompt("Scenario ID", str(server.get("scenarioId", "{ECC61978EDCC2B5A}Missions/23_Campaign.conf"))),
        "maxPlayers": prompt_int("Max players", int(server.get("maxPlayers", 64))),
        "visible": prompt_bool("Show in public browser", bool(server.get("visible", True))),
        "crossplay": prompt_bool("Allow crossplay clients", bool(server.get("crossplay", True))),
        "gameHostRegisterBindAddress": str(server.get("gameHostRegisterBindAddress", "")),
        "gameHostRegisterPort": int(server.get("gameHostRegisterPort", 0)),
        "publicAddress": str(server.get("publicAddress", "")),
    }
