from __future__ import annotations

import platform
import subprocess
from pathlib import Path


def is_windows() -> bool:
    return platform.system().lower().startswith("win")


def executable_name() -> str:
    return "ArmaReforgerServer.exe" if is_windows() else "ArmaReforgerServer"


def script_suffix() -> str:
    return ".cmd" if is_windows() else ".sh"


def quote(value: str | Path) -> str:
    text = str(value)
    if is_windows():
        return f'"{text}"'
    return "'" + text.replace("'", "'\"'\"'") + "'"


def run_checked(cmd: list[str], cwd: Path | None = None) -> None:
    print("+ " + " ".join(quote(part) for part in cmd))
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)
