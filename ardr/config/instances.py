from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..core.constants import EXPERIMENTAL_APP_ID, STABLE_APP_ID
from .json_io import write_json


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
        raise SystemExit(unknown_instance_message(config, name))
    return selected


def resolve_instance_name(config: dict[str, Any], name: str | None, command: str) -> str:
    instances = config.get("instances", [])
    if not isinstance(instances, list) or not instances:
        raise SystemExit("No instances configured. Run `reforger configure` to add one.")
    if name:
        select_instances(config, name)
        return name
    default = str(config.get("defaultInstance", "")).strip()
    if default:
        select_instances(config, default)
        return default
    if len(instances) == 1:
        return str(instances[0]["name"])
    names = "\n".join(f"  {index}. {instance['name']}" for index, instance in enumerate(instances, start=1))
    raise SystemExit(
        f"No instance selected for `{command}`.\n\n"
        f"Configured servers:\n{names}\n\n"
        f"Run:\n"
        f"  reforger {command} {instances[0]['name']}\n\n"
        f"Or set a default:\n"
        f"  reforger default {instances[0]['name']}"
    )


def write_instance_files(config_path: Path, config: dict[str, Any]) -> None:
    instance_dir = instance_dir_path(config_path, config)
    instance_dir.mkdir(parents=True, exist_ok=True)
    for instance in config.get("instances", []):
        write_json(instance_dir / f"{instance['name']}.json", instance)


def load_instance_files(config_path: Path, config: dict[str, Any]) -> list[dict[str, Any]]:
    inline = config.get("instances", [])
    instances = list(inline) if isinstance(inline, list) else []
    instance_dir = instance_dir_path(config_path, config)
    if not instance_dir.exists():
        return instances
    for path in sorted(instance_dir.glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as fh:
                instance = json.load(fh)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Instance file is not valid JSON: {path}\n{exc}") from exc
        instance.setdefault("name", path.stem)
        instances = [item for item in instances if item.get("name") != instance.get("name")]
        instances.append(instance)
    return instances


def instance_dir_path(config_path: Path, config: dict[str, Any]) -> Path:
    raw = Path(str(config.get("instanceDir", "instances")))
    return raw if raw.is_absolute() else config_path.parent / raw


def unknown_instance_message(config: dict[str, Any], name: str) -> str:
    instances = config.get("instances", [])
    if not isinstance(instances, list) or not instances:
        return f"Unknown instance: {name}"
    choices = "\n".join(f"  - {instance['name']}" for instance in instances)
    return f"Unknown instance: {name}\n\nConfigured servers:\n{choices}"
