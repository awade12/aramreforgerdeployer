from __future__ import annotations

import argparse
from typing import Any, Callable

from ..config import load_config, select_instances
from ..core.terminal import heading, note
from ..server.status import friendly_status

Action = Callable[[argparse.Namespace], None]


def server_hub(args: argparse.Namespace, dispatch: dict[str, Action]) -> None:
    """A small, focused control room for one server."""
    selected = args.instance or args.instance_name
    while True:
        config_path, config = load_config(args.config)
        instance = select_instances(config, selected)[0]
        heading(str(instance.get("server", {}).get("name", selected)), friendly_status(config_path, config, instance))
        print("\n  1. Start     2. Stop      3. Logs      4. Update")
        print("  5. Mods      6. Backup    7. Health    8. Details")
        print("  9. Resources 10. Invite    11. Edit settings")
        print("  0. Back\n")
        choice = input("What do you want to do? ").strip().lower()
        if choice in {"0", "back", "quit", "exit"}:
            return
        if choice == "1":
            _run(dispatch, args, selected, "start")
        elif choice == "2":
            _run(dispatch, args, selected, "stop")
        elif choice == "3":
            _run(dispatch, args, selected, "logs")
        elif choice == "4":
            _run(dispatch, args, selected, "update")
        elif choice == "5":
            _mods(args, config, instance)
        elif choice == "6":
            _run(dispatch, args, selected, "backup")
        elif choice == "7":
            _run(dispatch, args, selected, "check")
        elif choice == "8":
            _run(dispatch, args, selected, "info")
        elif choice == "9":
            _run(dispatch, args, selected, "resources")
        elif choice == "10":
            _run(dispatch, args, selected, "invite")
        elif choice == "11":
            _run(dispatch, args, selected, "edit")
        else:
            note("Choose one of the numbers shown.")


def _run(dispatch: dict[str, Action], original: argparse.Namespace, instance: str, command: str) -> None:
    args = argparse.Namespace(**vars(original))
    args.command = command
    args.instance = instance
    args.instance_name = instance
    args.yes = False
    args.wait = 2.0
    args.lines = 80
    args.follow = False
    args.systemd = False
    args.restart = True
    args.start_stopped = False
    args.include_downloads = False
    args.no_backup = False
    args.watch = 0
    args.fix = False
    args.dry_run = True
    if command == "backup":
        args.action = "create"
    try:
        dispatch[command](args)
    except SystemExit as exc:
        # A failed health/install action should return the person to their hub,
        # not throw them out of the interactive experience.
        if isinstance(exc.code, str):
            print(exc.code)
        elif exc.code not in {None, 0}:
            note("That action needs attention. Choose Health or Details for the next step.")


def _mods(args: argparse.Namespace, config: dict[str, Any], instance: dict[str, Any]) -> None:
    mods = instance.get("mods", [])
    print(f"\nMods: {len(mods)} configured")
    for index, mod in enumerate(mods, start=1):
        print(f"  {index}. {mod.get('name') or mod.get('modId')}")
    print("\nUse: reforger " + str(instance["name"]) + " mod add <workshop-url>")
