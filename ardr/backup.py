from __future__ import annotations

import shutil
import tarfile
import time
from pathlib import Path
from typing import Any

from .config import select_instances
from .paths import base_dir, install_dir, profile_dir


def create_backup(config_path: Path, config: dict[str, Any], instance_name: str | None, include_downloads: bool) -> Path:
    out_dir = base_dir(config_path, config) / "backups"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    name = instance_name or "all"
    archive = out_dir / f"ardr-backup-{name}-{stamp}.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        _add_if_exists(tar, config_path, "deployer.json")
        _add_dir_if_exists(tar, config_path.parent / str(config.get("instanceDir", "instances")), "instances")
        for instance in select_instances(config, instance_name):
            _add_dir_if_exists(tar, profile_dir(config_path, instance), f"profiles/{instance['name']}")
            _add_dir_if_exists(tar, install_dir(config_path, config, instance) / "BattlEye", f"battleye/{instance['name']}")
            if include_downloads:
                _add_dir_if_exists(tar, install_dir(config_path, config, instance), f"server/{instance['name']}")
    print(f"Created backup {archive}")
    return archive


def restore_backup(archive: Path, target: Path) -> None:
    if not archive.exists():
        raise SystemExit(f"Backup not found: {archive}")
    target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as tar:
        tar.extractall(target)
    print(f"Restored {archive} into {target}")


def list_backups(config_path: Path, config: dict[str, Any]) -> None:
    out_dir = base_dir(config_path, config) / "backups"
    if not out_dir.exists():
        print("No backups found.")
        return
    for path in sorted(out_dir.glob("*.tar.gz")):
        print(path)


def _add_if_exists(tar: tarfile.TarFile, path: Path, arcname: str) -> None:
    if path.exists():
        tar.add(path, arcname=arcname)


def _add_dir_if_exists(tar: tarfile.TarFile, path: Path, arcname: str) -> None:
    if path.exists():
        tar.add(path, arcname=arcname, filter=_skip_noise)


def _skip_noise(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
    return None if "__pycache__" in info.name else info

