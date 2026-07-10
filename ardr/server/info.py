from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from ..core.network import address_note, connect_address
from ..core.paths import generated_dir, install_dir, pid_file, profile_dir
from ..core.platforming import executable_name, quote
from ..core.terminal import commands, heading, kv, note, section, status_label
from ..platform.services import service_name, systemd_state
from .processes import process_running, read_pid
from .render import server_config_path, start_command


def show_info(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> None:
    name = instance["name"]
    server = instance.get("server", {})
    pid = read_pid(config_path, config, instance)
    running = process_running(pid)
    svc = service_name(instance)
    public_name = server.get("name", name)
    host, host_source = connect_address(instance)
    state = systemd_state(instance)
    runtime = "running" if running or state == "active" else "stopped"
    runtime_detail = f"pid {pid}" if pid else f"systemd {state}" if state else "no pid"
    is_default = str(config.get("defaultInstance", "")).strip() == name

    heading(f"{name}", str(public_name))
    kv(
        [
            ("Status", f"{status_label(runtime)} ({runtime_detail})"),
            ("Branch", instance.get("branch", "stable")),
            ("Players", server.get("maxPlayers", 64)),
            ("Service", f"{svc}" + (f" ({state})" if state else "")),
            ("Default", "yes" if is_default else "no"),
            ("Scenario", server.get("scenarioId", "")),
        ]
    )

    section("Connect")
    kv(
        [
            ("Direct/IP", f"{host}:{instance['port']}"),
            ("Address source", host_source),
            ("Game UDP", instance["port"]),
            ("Query UDP", instance["queryPort"]),
        ]
    )
    note(address_note(host, host_source))

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

    section("Recommended Next Step")
    commands([_recommended_command(config_path, config, instance, runtime)])

    section("Daily Commands")
    commands(
        [
            (_cmd(config, name, "status"), "show runtime state"),
            (_cmd(config, name, "tail"), "follow logs"),
            (_cmd(config, name, "restart"), "restart server"),
            (_cmd(config, name, "update"), "update server files"),
            (_cmd(config, name, "backup create"), "create a backup"),
        ]
    )

    section("Easy Server-First Shortcuts")
    commands(
        [
            (f"reforger {name}", "open this server's summary"),
            (f"reforger {name} start", "start it (you can also say `on`)"),
            (f"reforger {name} stop", "stop it (you can also say `off`)"),
            (f"reforger {name} logs", "show recent logs"),
            (f"reforger {name} health", "run readiness checks"),
        ]
    )

    section("Setup & Fix")
    commands(
        [
            (_cmd(config, name, "launch"), "preview first deploy"),
            (f"sudo {_cmd(config, name, 'launch')} --apply", "install service and start"),
            (_cmd(config, name, "ports"), "show firewall ports"),
            (_cmd(config, name, "check"), "validate config and host"),
            (_cmd(config, name, "fix"), "repair safe ports and check again"),
            (f"reforger default {name}", "make this server the default" if not is_default else "already the default"),
        ]
    )

    section("Mods")
    commands(
        [
            (_cmd(config, name, "mods list"), "list configured mods"),
            (_cmd(config, name, "mods add") + " --id MOD_ID --name \"Mod Name\"", "add or update a mod"),
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


def _cmd(config: dict[str, Any], name: str, command: str) -> str:
    if str(config.get("defaultInstance", "")).strip() == name:
        return f"reforger {command}"
    return f"reforger {command} {name}"


def _recommended_command(config_path: Path, config: dict[str, Any], instance: dict[str, Any], runtime: str) -> tuple[str, str]:
    name = str(instance["name"])
    exe = install_dir(config_path, config, instance) / executable_name()
    if not exe.exists():
        return f"sudo {_cmd(config, name, 'launch')} --apply", "server files/service are not installed yet"
    if runtime == "running":
        return _cmd(config, name, "tail"), "server is running; watch logs"
    return _cmd(config, name, "start"), "server is installed but stopped"
