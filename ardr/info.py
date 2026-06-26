from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .paths import generated_dir, install_dir, pid_file, profile_dir
from .platforming import quote
from .processes import process_running, read_pid
from .render import server_config_path, start_command
from .services import service_name, systemd_state
from .terminal import commands, heading, kv, note, section, status_label


def show_info(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> None:
    name = instance["name"]
    server = instance.get("server", {})
    pid = read_pid(config_path, config, instance)
    running = process_running(pid)
    svc = service_name(instance)
    public_name = server.get("name", name)
    host = server.get("publicAddress") or "<VPS_PUBLIC_IP>"
    state = systemd_state(instance)
    runtime = "running" if running or state == "active" else "stopped"
    runtime_detail = f"pid {pid}" if pid else f"systemd {state}" if state else "no pid"

    heading(f"{name}", str(public_name))
    kv(
        [
            ("Status", f"{status_label(runtime)} ({runtime_detail})"),
            ("Branch", instance.get("branch", "stable")),
            ("Players", server.get("maxPlayers", 64)),
            ("Service", f"{svc}" + (f" ({state})" if state else "")),
            ("Scenario", server.get("scenarioId", "")),
        ]
    )

    section("Connect")
    kv(
        [
            ("Direct/IP", f"{host}:{instance['port']}"),
            ("Game UDP", instance["port"]),
            ("Query UDP", instance["queryPort"]),
        ]
    )

    section("Files")
    kv(
        [
            ("Instance", _instance_file(config_path, config, name)),
            ("Server config", server_config_path(config_path, config, instance)),
            ("Start script", generated_dir(config_path, config, instance) / ("start-" + name + ".sh")),
            ("Install dir", install_dir(config_path, config, instance)),
            ("Profile/logs", profile_dir(config_path, instance)),
            ("PID file", pid_file(config_path, config, instance)),
        ]
    )

    section("Next Commands")
    commands(
        [
            (f"reforger status {name}", "show runtime state"),
            (f"reforger tail {name}", "follow logs"),
            (f"reforger restart {name}", "restart server"),
            (f"reforger ports {name}", "show firewall ports"),
            (f"reforger mods list {name}", "list configured mods"),
            (f"reforger backup create {name}", "create a backup"),
        ]
    )

    section("Launch Command")
    print("  " + " ".join(quote(part) for part in start_command(config_path, config, instance)))
    if not shutil.which("systemctl"):
        print()
        note("systemctl was not found here; service commands are for Linux/systemd hosts.")


def _instance_file(config_path: Path, config: dict[str, Any], name: str) -> Path:
    raw = Path(str(config.get("instanceDir", "instances")))
    instance_dir = raw if raw.is_absolute() else config_path.parent / raw
    return instance_dir / f"{name}.json"
