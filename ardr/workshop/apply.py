from __future__ import annotations

from pathlib import Path
from typing import Any

from ..config import save_config, select_instances
from ..core.terminal import heading, kv, section, table
from .client import WorkshopBundle, mod_payload


def preview_workshop_bundle(bundle: WorkshopBundle) -> None:
    heading(bundle.name, bundle.summary or bundle.mod_id)
    version_line = bundle.version or "unknown"
    if bundle.updated_at:
        version_line = f"{version_line} (updated {bundle.updated_at})"
    kv([("Version", version_line)])
    if bundle.scenario:
        kv(
            [
                ("Scenario", bundle.scenario.name),
                ("Scenario ID", bundle.scenario.scenario_id),
                ("Game mode", bundle.scenario.game_mode or "unknown"),
                ("Players", bundle.scenario.player_count or "default"),
            ]
        )
    if len(bundle.scenarios) > 1:
        section("Available scenarios")
        table(
            ["#", "Name", "Scenario ID", "Players"],
            [
                [index, item.name, item.scenario_id, item.player_count or ""]
                for index, item in enumerate(bundle.scenarios)
            ],
        )
    section("Mods to configure")
    table(
        ["Mod ID", "Name", "Version"],
        [[mod.mod_id, mod.name, mod.version] for mod in bundle.mods],
    )


def apply_workshop_bundle(
    config_path: Path,
    config: dict[str, Any],
    instance_name: str,
    bundle: WorkshopBundle,
    *,
    merge_mods: bool = False,
    set_server_name: bool = False,
) -> None:
    instance = select_instances(config, instance_name)[0]
    server = instance.setdefault("server", {})
    if bundle.scenario:
        server["scenarioId"] = bundle.scenario.scenario_id
        if bundle.scenario.player_count:
            server["maxPlayers"] = bundle.scenario.player_count
        if set_server_name:
            server["name"] = bundle.scenario.name
    incoming = [mod_payload(mod) for mod in bundle.mods]
    if merge_mods:
        existing = {str(item.get("modId", "")).upper(): item for item in instance.get("mods", [])}
        for mod in incoming:
            existing[mod["modId"]] = mod
        instance["mods"] = list(existing.values())
    else:
        instance["mods"] = incoming
    save_config(config_path, config)
    print(f"Applied workshop setup for {bundle.name} to {instance_name}.")
    if bundle.scenario:
        print(f"  scenarioId: {bundle.scenario.scenario_id}")
    print(f"  mods: {len(instance['mods'])}")
