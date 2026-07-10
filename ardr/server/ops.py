from __future__ import annotations

import time
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ..config import select_instances
from ..core.paths import install_dir, profile_dir
from ..core.platforming import executable_name, is_windows, run_checked, run_follow
from ..core.terminal import bad, commands, good, heading, section, table, warn
from .processes import process_running, read_pid, start_instance, stop_instance
from .render import render_instances, steamcmd_command


def install_instances(config_path: Path, config: dict[str, Any], instance_name: str | None) -> None:
    steamcmd = str(config.get("steamcmd", "steamcmd"))
    if not (shutil.which(steamcmd) or Path(steamcmd).exists()):
        raise SystemExit(
            "SteamCMD is not installed or cannot be found.\n\n"
            "Ubuntu/Debian quick fix:\n"
            "  sudo add-apt-repository multiverse\n"
            "  sudo apt update && sudo apt install steamcmd\n\n"
            "Then run this install command again. If SteamCMD lives elsewhere, set `steamcmd` in deployer.json."
        )
    render_instances(config_path, config, instance_name)
    for instance in select_instances(config, instance_name):
        heading(f"Installing {instance['name']}", "Downloading or updating server files. This can take a few minutes.")
        run_checked(steamcmd_command(config_path, config, instance))
        exe = install_dir(config_path, config, instance) / executable_name()
        if not exe.exists():
            print(f"WARNING: expected server executable was not found at {exe}")
        elif not is_windows():
            exe.chmod(exe.stat().st_mode | 0o111)
            print(f"Ready: server files are installed for {instance['name']}.")


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
    runner = run_follow if follow else run_checked
    if systemd:
        cmd = ["journalctl", "-u", f"ardr-{instance['name']}.service", "-n", str(lines)]
        runner(cmd + (["-f"] if follow else []))
        return
    profile = profile_dir(config_path, instance)
    heading("Logs", str(profile))
    logs = sorted(profile.rglob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True) if profile.exists() else []
    if not logs:
        print("  No .log files found yet. If using systemd, try `reforger tail --systemd`.")
        return
    if follow:
        print("Watching live logs. Press Ctrl+C when you are done.")
        _follow_colored(logs[0], lines)
        return
    print(f"Showing the latest {lines} lines. Red means error; yellow means warning.")
    with logs[0].open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle.readlines()[-lines:]:
            print(_friendly_log_line(line.rstrip()))


def _friendly_log_line(line: str) -> str:
    upper = line.upper()
    if "ERROR" in upper or "FATAL" in upper or "EXCEPTION" in upper:
        return bad(line)
    if "WARN" in upper or "WARNING" in upper:
        return warn(line)
    if "STARTED" in upper or "CONNECTED" in upper:
        return good(line)
    return line


def _follow_colored(path: Path, lines: int) -> None:
    """Keep live logs readable while still calling attention to problems."""
    process = subprocess.Popen(["tail", "-n", str(lines), "-f", str(path)], stdout=subprocess.PIPE, text=True, errors="replace")
    try:
        assert process.stdout is not None
        for line in process.stdout:
            print(_friendly_log_line(line.rstrip()))
    except KeyboardInterrupt:
        pass
    finally:
        process.terminate()
        process.wait(timeout=2)
