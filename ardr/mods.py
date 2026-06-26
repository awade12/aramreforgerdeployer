from __future__ import annotations

from typing import Any

from .config import save_config, select_instances
from .terminal import heading, table


def add_mod(config_path, config: dict[str, Any], instance_name: str, mod_id: str, name: str, version: str) -> None:
    instance = select_instances(config, instance_name)[0]
    mods = instance.setdefault("mods", [])
    existing = next((mod for mod in mods if mod.get("modId") == mod_id), None)
    payload = {"modId": mod_id, "name": name or mod_id, "version": version}
    if existing:
        existing.update(payload)
        print(f"Updated mod {mod_id} on {instance_name}")
    else:
        mods.append(payload)
        print(f"Added mod {mod_id} to {instance_name}")
    save_config(config_path, config)


def list_mods(config: dict[str, Any], instance_name: str) -> None:
    instance = select_instances(config, instance_name)[0]
    mods = instance.get("mods", [])
    heading(f"Mods: {instance_name}", f"{len(mods)} configured")
    if not mods:
        print("  No mods configured.")
        return
    table(
        ["Mod ID", "Name", "Version"],
        [[mod.get("modId", ""), mod.get("name", ""), mod.get("version", "")] for mod in mods],
    )


def remove_mod(config_path, config: dict[str, Any], instance_name: str, mod_id: str) -> None:
    instance = select_instances(config, instance_name)[0]
    before = len(instance.get("mods", []))
    instance["mods"] = [mod for mod in instance.get("mods", []) if mod.get("modId") != mod_id]
    save_config(config_path, config)
    print("Removed mod." if len(instance["mods"]) < before else "Mod was not configured.")
