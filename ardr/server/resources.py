from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from ..core.network import connect_address
from ..core.paths import base_dir
from ..core.terminal import good, heading, note, section, warn
from .processes import read_pid
from .query import query_info
from .status import friendly_status


def show_resources(config_path: Path, config: dict[str, Any], instance: dict[str, Any], watch: float = 0) -> None:
    while True:
        if watch:
            print("\033[2J\033[H", end="")
        _draw(config_path, config, instance)
        if not watch:
            return
        try:
            time.sleep(watch)
        except KeyboardInterrupt:
            print("\nStopped resource view.")
            return


def _draw(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> None:
    heading(f"{instance['name']} · Resources", friendly_status(config_path, config, instance))
    pid = read_pid(config_path, config, instance)
    cpu, memory, age = _process_usage(pid)
    disk_target = base_dir(config_path, config)
    disk_target.mkdir(parents=True, exist_ok=True)
    disk = shutil.disk_usage(disk_target)
    info = _live_info(instance)
    print()
    _metric("CPU", cpu, 100)
    _metric("RAM", memory, 100)
    _metric("Disk used", disk.used / disk.total * 100, 100, suffix=f"{_bytes(disk.used)} / {_bytes(disk.total)}")
    _metric("Players", float(info.get("players", 0)), float(info.get("max_players", instance.get("server", {}).get("maxPlayers", 64))), suffix=f"{info.get('players', 0)} / {info.get('max_players', instance.get('server', {}).get('maxPlayers', 64))}")
    section("Live details")
    print(f"  Runtime     {age or 'not running'}")
    print(f"  Ping        {str(info['ping_ms']) + ' ms' if info else 'not available'}")
    print("  Tick / FPS  not reported by the Reforger server query")
    host, _ = connect_address(instance)
    note(f"Connect: {host}:{instance['port']}")
    note("Use `--watch 2` to refresh this dashboard every two seconds.")


def _process_usage(pid: int | None) -> tuple[float, float, str]:
    if not pid:
        return 0.0, 0.0, ""
    try:
        result = subprocess.run(["ps", "-p", str(pid), "-o", "%cpu=,%mem=,etime="], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
        values = result.stdout.split()
        return (float(values[0]), float(values[1]), values[2]) if len(values) == 3 else (0.0, 0.0, "")
    except (OSError, ValueError):
        return 0.0, 0.0, ""


def _live_info(instance: dict[str, Any]) -> dict[str, Any]:
    host = str(instance.get("server", {}).get("publicAddress") or "127.0.0.1")
    return query_info(instance, host, timeout=0.4) or {}


def _metric(label: str, value: float, maximum: float, suffix: str = "") -> None:
    maximum = max(maximum, 1)
    filled = min(24, round(max(0, value) / maximum * 24))
    bar = "█" * filled + "░" * (24 - filled)
    shown = suffix or f"{value:.1f}%"
    style = warn if value / maximum >= 0.85 else good
    print(f"  {label:<10} {style(bar)}  {shown}")


def _bytes(value: int) -> str:
    amount = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if amount < 1024 or unit == "TB":
            return f"{amount:.1f} {unit}" if unit != "B" else f"{int(amount)} B"
        amount /= 1024
    return f"{amount:.1f} TB"
