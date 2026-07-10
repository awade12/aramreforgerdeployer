from __future__ import annotations

import argparse
import copy
from typing import Any

from ..core.paths import norm_path
from .instances import resolve_instance_name, select_instances
from .io import load_config, save_config
from .sample import sample_config
from .validation import normalize_config_ports, validate_config
from .wizard import build_instance, prompt, prompt_bool, prompt_int


def cmd_init(args: argparse.Namespace) -> None:
    path = norm_path(args.config)
    instance_dir = path.parent / "instances"
    if (path.exists() or instance_dir.exists()) and not args.force:
        raise SystemExit(f"{path} already exists. Use --force to overwrite.")
    config = sample_config()
    normalize_config_ports(config)
    save_config(path, config)
    print(f"Created {path} and {instance_dir}/*.json")


def cmd_configure(args: argparse.Namespace) -> None:
    path = norm_path(args.config)
    config = load_config(args.config)[1] if path.exists() else {"baseDir": "./deployments", "steamcmd": "steamcmd", "instanceDir": "instances", "instances": []}
    before = copy.deepcopy(config)
    config["baseDir"] = prompt("Base deploy directory", str(config.get("baseDir", "./deployments")))
    config["steamcmd"] = prompt("SteamCMD command/path", str(config.get("steamcmd", "steamcmd")))
    config.setdefault("instances", [])
    _upsert_instance(config, _arg_instance(args))
    _preview_changes(before, config)
    if not prompt_bool("Save these changes", True):
        print("No changes were saved.")
        return
    normalize_config_ports(config)
    save_config(path, config)
    _print_validation(config)
    print(f"Saved {path}")


def cmd_setup(args: argparse.Namespace) -> None:
    """A deliberately small first-run wizard; configure remains the full editor."""
    path = norm_path(args.config)
    if path.exists():
        _, config = load_config(args.config)
        if config.get("instances"):
            print("You already have a server configured. Opening the full editor so you can add or change one.")
            cmd_configure(args)
            return
    else:
        config = {"baseDir": "./deployments", "steamcmd": "steamcmd", "instanceDir": "instances", "instances": []}

    print("\nLet's make your first Reforger server. You can change anything later with `reforger configure`.\n")
    public_name = prompt("What should players see as the server name", "My Reforger Server")
    admin_password = prompt("Choose an admin password")
    while not admin_password:
        print("An admin password keeps your server under your control.")
        admin_password = prompt("Choose an admin password")
    join_password = prompt("Join password (leave blank to make it public)")
    max_players = prompt_int("How many player slots", 64)
    while not 1 <= max_players <= 256:
        print("Choose a number from 1 to 256.")
        max_players = prompt_int("How many player slots", 64)
    public_address = prompt("Public IP or domain (leave blank to auto-detect)")
    experimental = prompt_bool("Use the experimental server branch", False)
    name = _next_instance_name(config)
    instance = {
        "name": name,
        "branch": "experimental" if experimental else "stable",
        "maxFPS": 60,
        "profileDir": f"./profiles/{name}",
        "server": {
            "name": public_name,
            "password": join_password,
            "adminPassword": admin_password,
            "scenarioId": "{ECC61978EDCC2B5A}Missions/23_Campaign.conf",
            "maxPlayers": max_players,
            "visible": True,
            "gameHostRegisterBindAddress": "",
            "gameHostRegisterPort": 0,
            "publicAddress": public_address,
        },
        "mods": [],
    }
    config["instances"].append(instance)
    config["defaultInstance"] = name
    normalize_config_ports(config)
    save_config(path, config)
    print(f"\nSaved your server as {name} in {path}.")
    print("\nNext, run:")
    print(f"  reforger launch {name}          # see exactly what will happen")
    print(f"  sudo reforger launch {name} --apply  # install it and start it")
    print("\nUse `reforger info` any time for a plain-English status and next step.")


def cmd_default(args: argparse.Namespace) -> None:
    path, config = load_config(args.config)
    name = _arg_instance(args)
    if not name:
        current = str(config.get("defaultInstance", "")).strip()
        if current:
            print(f"Default server: {current}")
            return
        resolved = resolve_instance_name(config, None, "default")
        print(f"Default server: {resolved}")
        return
    select_instances(config, name)
    config["defaultInstance"] = name
    save_config(path, config)
    print(f"Default server set to {name}")


def cmd_validate(args: argparse.Namespace) -> None:
    _, config = load_config(args.config)
    if normalize_config_ports(config):
        print("WARNING: config has missing or colliding ports. Run `reforger ports --fix` to save safe ports.")
    _print_validation(config)
    print("Config is valid.")


def _upsert_instance(config: dict[str, Any], instance_name: str | None) -> None:
    if instance_name:
        for index, instance in enumerate(config["instances"]):
            if instance.get("name") == instance_name:
                config["instances"][index] = build_instance(config, instance)
                return
    config["instances"].append(build_instance(config))


def _print_validation(config: dict) -> None:
    normalize_config_ports(config)
    errors = validate_config(config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)


def _arg_instance(args: argparse.Namespace) -> str | None:
    return getattr(args, "instance", None) or getattr(args, "instance_name", None)


def _next_instance_name(config: dict[str, Any]) -> str:
    used = {str(item.get("name", "")) for item in config.get("instances", [])}
    index = 1
    while f"reforger-{index}" in used:
        index += 1
    return f"reforger-{index}"


def _preview_changes(before: dict[str, Any], after: dict[str, Any]) -> None:
    changes = _changes(before, after)
    print("\nConfig preview")
    print("--------------")
    if not changes:
        print("  No changes.")
        return
    for path, old, new in changes:
        print(f"  {path}: {old!r} → {new!r}")


def _changes(before: Any, after: Any, path: str = "") -> list[tuple[str, Any, Any]]:
    if isinstance(before, dict) and isinstance(after, dict):
        result: list[tuple[str, Any, Any]] = []
        for key in sorted(set(before) | set(after)):
            next_path = f"{path}.{key}" if path else str(key)
            result.extend(_changes(before.get(key), after.get(key), next_path))
        return result
    if isinstance(before, list) and isinstance(after, list):
        result = []
        for index in range(max(len(before), len(after))):
            old = before[index] if index < len(before) else "<not set>"
            new = after[index] if index < len(after) else "<not set>"
            result.extend(_changes(old, new, f"{path}[{index}]"))
        return result
    if before != after:
        return [(path, before, after)]
    return []
