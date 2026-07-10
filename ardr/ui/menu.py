from __future__ import annotations

import argparse
from typing import Any, Callable

from ..config import load_config, select_instances
from ..core.terminal import heading, note, section

Action = Callable[[argparse.Namespace], None]
MenuItem = tuple[str, str, bool]


def choose_instance(config: dict[str, Any]) -> str:
    instances = select_instances(config, None)
    print("\nYour servers:")
    for index, instance in enumerate(instances, start=1):
        print(f"  {index}. {instance['name']}")
    while True:
        raw = input("Choose a server number: ").strip()
        try:
            return str(instances[int(raw) - 1]["name"])
        except (ValueError, IndexError):
            print("Please enter one of the numbers shown above.")


def interactive_loop(args: argparse.Namespace, dispatch: dict[str, Action]) -> None:
    try:
        _, config = load_config(args.config)
    except FileNotFoundError:
        print("\nNo server is set up yet. Let's fix that first.")
        dispatch["setup"](args)
        try:
            _, config = load_config(args.config)
        except FileNotFoundError:
            return

    selected_name = _default_instance(config)
    show_more = False
    while True:
        _print_menu(selected_name, show_more)
        selected = _selected_action(_actions(show_more), input("Choose a number: ").strip().lower())
        if not selected:
            print("Please choose one of the numbers shown.")
            continue
        command, _, needs_instance = selected
        if command == "quit":
            print("See you next time.")
            return
        if command == "more":
            show_more = not show_more
            continue
        if command == "switch":
            selected_name = choose_instance(config)
            continue
        next_args = argparse.Namespace(**vars(args))
        next_args.command = command
        next_args.instance = selected_name if needs_instance else None
        _fill_defaults(next_args)
        if command == "tail":
            next_args.follow = True
        if command == "firewall":
            next_args.action = "apply"
            next_args.dry_run = True
        if command == "backup":
            next_args.action = "create"
        if command == "deploy":
            next_args.apply = False
        dispatch[command](next_args)
        _, config = load_config(args.config)
        selected_name = selected_name if any(i.get("name") == selected_name for i in config["instances"]) else _default_instance(config)


def _actions(show_more: bool) -> list[MenuItem]:
    if show_more:
        return [
            ("update", "Update server files", True),
            ("render", "Regenerate config and launch files", True),
            ("backup", "Create a backup", True),
            ("query", "Query live server status", True),
            ("ports", "Show ports and firewall help", True),
            ("doctor", "Run host diagnostics", False),
            ("firewall", "Preview firewall changes", False),
            ("configure", "Edit every server setting", False),
            ("more", "Back to everyday controls", False),
            ("quit", "Quit", False),
        ]
    return [
        ("status", "See all server status", False),
        ("start", "Start selected server", True),
        ("stop", "Stop selected server", True),
        ("restart", "Restart selected server", True),
        ("tail", "Watch live logs", True),
        ("info", "Show connection info and next step", True),
        ("check", "Check if everything is ready", False),
        ("switch", "Switch selected server", False),
        ("more", "More tools", False),
        ("quit", "Quit", False),
    ]


def _print_menu(selected_name: str, show_more: bool) -> None:
    heading("Reforger Manager", f"Selected server: {selected_name}")
    if not show_more:
        note("Everyday controls — use More tools only when you need them.")
    print()
    for index, (_, label, _) in enumerate(_actions(show_more), start=1):
        print(f"  {index}. {label}")


def _selected_action(actions: list[MenuItem], choice: str) -> MenuItem | None:
    if choice.isdigit():
        index = int(choice) - 1
        return actions[index] if 0 <= index < len(actions) else None
    return next((item for item in actions if item[0] == choice), None)


def _default_instance(config: dict[str, Any]) -> str:
    default = str(config.get("defaultInstance", "")).strip()
    if default and any(instance.get("name") == default for instance in config.get("instances", [])):
        return default
    return str(select_instances(config, None)[0]["name"])


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
