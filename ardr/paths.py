from __future__ import annotations

from pathlib import Path
from typing import Any


def norm_path(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def base_dir(config_path: Path, config: dict[str, Any]) -> Path:
    raw = Path(str(config.get("baseDir", "./deployments")))
    return raw if raw.is_absolute() else (config_path.parent / raw).resolve()


def profile_dir(config_path: Path, instance: dict[str, Any]) -> Path:
    raw = Path(str(instance.get("profileDir", f"./profiles/{instance['name']}")))
    return raw if raw.is_absolute() else (config_path.parent / raw).resolve()


def install_dir(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> Path:
    custom = instance.get("installDir")
    if custom:
        raw = Path(str(custom))
        return raw if raw.is_absolute() else (config_path.parent / raw).resolve()
    return base_dir(config_path, config) / instance["name"] / "server"


def generated_dir(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> Path:
    return base_dir(config_path, config) / instance["name"] / "generated"


def pid_file(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> Path:
    return generated_dir(config_path, config, instance) / "server.pid"

