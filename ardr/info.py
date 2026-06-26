from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .paths import generated_dir, install_dir, pid_file, profile_dir
from .platforming import quote
from .processes import process_running, read_pid
from .render import server_config_path, start_command
from .services import service_name, systemd_state


def show_info(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> None:
    name = instance["name"]
    server = instance.get("server", {})
    pid = read_pid(config_path, config, instance)
    running = process_running(pid)
    svc = service_name(instance)
    public_name = server.get("name", name)
    host = server.get("publicAddress") or "<VPS_PUBLIC_IP>"
    print(f"Instance: {name}")
    print(f"Server name: {public_name}")
    print(f"Branch: {instance.get('branch', 'stable')}")
    print(f"Players: {server.get('maxPlayers', 64)}")
    print(f"Status: {'running' if running else 'stopped'}" + (f" pid={pid}" if pid else ""))
    state = systemd_state(instance)
    print(f"Service: {svc}" + (f" ({state})" if state else ""))
    print()
    print("Connection")
    print(f"  Game UDP: {instance['port']}")
    print(f"  Query UDP: {instance['queryPort']}")
    print(f"  Direct/IP connect: {host}:{instance['port']}")
    print()
    print("Files")
    print(f"  Instance config: {_instance_file(config_path, config, name)}")
    print(f"  Generated server config: {server_config_path(config_path, config, instance)}")
    print(f"  Start script: {generated_dir(config_path, config, instance) / ('start-' + name + '.sh')}")
    print(f"  Install dir: {install_dir(config_path, config, instance)}")
    print(f"  Profile/log dir: {profile_dir(config_path, instance)}")
    print(f"  PID file: {pid_file(config_path, config, instance)}")
    print()
    print("Useful Commands")
    print(f"  reforger service status --instance {name}")
    print(f"  reforger service logs --instance {name} --follow")
    print(f"  sudo reforger service restart --instance {name}")
    print(f"  reforger ports --instance {name}")
    print(f"  reforger mods list --instance {name}")
    print(f"  reforger backup create --instance {name}")
    print()
    print("Launch Command")
    print("  " + " ".join(quote(part) for part in start_command(config_path, config, instance)))
    if not shutil.which("systemctl"):
        print()
        print("Note: systemctl was not found here; service commands are for Linux/systemd hosts.")


def _instance_file(config_path: Path, config: dict[str, Any], name: str) -> Path:
    raw = Path(str(config.get("instanceDir", "instances")))
    instance_dir = raw if raw.is_absolute() else config_path.parent / raw
    return instance_dir / f"{name}.json"

