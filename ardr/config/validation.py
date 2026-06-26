from __future__ import annotations

from typing import Any

from ..core.ports import assign_missing_ports
from .instances import instance_app_id


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
