from __future__ import annotations

import copy
import getpass
from pathlib import Path
from typing import Any, Callable

from ..config import normalize_config_ports, save_config, validate_config
from ..config.instances import instance_dir_path
from ..config.wizard import prompt, prompt_bool, prompt_int
from ..core.terminal import heading, note
from .editor import open_in_micro


def edit_server(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> None:
    """A safe, section-by-section editor for normal server administration."""
    while True:
        server = instance.setdefault("server", {})
        heading(f"Edit {instance['name']}", "Choose one area. You will preview changes before they are saved.")
        print("\n  1. Server name and visibility")
        print("  2. Players, passwords, and admins")
        print("  3. Gameplay and performance")
        print("  4. Network and ports")
        print("  5. Mods")
        print("  6. Advanced: open raw JSON in Micro")
        print("  0. Done\n")
        choice = input("What would you like to edit? ").strip().lower()
        if choice in {"0", "done", "back", "quit"}:
            return
        before = copy.deepcopy(instance)
        if choice == "1":
            server["name"] = prompt("Server name", str(server.get("name", instance["name"])))
            server["visible"] = prompt_bool("Show in the public server browser", bool(server.get("visible", True)))
        elif choice == "2":
            _edit_access(server)
        elif choice == "3":
            _edit_gameplay(instance, server)
        elif choice == "4":
            _edit_network(instance, server)
        elif choice == "5":
            _show_mod_help(instance)
            continue
        elif choice == "6":
            open_in_micro(instance_dir_path(config_path, config) / f"{instance['name']}.json")
            return
        else:
            note("Choose one of the numbers shown.")
            continue
        _save_if_confirmed(config_path, config, instance, before)


def _edit_access(server: dict[str, Any]) -> None:
    server["password"] = _secret("Join password", str(server.get("password", "")), allow_clear=True)
    server["adminPassword"] = _secret("Admin password", str(server.get("adminPassword", "")), allow_clear=False)
    server["maxPlayers"] = _bounded_int("Player slots", int(server.get("maxPlayers", 64)), 1, 256)
    current = ", ".join(str(value) for value in server.get("admins", []))
    raw = prompt("Admin IDs, comma-separated (leave blank to keep existing)", current)
    if raw != current:
        server["admins"] = [item.strip() for item in raw.split(",") if item.strip()]


def _edit_gameplay(instance: dict[str, Any], server: dict[str, Any]) -> None:
    server["scenarioId"] = prompt("Scenario ID", str(server.get("scenarioId", "")))
    instance["maxFPS"] = _bounded_int("Maximum server FPS", int(instance.get("maxFPS", 60)), 1, 360)
    disable_third = bool(server.get("disableThirdPerson", False))
    server["disableThirdPerson"] = not prompt_bool("Allow third-person camera", not disable_third)
    server["battlEye"] = prompt_bool("Enable BattlEye", bool(server.get("battlEye", True)))


def _edit_network(instance: dict[str, Any], server: dict[str, Any]) -> None:
    server["publicAddress"] = prompt("Public IP or domain", str(server.get("publicAddress", "")))
    instance["port"] = _bounded_int("Game UDP port", int(instance.get("port", 2001)), 1024, 65535)
    instance["queryPort"] = _bounded_int("Query UDP port", int(instance.get("queryPort", 17777)), 1024, 65535)


def _secret(label: str, current: str, allow_clear: bool) -> str:
    suffix = "Type - to clear it." if allow_clear else "Leave blank to keep the current value."
    value = getpass.getpass(f"{label} (hidden; {suffix}): ")
    if allow_clear and value == "-":
        return ""
    return value or current


def _bounded_int(label: str, default: int, low: int, high: int) -> int:
    while True:
        value = prompt_int(label, default)
        if low <= value <= high:
            return value
        print(f"Choose a number from {low} to {high}.")


def _show_mod_help(instance: dict[str, Any]) -> None:
    mods = instance.get("mods", [])
    print(f"\n{len(mods)} mod(s) configured.")
    for mod in mods:
        print(f"  - {mod.get('name') or mod.get('modId')}")
    print(f"\nAdd a Workshop setup: reforger {instance['name']} mod add <workshop-url>")
    print(f"List configured mods:    reforger {instance['name']} mod list")


def _save_if_confirmed(config_path: Path, config: dict[str, Any], instance: dict[str, Any], before: dict[str, Any]) -> None:
    changes = _changes(before, instance)
    if not changes:
        print("Nothing changed.")
        return
    print("\nChanges to save")
    print("---------------")
    for name, old, new in changes:
        print(f"  {name}: {_display_change(name, old)!r} → {_display_change(name, new)!r}")
    if not prompt_bool("Save these changes", True):
        instance.clear()
        instance.update(before)
        print("Changes discarded.")
        return
    normalize_config_ports(config)
    errors = validate_config(config)
    if errors:
        instance.clear()
        instance.update(before)
        print("Not saved:")
        for error in errors:
            print(f"  {error}")
        return
    save_config(config_path, config)
    print("Saved. Run `reforger " + str(instance["name"]) + " render` before the next start to apply it.")


def _changes(before: Any, after: Any, path: str = "") -> list[tuple[str, Any, Any]]:
    if isinstance(before, dict) and isinstance(after, dict):
        result: list[tuple[str, Any, Any]] = []
        for key in sorted(set(before) | set(after)):
            result.extend(_changes(before.get(key), after.get(key), f"{path}.{key}" if path else str(key)))
        return result
    if isinstance(before, list) and isinstance(after, list):
        result = []
        for index in range(max(len(before), len(after))):
            old = before[index] if index < len(before) else "<not set>"
            new = after[index] if index < len(after) else "<not set>"
            result.extend(_changes(old, new, f"{path}[{index}]"))
        return result
    return [(path, before, after)] if before != after else []


def _display_change(path: str, value: Any) -> Any:
    return "••••••" if path.endswith(("password", "adminPassword")) and value else value
