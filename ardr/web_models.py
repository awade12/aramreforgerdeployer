from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .paths import generated_dir, install_dir, pid_file, profile_dir
from .platforming import executable_name
from .processes import cleanup_dead_pid, process_running, read_pid
from .services import systemd_state


def instance_details(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> dict[str, Any]:
    cleanup_dead_pid(config_path, config, instance)
    pid = read_pid(config_path, config, instance)
    running = process_running(pid)
    install = install_dir(config_path, config, instance)
    exe = install / executable_name()
    inst_dir = Path(str(config.get("instanceDir", "instances")))
    if not inst_dir.is_absolute():
        inst_dir = config_path.parent / inst_dir
    svc = systemd_state(instance) or "unavailable"
    return {
        "checkedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "running": running,
        "pid": pid,
        "runtime": "running" if running else "stopped",
        "service": svc,
        "serviceInstalled": svc not in {"", "unavailable"},
        "installDir": install,
        "profileDir": profile_dir(config_path, instance),
        "generatedDir": generated_dir(config_path, config, instance),
        "configFile": inst_dir / f"{instance['name']}.json",
        "pidFile": pid_file(config_path, config, instance),
        "serverExe": exe,
        "serverExeExists": exe.exists(),
    }
