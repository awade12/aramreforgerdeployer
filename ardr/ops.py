from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .config import select_instances
from .paths import install_dir, profile_dir
from .platforming import executable_name, is_windows, run_checked
from .processes import process_running, read_pid, start_instance, stop_instance
from .render import render_instances, steamcmd_command
from .terminal import commands, heading, section, table


def install_instances(config_path: Path, config: dict[str, Any], instance_name: str | None) -> None:
    render_instances(config_path, config, instance_name)
    for instance in select_instances(config, instance_name):
        run_checked(steamcmd_command(config_path, config, instance))
        exe = install_dir(config_path, config, instance) / executable_name()
        if not exe.exists():
            print(f"WARNING: expected server executable was not found at {exe}")
        elif not is_windows():
            exe.chmod(exe.stat().st_mode | 0o111)


def update_instances(config_path: Path, config: dict[str, Any], instance_name: str | None, restart: bool, start_stopped: bool) -> None:
    targets = select_instances(config, instance_name)
    running = {i["name"] for i in targets if process_running(read_pid(config_path, config, i))}
    if restart:
        for instance in targets:
            if instance["name"] in running:
                stop_instance(config_path, config, instance)
    install_instances(config_path, config, instance_name)
    if restart:
        for instance in targets:
            if instance["name"] in running or start_stopped:
                start_instance(config_path, config, instance)


def restart_instance(config_path: Path, config: dict[str, Any], instance: dict[str, Any], wait: float) -> None:
    stop_instance(config_path, config, instance, quiet=True)
    time.sleep(wait)
    render_instances(config_path, config, instance["name"])
    start_instance(config_path, config, instance)


def show_ports(config: dict[str, Any], instance_name: str | None) -> None:
    targets = select_instances(config, instance_name)
    heading("Ports", "Open these UDP ports locally and in your VPS provider firewall.")
    table(
        ["Server", "Game UDP", "Query UDP"],
        [[instance["name"], int(instance["port"]), int(instance["queryPort"])] for instance in targets],
    )
    section("Linux ufw")
    for instance in targets:
        commands(
            [
                (f"sudo ufw allow {int(instance['port'])}/udp", f"{instance['name']} game"),
                (f"sudo ufw allow {int(instance['queryPort'])}/udp", f"{instance['name']} query"),
            ]
        )
    section("Windows PowerShell")
    for instance in targets:
        ports = f"{int(instance['port'])},{int(instance['queryPort'])}"
        commands(
            [
                (
                    f'New-NetFirewallRule -DisplayName "Reforger {instance["name"]}" -Direction Inbound -Protocol UDP -LocalPort {ports} -Action Allow',
                    "allow both UDP ports",
                )
            ]
        )


def show_logs(config_path: Path, config: dict[str, Any], instance: dict[str, Any], lines: int, follow: bool, systemd: bool) -> None:
    if systemd:
        cmd = ["journalctl", "-u", f"ardr-{instance['name']}.service", "-n", str(lines)]
        run_checked(cmd + (["-f"] if follow else []))
        return
    profile = profile_dir(config_path, instance)
    heading("Logs", str(profile))
    logs = sorted(profile.rglob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True) if profile.exists() else []
    if not logs:
        print("  No .log files found yet. If using systemd, try `reforger tail --systemd`.")
        return
    cmd = ["tail", "-n", str(lines)]
    run_checked(cmd + (["-f"] if follow else []) + [str(logs[0])])
