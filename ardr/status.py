from __future__ import annotations

from pathlib import Path
from typing import Any

from .processes import cleanup_dead_pid, process_running, read_pid
from .services import systemd_state
from .terminal import status_label


def print_status(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> None:
    name, state, detail, systemd = status_row(config_path, config, instance)
    service = f", systemd {systemd}" if systemd else ""
    print(f"{name:<18} {status_label(state):<12} {detail}{service}")


def status_row(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> tuple[str, str, str, str]:
    cleanup_dead_pid(config_path, config, instance)
    pid = read_pid(config_path, config, instance)
    systemd = systemd_state(instance)
    state = "running" if process_running(pid) or systemd == "active" else "stopped"
    detail = f"pid {pid}" if pid else "systemd active" if systemd == "active" else "no pid"
    return str(instance["name"]), state, detail, systemd
