from __future__ import annotations

import argparse
from typing import Any, Callable

from .config import load_config, select_instances


Action = Callable[[argparse.Namespace], None]


def choose_instance(config: dict[str, Any]) -> str:
    instances = select_instances(config, None)
    print("\nInstances:")
    for index, instance in enumerate(instances, start=1):
        print(f"  {index}. {instance['name']}")
    while True:
        raw = input("Choose instance number: ").strip()
        try:
            selected = instances[int(raw) - 1]
            return str(selected["name"])
        except (ValueError, IndexError):
            print("Choose a listed number.")


def interactive_loop(args: argparse.Namespace, dispatch: dict[str, Action]) -> None:
    _, config = load_config(args.config)
    actions = [
        ("status", "Show status", False, False),
        ("info", "Show instance info", True, False),
        ("query", "Query live server", True, False),
        ("start", "Start server", True, False),
        ("stop", "Stop server", True, False),
        ("restart", "Restart server", True, False),
        ("pause", "Pause server process", True, False),
        ("resume", "Resume paused server", True, False),
        ("update", "Update server files", False, False),
        ("render", "Render configs/scripts", False, False),
        ("ports", "Show firewall ports", False, False),
        ("ports", "Auto-fix and save ports", False, True),
        ("doctor", "Run preflight doctor", False, False),
        ("deploy", "Dry-run first deploy", True, False),
        ("firewall", "Show firewall apply commands", False, False),
        ("backup", "Create backup", False, False),
        ("linuxgsm", "Render LinuxGSM helper", False, False),
        ("configure", "Add/edit config with wizard", False, False),
        ("quit", "Quit", False, False),
    ]
    while True:
        print("\nARDR Manager")
        for index, (_, label, _, _) in enumerate(actions, start=1):
            print(f"  {index}. {label}")
        choice = input("Choose action: ").strip().lower()
        selected = _selected_action(actions, choice)
        if not selected:
            print("Choose a listed action.")
            continue
        command, _, needs_instance, fix_ports = selected
        if command == "quit":
            return
        next_args = argparse.Namespace(**vars(args))
        next_args.command = command
        next_args.instance = choose_instance(config) if needs_instance else None
        _fill_defaults(next_args)
        next_args.fix = fix_ports
        if command == "firewall":
            next_args.action = "apply"
        if command == "backup":
            next_args.action = "create"
        if command == "deploy":
            next_args.apply = False
        dispatch[command](next_args)
        _, config = load_config(args.config)


def _selected_action(actions: list[tuple[str, str, bool, bool]], choice: str) -> tuple[str, str, bool, bool] | None:
    if choice.isdigit():
        index = int(choice) - 1
        return actions[index] if 0 <= index < len(actions) else None
    for item in actions:
        if item[0] == choice:
            return item
    return None


def _fill_defaults(args: argparse.Namespace) -> None:
    args.wait = getattr(args, "wait", 2.0)
    args.restart = getattr(args, "restart", True)
    args.start_stopped = getattr(args, "start_stopped", False)
    args.lines = getattr(args, "lines", 80)
    args.follow = getattr(args, "follow", False)
    args.systemd = getattr(args, "systemd", False)
    args.fix = getattr(args, "fix", False)
    args.dry_run = getattr(args, "dry_run", True)
    args.include_downloads = getattr(args, "include_downloads", False)
    args.archive = getattr(args, "archive", None)
    args.target = getattr(args, "target", ".")
    args.host = getattr(args, "host", None)
    args.timeout = getattr(args, "timeout", 3.0)
    args.apply = getattr(args, "apply", False)
