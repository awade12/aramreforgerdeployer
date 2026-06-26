from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from ..core.terminal import heading, section, table
from ..platform.firewall import apply_firewall
from ..platform.services import control_service, render_systemd
from ..server.info import show_info
from ..server.ops import install_instances
from ..server.render import render_instances
from .backup import create_backup


def deploy_instance(config_path: Path, config: dict[str, Any], instance: dict[str, Any], apply: bool) -> None:
    name = instance["name"]
    steps: list[tuple[str, Callable[[], None]]] = [
        ("render configs", lambda: render_instances(config_path, config, name)),
        ("backup config/profile", lambda: create_backup(config_path, config, name, False)),
        ("install/update server", lambda: install_instances(config_path, config, name)),
        ("apply local firewall", lambda: apply_firewall(config, name, False)),
        ("install systemd service", lambda: render_systemd(config_path, config, name, True)),
        ("enable service", lambda: control_service(instance, "enable")),
        ("start service", lambda: control_service(instance, "start")),
    ]
    if not apply:
        heading(f"Launch Preview: {name}", "Re-run with --apply to execute these steps.")
        table("Step Action".split(), [[index, label] for index, (label, _) in enumerate(steps, start=1)] + [[len(steps) + 1, f"show info for {name}"]])
        return
    for label, action in steps:
        section(label)
        action()
    section("info")
    show_info(config_path, config, instance)
