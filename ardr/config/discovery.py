from __future__ import annotations

import sys
from pathlib import Path

from ..core.constants import DEFAULT_CONFIG


def resolve_config_path(explicit: str | None) -> str:
    """Find the deployer config without making people cd into the repo first."""
    if explicit:
        return explicit
    for folder in _search_folders():
        candidate = folder / DEFAULT_CONFIG
        if candidate.is_file():
            return str(candidate)
    # Keep `init` intuitive for a genuinely new installation: it creates the
    # config in the directory the person is currently using.
    return str(Path.cwd() / DEFAULT_CONFIG)


def _search_folders() -> list[Path]:
    folders: list[Path] = []
    cwd = Path.cwd().resolve()
    folders.extend([cwd, *cwd.parents])
    try:
        folders.append(Path(sys.argv[0]).resolve().parent)
    except OSError:
        pass
    folders.append(Path.home() / "aramreforgerdeployer")
    unique: list[Path] = []
    for folder in folders:
        if folder not in unique:
            unique.append(folder)
    return unique
