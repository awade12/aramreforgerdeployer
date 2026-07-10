from __future__ import annotations

import argparse
from pathlib import Path

from ..config import load_config, select_instances
from ..core.terminal import commands, heading, note, section, table
from ..server.status import status_row


def show_home(args: argparse.Namespace) -> None:
    """Show a calm, useful starting point when no command was supplied."""
    config_path = Path(args.config)
    if not config_path.exists():
        heading("Reforger Server Manager", "A simpler way to run your Arma Reforger server.")
        print()
        note("No server is set up here yet. That is okay — setup asks only the important questions.")
        section("Start here")
        commands(
            [
                ("reforger setup", "create your first server in a few friendly prompts"),
                ("reforger --help", "see every command when you are ready for more control"),
            ]
        )
        return

    config_path, config = load_config(args.config)
    instances = select_instances(config, None)
    heading("Reforger Server Manager", f"{len(instances)} configured server{'s' if len(instances) != 1 else ''}")
    rows = [list(status_row(config_path, config, instance)[:3]) for instance in instances]
    table(["Server", "State", "Details"], rows)
    default = str(config.get("defaultInstance", "")).strip()
    print()
    section("Most common things")
    commands(
        [
            ("reforger start", "start your default server"),
            ("reforger stop", "stop it safely"),
            ("reforger info", "see connection details and the best next step"),
            ("reforger menu", "open the guided interactive manager"),
        ]
    )
    if not default:
        print()
        note(f"Tip: choose a default once with `reforger default {instances[0]['name']}` so daily commands stay short.")

