from __future__ import annotations

import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

from .config import normalize_config_ports, validate_config
from .paths import base_dir, install_dir
from .platforming import executable_name, is_windows
from .terminal import check_line, heading, note, section


def run_doctor(config_path: Path, config: dict[str, Any]) -> int:
    heading("Doctor", "Host, config, server files, and network preflight checks.")
    failures = 0
    failures += _check("Python 3.10+", sys.version_info >= (3, 10), sys.version.split()[0])
    failures += _check("SteamCMD available", _steamcmd_exists(config), str(config.get("steamcmd", "steamcmd")))
    failures += _check("Config valid", not validate_config(config), "ports are normalized" if not normalize_config_ports(config) else "ports need saving")
    failures += _disk_check(config_path, config)
    failures += _port_checks(config)
    failures += _executable_checks(config_path, config)
    _firewall_notes(config)
    return failures


def _check(label: str, ok: bool, detail: str = "") -> int:
    check_line(ok, label, detail)
    return 0 if ok else 1


def _steamcmd_exists(config: dict[str, Any]) -> bool:
    steamcmd = str(config.get("steamcmd", "steamcmd"))
    return bool(shutil.which(steamcmd) or Path(steamcmd).exists())


def _disk_check(config_path: Path, config: dict[str, Any]) -> int:
    target = base_dir(config_path, config)
    target.mkdir(parents=True, exist_ok=True)
    free_gb = shutil.disk_usage(target).free / 1024**3
    return _check("Disk free >= 15 GB", free_gb >= 15, f"{free_gb:.1f} GB free at {target}")


def _port_checks(config: dict[str, Any]) -> int:
    section("UDP Bind Checks")
    failures = 0
    for instance in config.get("instances", []):
        for label, port in (("game", int(instance["port"])), ("query", int(instance["queryPort"]))):
            failures += _check(f"{instance['name']} {label} UDP {port} bindable", _udp_bindable(port), "local bind check")
    return failures


def _udp_bindable(port: int) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", port))
        sock.close()
        return True
    except OSError:
        return False


def _executable_checks(config_path: Path, config: dict[str, Any]) -> int:
    section("Server Executables")
    failures = 0
    for instance in config.get("instances", []):
        exe = install_dir(config_path, config, instance) / executable_name()
        failures += _check(f"{instance['name']} server executable", exe.exists(), str(exe))
    return failures


def _firewall_notes(config: dict[str, Any]) -> None:
    section("Firewall Notes")
    if is_windows():
        note("Windows firewall: run `reforger ports` for New-NetFirewallRule examples.")
        return
    ufw = shutil.which("ufw")
    if ufw:
        result = subprocess.run([ufw, "status"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
        first = result.stdout.splitlines()[0] if result.stdout else "unknown"
        note(f"UFW status: {first}")
    else:
        note("UFW not found; open UDP ports with your distro firewall if enabled.")
    note("VPS provider firewall/security groups must also allow the UDP ports from `reforger ports`.")
