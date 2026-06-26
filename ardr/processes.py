from __future__ import annotations

import os
import signal
import subprocess
from pathlib import Path
from typing import Any

from .paths import generated_dir, install_dir, pid_file
from .platforming import executable_name, is_windows, run_checked
from .render import start_command


def read_pid(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> int | None:
    path = pid_file(config_path, config, instance)
    if not path.exists():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def process_running(pid: int | None) -> bool:
    if not pid:
        return False
    if is_windows():
        result = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
        return str(pid) in result.stdout
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def cleanup_dead_pid(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> None:
    pid = read_pid(config_path, config, instance)
    if pid and not process_running(pid):
        pid_file(config_path, config, instance).unlink(missing_ok=True)


def start_instance(config_path: Path, config: dict[str, Any], instance: dict[str, Any], foreground: bool = False) -> None:
    cleanup_dead_pid(config_path, config, instance)
    pid = read_pid(config_path, config, instance)
    if pid and process_running(pid):
        print(f"{instance['name']} is already running with PID {pid}")
        return
    cwd = install_dir(config_path, config, instance)
    if not (cwd / executable_name()).exists():
        raise SystemExit(f"Server executable not found. Run install first: {cwd / executable_name()}")
    cmd = start_command(config_path, config, instance)
    if foreground:
        run_checked(cmd, cwd=cwd)
        return
    if is_windows():
        proc = subprocess.Popen(cmd, cwd=str(cwd), creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)  # type: ignore[attr-defined]
    else:
        proc = subprocess.Popen(cmd, cwd=str(cwd), start_new_session=True)
    path = pid_file(config_path, config, instance)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(proc.pid), encoding="utf-8")
    print(f"Started {instance['name']} with PID {proc.pid}")


def stop_instance(config_path: Path, config: dict[str, Any], instance: dict[str, Any], quiet: bool = False) -> bool:
    path = pid_file(config_path, config, instance)
    pid = read_pid(config_path, config, instance)
    if not pid or not process_running(pid):
        path.unlink(missing_ok=True)
        if not quiet:
            print(f"{instance['name']} is not running under Reforger.")
        return False
    if is_windows():
        run_checked(["taskkill", "/PID", str(pid), "/T", "/F"])
    else:
        os.killpg(pid, signal.SIGTERM)
    path.unlink(missing_ok=True)
    if not quiet:
        print(f"Stopped {instance['name']} PID {pid}")
    return True


def pause_instance(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> None:
    pid = read_pid(config_path, config, instance)
    if not process_running(pid):
        raise SystemExit(f"{instance['name']} is not running under Reforger.")
    if is_windows():
        run_checked(["powershell", "-NoProfile", "-Command", f"Suspend-Process -Id {pid}"])
    else:
        os.killpg(int(pid), signal.SIGSTOP)
    print(f"Paused {instance['name']} PID {pid}")


def resume_instance(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> None:
    pid = read_pid(config_path, config, instance)
    if not process_running(pid):
        raise SystemExit(f"{instance['name']} is not running under Reforger.")
    if is_windows():
        run_checked(["powershell", "-NoProfile", "-Command", f"Resume-Process -Id {pid}"])
    else:
        os.killpg(int(pid), signal.SIGCONT)
    print(f"Resumed {instance['name']} PID {pid}")


def tracked_log_dir(config_path: Path, config: dict[str, Any], instance: dict[str, Any]) -> Path:
    return generated_dir(config_path, config, instance)

