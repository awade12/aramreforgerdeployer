from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.paths import install_dir


def append_rcon(config_path: Path, config: dict[str, Any], instance: dict[str, Any], rcon_port: int, password: str) -> None:
    be_dir = install_dir(config_path, config, instance) / "BattlEye"
    be_dir.mkdir(parents=True, exist_ok=True)
    be_cfg = be_dir / "BEServer_x64.cfg"
    existing = be_cfg.read_text(encoding="utf-8", errors="ignore") if be_cfg.exists() else ""
    additions = []
    if "RConPort" not in existing:
        additions.append(f"RConPort {rcon_port}")
    if "RConPassword" not in existing:
        additions.append(f"RConPassword {password}")
    if not additions:
        print(f"No changes needed; RCon settings already exist in {be_cfg}")
        return
    with be_cfg.open("a", encoding="utf-8") as fh:
        if existing and not existing.endswith("\n"):
            fh.write("\n")
        fh.write("\n".join(additions))
        fh.write("\n")
    print(f"Appended BattlEye RCon settings to {be_cfg}")
