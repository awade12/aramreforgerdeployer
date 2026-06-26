from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..core.paths import norm_path
from .instances import load_instance_files
from .json_io import write_json


def load_config(path: str) -> tuple[Path, dict[str, Any]]:
    cfg_path = norm_path(path)
    if not cfg_path.exists():
        raise SystemExit(f"Config file not found: {cfg_path}. Run `reforger init` first.")
    try:
        with cfg_path.open("r", encoding="utf-8") as fh:
            config = json.load(fh)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Config file is not valid JSON: {cfg_path}\n{exc}") from exc
    config["instances"] = load_instance_files(cfg_path, config)
    return cfg_path, config


def load_root_config(path: str) -> tuple[Path, dict[str, Any]]:
    cfg_path = norm_path(path)
    if not cfg_path.exists():
        raise SystemExit(f"Config file not found: {cfg_path}. Run `reforger init` first.")
    try:
        with cfg_path.open("r", encoding="utf-8") as fh:
            return cfg_path, json.load(fh)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Config file is not valid JSON: {cfg_path}\n{exc}") from exc


def save_config(config_path: Path, config: dict[str, Any]) -> None:
    from .instances import write_instance_files

    root = {key: value for key, value in config.items() if key != "instances"}
    root["instanceDir"] = str(config.get("instanceDir", "instances"))
    write_json(config_path, root)
    write_instance_files(config_path, config)
