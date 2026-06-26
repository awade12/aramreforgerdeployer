from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import instance_app_id, select_instances, validate_config, write_json
from .constants import SUPPORTED_CLIENTS_CROSSPLAY, SUPPORTED_CLIENTS_PC_ONLY
from .paths import generated_dir, install_dir, profile_dir
from .platforming import executable_name, is_windows, quote, script_suffix


def render_server_config(instance: dict[str, Any]) -> dict[str, Any]:
    server = dict(instance.get("server", {}))
    port = int(instance.get("port", 2001))
    query_port = int(instance.get("queryPort", port + 15776))
    crossplay = bool(server.get("crossplay", True))
    cfg = {
        "bindAddress": server.get("bindAddress", "0.0.0.0"),
        "bindPort": port,
        "publicAddress": server.get("publicAddress", ""),
        "publicPort": int(server.get("publicPort", port)),
        "a2s": {"address": server.get("queryAddress", "0.0.0.0"), "port": query_port},
        "game": _game_block(instance, server, crossplay),
    }
    for key in ("gameHostBindAddress", "gameHostRegisterBindAddress"):
        if server.get(key):
            cfg[key] = server[key]
    for key in ("gameHostBindPort", "gameHostRegisterPort"):
        if server.get(key):
            cfg[key] = int(server[key])
    return cfg


def _game_block(instance: dict[str, Any], server: dict[str, Any], crossplay: bool) -> dict[str, Any]:
    game = {
        "name": server.get("name", instance["name"]),
        "password": server.get("password", ""),
        "passwordAdmin": server.get("adminPassword", "change-this-admin-password"),
        "scenarioId": server.get("scenarioId", "{ECC61978EDCC2B5A}Missions/23_Campaign.conf"),
        "maxPlayers": int(server.get("maxPlayers", 64)),
        "visible": bool(server.get("visible", True)),
        "supportedGameClientTypes": SUPPORTED_CLIENTS_CROSSPLAY if crossplay else SUPPORTED_CLIENTS_PC_ONLY,
        "gameProperties": {
            "serverMaxViewDistance": int(server.get("serverMaxViewDistance", 2500)),
            "serverMinGrassDistance": int(server.get("serverMinGrassDistance", 50)),
            "networkViewDistance": int(server.get("networkViewDistance", 1000)),
            "disableThirdPerson": bool(server.get("disableThirdPerson", False)),
            "fastValidation": bool(server.get("fastValidation", True)),
            "battlEye": bool(server.get("battlEye", True)),
        },
    }
    if instance.get("mods"):
        game["mods"] = instance["mods"]
    return game


def start_command(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> list[str]:
    return [
        str(install_dir(config_path, config, instance) / executable_name()),
        "-config",
        str(server_config_path(config_path, config, instance)),
        "-profile",
        str(profile_dir(config_path, instance)),
        "-maxFPS",
        str(int(instance.get("maxFPS", 60))),
    ]


def steamcmd_command(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> list[str]:
    return [
        str(config.get("steamcmd", "steamcmd")),
        "+force_install_dir",
        str(install_dir(config_path, config, instance)),
        "+login",
        "anonymous",
        "+app_update",
        instance_app_id(instance),
        "validate",
        "+quit",
    ]


def render_start_script(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> Path:
    out = generated_dir(config_path, config, instance) / f"start-{instance['name']}{script_suffix()}"
    cmd = start_command(config_path, config, instance)
    out.parent.mkdir(parents=True, exist_ok=True)
    if is_windows():
        lines = ["@echo off", "setlocal", f"cd /d {quote(install_dir(config_path, config, instance))}", " ".join(quote(x) for x in cmd), ""]
    else:
        lines = ["#!/usr/bin/env bash", "set -euo pipefail", f"cd {quote(install_dir(config_path, config, instance))}", " ".join(quote(x) for x in cmd), ""]
    out.write_text("\n".join(lines), encoding="utf-8")
    if not is_windows():
        out.chmod(0o755)
    return out


def server_config_path(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> Path:
    return generated_dir(config_path, config, instance) / f"{instance['name']}-server-config.json"


def render_instances(config_path: Path, config: dict[str, Any], instance_name: str | None = None) -> None:
    errors = validate_config(config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    for instance in select_instances(config, instance_name):
        install_dir(config_path, config, instance).mkdir(parents=True, exist_ok=True)
        profile_dir(config_path, instance).mkdir(parents=True, exist_ok=True)
        gen = generated_dir(config_path, config, instance)
        write_json(server_config_path(config_path, config, instance), render_server_config(instance))
        print(f"Rendered {instance['name']}: {server_config_path(config_path, config, instance)}")
        print(f"Rendered start script: {render_start_script(config_path, config, instance)}")
