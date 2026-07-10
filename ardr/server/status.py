from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

from ..core.terminal import status_label
from ..platform.services import systemd_state
from .processes import cleanup_dead_pid, process_running, read_pid


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


def friendly_status(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> str:
    """A sentence for people; detailed PID/service data stays in `info`."""
    _, state, _, _ = status_row(config_path, config, instance)
    if state == "running":
        age = _process_age(read_pid(config_path, config, instance))
        players = _player_count(instance)
        details = ["Running"]
        if players:
            details.append(players)
        details.append(f"started {age} ago" if age else "ready for players")
        return " · ".join(details)
    return "Stopped · choose Start when you are ready"


def _process_age(pid: int | None) -> str:
    if not pid:
        return ""
    try:
        result = subprocess.run(["ps", "-o", "etime=", "-p", str(pid)], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    except OSError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def _player_count(instance: dict[str, Any]) -> str:
    """A short best-effort query: a missing response must never slow the hub down."""
    from .query import query_info

    host = str(instance.get("server", {}).get("publicAddress") or "127.0.0.1")
    info = query_info(instance, host, timeout=0.25)
    if not info:
        return ""
    return f"{info.get('players', 0)}/{info.get('max_players', '?')} players"
