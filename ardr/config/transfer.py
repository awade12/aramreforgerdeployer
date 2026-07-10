from __future__ import annotations

import copy
import json
from pathlib import Path

from .io import load_config, save_config
from .instances import select_instances
from .validation import normalize_config_ports


def export_instance(config_path: str, instance_name: str, output: str) -> Path:
    _, config = load_config(config_path)
    instance = select_instances(config, instance_name)[0]
    destination = Path(output).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"format": "ardr-instance-v1", "instance": instance}, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {instance_name} to {destination}")
    return destination


def import_instance(config_path: str, source: str, new_name: str | None = None) -> str:
    source_path = Path(source).expanduser().resolve()
    if not source_path.exists():
        raise SystemExit(f"Import file not found: {source_path}")
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        instance = copy.deepcopy(payload["instance"])
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise SystemExit("That is not a valid Reforger server export file.") from exc
    path, config = load_config(config_path)
    if payload.get("format") != "ardr-instance-v1":
        raise SystemExit("That export file has an unsupported format.")
    name = new_name or str(instance.get("name", ""))
    if not name:
        raise SystemExit("The exported server has no name.")
    if any(str(item.get("name")) == name for item in config.get("instances", [])):
        raise SystemExit(f"A server named {name} already exists. Use --as to import under a new name.")
    instance["name"] = name
    config.setdefault("instances", []).append(instance)
    normalize_config_ports(config)
    save_config(path, config)
    print(f"Imported {name}. Review it with `reforger {name}` before starting it.")
    return name
