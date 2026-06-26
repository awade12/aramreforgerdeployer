from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .config import select_instances
from .paths import generated_dir, install_dir
from .platforming import is_windows, run_checked
from .render import render_instances, render_start_script


def service_name(instance: dict[str, Any]) -> str:
    return f"ardr-{instance['name']}.service"


def service_text(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> str:
    user = os.environ.get("SUDO_USER") or os.environ.get("USER") or "steam"
    return f"""[Unit]
Description=Arma Reforger Dedicated Server ({instance['name']})
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User={user}
WorkingDirectory={install_dir(config_path, config, instance)}
ExecStart={render_start_script(config_path, config, instance)}
Restart=on-failure
RestartSec=15
LimitNOFILE=100000

[Install]
WantedBy=multi-user.target
"""


def render_systemd(config_path: Path, config: dict[str, Any], instance_name: str | None, install: bool) -> None:
    if is_windows():
        raise SystemExit("systemd is only available on Linux.")
    render_instances(config_path, config, instance_name)
    for instance in select_instances(config, instance_name):
        name = service_name(instance)
        rendered = generated_dir(config_path, config, instance) / name
        rendered.write_text(service_text(config_path, config, instance), encoding="utf-8")
        print(f"Rendered {rendered}")
        if install:
            if os.geteuid() != 0:
                raise SystemExit("Run systemd install with sudo.")
            target = Path("/etc/systemd/system") / name
            shutil.copyfile(rendered, target)
            print(f"Installed {target}")
    if install:
        run_checked(["systemctl", "daemon-reload"])


def systemd_state(instance: dict[str, Any]) -> str:
    if is_windows() or not shutil.which("systemctl"):
        return ""
    result = subprocess.run(["systemctl", "is-active", service_name(instance)], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return result.stdout.strip()


def control_service(instance: dict[str, Any], action: str, lines: int = 80, follow: bool = False) -> None:
    if is_windows():
        raise SystemExit("service controls are only available for systemd on Linux.")
    name = service_name(instance)
    if action == "logs":
        cmd = ["journalctl", "-u", name, "-n", str(lines)]
        run_checked(cmd + (["-f"] if follow else []))
    elif action in {"start", "stop", "restart", "status", "enable", "disable"}:
        run_checked(["systemctl", action, name])
    else:
        raise SystemExit(f"Unsupported service action: {action}")


def manage_windows_task(config_path: Path, config: dict[str, Any], instance_name: str | None, install: bool) -> None:
    if not is_windows():
        raise SystemExit("windows-task is only available on Windows.")
    render_instances(config_path, config, instance_name)
    ardr = Path(sys.argv[0]).resolve()
    for instance in select_instances(config, instance_name):
        task_name = f"ARDR {instance['name']}"
        if install:
            task_cmd = f'"{sys.executable}" "{ardr}" start --config "{config_path}" --instance "{instance["name"]}"'
            run_checked(["schtasks", "/Create", "/TN", task_name, "/SC", "ONSTART", "/RL", "HIGHEST", "/TR", task_cmd, "/F"])
        else:
            run_checked(["schtasks", "/Delete", "/TN", task_name, "/F"])
