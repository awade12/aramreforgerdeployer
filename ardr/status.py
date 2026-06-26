from __future__ import annotations

from pathlib import Path
from typing import Any

from .processes import cleanup_dead_pid, process_running, read_pid
from .services import systemd_state


def print_status(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> None:
    cleanup_dead_pid(config_path, config, instance)
    pid = read_pid(config_path, config, instance)
    systemd = systemd_state(instance)
    state = "running" if process_running(pid) or systemd == "active" else "stopped"
    detail = f"pid {pid}" if pid else "systemd active" if systemd == "active" else "no pid"
    print(f"{instance['name']}: {state} ({detail}{', systemd ' + systemd if systemd else ''})")
