from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import EXPERIMENTAL_APP_ID, STABLE_APP_ID
from .paths import norm_path
from .ports import assign_missing_ports


def load_config(path: str) -> tuple[Path, dict[str, Any]]:
    cfg_path = norm_path(path)
    if not cfg_path.exists():
        raise SystemExit(f"Config file not found: {cfg_path}. Run `ardr.py init` first.")
    with cfg_path.open("r", encoding="utf-8") as fh:
        config = json.load(fh)
    config["instances"] = _load_instance_files(cfg_path, config)
    return cfg_path, config


def load_root_config(path: str) -> tuple[Path, dict[str, Any]]:
    cfg_path = norm_path(path)
    if not cfg_path.exists():
        raise SystemExit(f"Config file not found: {cfg_path}. Run `ardr.py init` first.")
    with cfg_path.open("r", encoding="utf-8") as fh:
        return cfg_path, json.load(fh)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def save_config(config_path: Path, config: dict[str, Any]) -> None:
    root = {key: value for key, value in config.items() if key != "instances"}
    root["instanceDir"] = str(config.get("instanceDir", "instances"))
    write_json(config_path, root)
    write_instance_files(config_path, config)


def write_instance_files(config_path: Path, config: dict[str, Any]) -> None:
    instance_dir = _instance_dir(config_path, config)
    instance_dir.mkdir(parents=True, exist_ok=True)
    for instance in config.get("instances", []):
        write_json(instance_dir / f"{instance['name']}.json", instance)


def instance_app_id(instance: dict[str, Any]) -> str:
    branch = str(instance.get("branch", "stable")).lower()
    if branch == "stable":
        return STABLE_APP_ID
    if branch in {"experimental", "exp"}:
        return EXPERIMENTAL_APP_ID
    if branch.isdigit():
        return branch
    raise SystemExit(f"Unsupported branch/app id for instance {instance.get('name')}: {branch}")


def select_instances(config: dict[str, Any], name: str | None) -> list[dict[str, Any]]:
    instances = config.get("instances", [])
    if not isinstance(instances, list) or not instances:
        raise SystemExit("No instances configured.")
    if not name:
        return instances
    selected = [item for item in instances if item.get("name") == name]
    if not selected:
        raise SystemExit(f"Unknown instance: {name}")
    return selected


def sample_config() -> dict[str, Any]:
    return {
        "baseDir": "./deployments",
        "steamcmd": "steamcmd",
        "instanceDir": "instances",
        "instances": [
            _sample_instance("reforger-1", 2001, 17777),
            _sample_instance("reforger-2", 2003, 17779),
        ],
    }


def _sample_instance(name: str, port: int, query_port: int) -> dict[str, Any]:
    return {
        "name": name,
        "branch": "stable",
        "port": port,
        "queryPort": query_port,
        "maxFPS": 60,
        "profileDir": f"./profiles/{name}",
        "server": {
            "name": f"My Reforger Server {name.rsplit('-', 1)[-1]}",
            "password": "",
            "adminPassword": "change-this-admin-password",
            "scenarioId": "{ECC61978EDCC2B5A}Missions/23_Campaign.conf",
            "maxPlayers": 64,
            "visible": True,
            "gameHostRegisterBindAddress": "",
            "gameHostRegisterPort": 0,
            "publicAddress": "",
        },
        "mods": [],
    }


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen_names: set[str] = set()
    seen_ports: dict[int, str] = {}
    for instance in config.get("instances", []):
        name = instance.get("name")
        if not name:
            errors.append("Every instance needs a name.")
            continue
        if name in seen_names:
            errors.append(f"Duplicate instance name: {name}")
        seen_names.add(name)
        _validate_ports(instance, str(name), seen_ports, errors)
        _validate_max_fps(instance, str(name), errors)
        try:
            instance_app_id(instance)
        except SystemExit as exc:
            errors.append(str(exc))
    return errors


def normalize_config_ports(config: dict[str, Any]) -> bool:
    return assign_missing_ports(config)


def _load_instance_files(config_path: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    inline = config.get("instances", [])
    instances = list(inline) if isinstance(inline, list) else []
    instance_dir = _instance_dir(config_path, config)
    if not instance_dir.exists():
        return instances
    for path in sorted(instance_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as fh:
            instance = json.load(fh)
        instance.setdefault("name", path.stem)
        instances = [item for item in instances if item.get("name") != instance.get("name")]
        instances.append(instance)
    return instances


def _instance_dir(config_path: Path, config: dict[str, Any]) -> Path:
    raw = Path(str(config.get("instanceDir", "instances")))
    return raw if raw.is_absolute() else config_path.parent / raw


def _validate_ports(instance: dict[str, Any], name: str, seen: dict[int, str], errors: list[str]) -> None:
    for field in ("port", "queryPort"):
        try:
            port = int(instance[field])
        except (KeyError, TypeError, ValueError):
            errors.append(f"{name} needs numeric {field}.")
            continue
        if not 1 <= port <= 65535:
            errors.append(f"{name} {field} is outside 1-65535: {port}")
        if port in seen:
            errors.append(f"Port collision: {name} {field}={port} already used by {seen[port]}")
        seen[port] = f"{name}.{field}"


def _validate_max_fps(instance: dict[str, Any], name: str, errors: list[str]) -> None:
    try:
        if int(instance.get("maxFPS", 60)) < 1:
            errors.append(f"{name} maxFPS must be positive.")
    except ValueError:
        errors.append(f"{name} maxFPS must be numeric.")
