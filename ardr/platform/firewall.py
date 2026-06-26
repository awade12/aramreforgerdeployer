from __future__ import annotations

import shutil
from typing import Any

from ..config import select_instances
from ..core.platforming import is_windows, run_checked


def apply_firewall(config: dict[str, Any], instance_name: str | None, dry_run: bool) -> None:
    if is_windows():
        _windows_rules(config, instance_name, dry_run)
        return
    if shutil.which("ufw"):
        _ufw_rules(config, instance_name, dry_run)
    else:
        print("ufw was not found. Install ufw or open these UDP ports with your firewall:")
        for instance in select_instances(config, instance_name):
            print(f"  {instance['name']}: {instance['port']}/udp, {instance['queryPort']}/udp")
    print("Also open these UDP ports in your VPS provider firewall/security group.")


def _ufw_rules(config: dict[str, Any], instance_name: str | None, dry_run: bool) -> None:
    for instance in select_instances(config, instance_name):
        for port in (str(instance["port"]), str(instance["queryPort"])):
            cmd = ["ufw", "allow", f"{port}/udp"]
            _run_or_print(cmd, dry_run)


def _windows_rules(config: dict[str, Any], instance_name: str | None, dry_run: bool) -> None:
    for instance in select_instances(config, instance_name):
        ports = f"{int(instance['port'])},{int(instance['queryPort'])}"
        cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            f'New-NetFirewallRule -DisplayName "Reforger {instance["name"]}" -Direction Inbound -Protocol UDP -LocalPort {ports} -Action Allow',
        ]
        _run_or_print(cmd, dry_run)


def _run_or_print(cmd: list[str], dry_run: bool) -> None:
    if dry_run:
        print("+ " + " ".join(cmd))
    else:
        run_checked(cmd)
