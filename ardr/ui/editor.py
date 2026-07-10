from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from ..core.platforming import is_windows


def open_in_micro(path: Path) -> None:
    """Open a config in Micro, offering (but never silently doing) installation."""
    if not shutil.which("micro"):
        _offer_micro_install()
    if not shutil.which("micro"):
        print(f"Micro is not installed yet. When it is ready, run:\n  micro {path}")
        return
    subprocess.run(["micro", str(path)], check=False)


def _offer_micro_install() -> None:
    print("Micro is a simple terminal editor that is great for JSON files.")
    if not sys.stdin.isatty():
        _manual_micro_instructions()
        return
    if input("Micro is not installed. Install it now? [y/N]: ").strip().lower() not in {"y", "yes"}:
        _manual_micro_instructions()
        return
    if is_windows():
        print("On Windows, install Micro with: winget install zyedidia.micro")
        return
    if shutil.which("apt-get"):
        subprocess.run(["sudo", "apt-get", "update"], check=False)
        subprocess.run(["sudo", "apt-get", "install", "-y", "micro"], check=False)
    elif shutil.which("brew"):
        subprocess.run(["brew", "install", "micro"], check=False)
    else:
        _manual_micro_instructions()


def _manual_micro_instructions() -> None:
    print("Install Micro with one of these commands, then run the edit command again:")
    print("  Debian/Ubuntu: sudo apt install micro")
    print("  macOS:         brew install micro")
    print("  Other Linux:   https://micro-editor.github.io/")
