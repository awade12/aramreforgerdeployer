from __future__ import annotations

from pathlib import Path
from typing import Any

from ..config.instances import instance_dir_path, select_instances
from ..core.paths import base_dir, generated_dir, install_dir, profile_dir
from ..core.terminal import heading, kv, section


def show_where(config_path: Path, config: dict[str, Any], instance_name: str | None = None) -> None:
    """Print every important resolved location so there is no path guessing."""
    heading("Where Reforger is working", "Resolved paths currently in use")
    section("Shared locations")
    kv(
        [
            ("Config", config_path),
            ("Project folder", config_path.parent),
            ("Instance configs", instance_dir_path(config_path, config)),
            ("Deployments", base_dir(config_path, config)),
            ("Backups", base_dir(config_path, config) / "backups"),
        ]
    )
    for instance in select_instances(config, instance_name):
        section(f"Server: {instance['name']}")
        kv(
            [
                ("Instance config", instance_dir_path(config_path, config) / f"{instance['name']}.json"),
                ("Install", install_dir(config_path, config, instance)),
                ("Logs / profile", profile_dir(config_path, instance)),
                ("Generated files", generated_dir(config_path, config, instance)),
            ]
        )
    section("Quick edit commands")
    print("  reforger edit                     open the main deployer.json in Micro")
    for instance in select_instances(config, instance_name):
        print(f"  reforger {instance['name']} edit   open this server's JSON in Micro")
    print("  Micro is offered for installation if it is not installed yet.")
