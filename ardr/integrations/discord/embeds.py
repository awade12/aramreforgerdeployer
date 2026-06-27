from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ...core.network import connect_address
from ...server.query import query_info
from ...server.status import status_row
from ...web.models import instance_details
from .store import DiscordSettings


def build_status_payload(
    config_path: Path,
    config: dict[str, Any],
    instances: list[dict[str, Any]],
    settings: DiscordSettings,
) -> dict[str, Any]:
    fields: list[dict[str, Any]] = []
    running_count = 0
    for instance in instances:
        name, state, detail, systemd = status_row(config_path, config, instance)
        details = instance_details(config_path, config, instance)
        if state == "running":
            running_count += 1
        host, _ = connect_address(instance)
        live = query_info(instance, host, 2.0) if settings.query_live and state == "running" else None
        fields.append(_instance_field(instance, name, state, detail, systemd, details, live))

    total = len(instances)
    summary = f"{running_count}/{total} online"
    color = 0x22C55E if running_count == total and total else 0xEF4444 if running_count == 0 else 0xF59E0B
    checked = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    embed = {
        "title": settings.title,
        "description": f"{summary}\nLast updated: {checked}",
        "color": color,
        "fields": fields[:25],
        "footer": {"text": "Reforger Deployer"},
    }
    return {"embeds": [embed]}


def _instance_field(
    instance: dict[str, Any],
    name: str,
    state: str,
    detail: str,
    systemd: str,
    details: dict[str, Any],
    live: dict[str, Any] | None,
) -> dict[str, Any]:
    server = instance.get("server", {})
    display_name = str(server.get("name", name))
    icon = "Online" if state == "running" else "Offline"
    lines = [
        f"**{icon}** {state.title()}",
        f"Connect: `{details['connectAddress']}`",
        f"Game UDP: `{instance['port']}` | Query UDP: `{instance['queryPort']}`",
    ]
    if detail:
        lines.append(f"Process: {detail}")
    if systemd:
        lines.append(f"Systemd: {systemd}")
    if live:
        lines.append(f"Players: {live['players']}/{live['max_players']}")
        if live.get("map"):
            lines.append(f"Map: {live['map']}")
        if live.get("version"):
            lines.append(f"Version: {live['version']}")
    elif state == "running" and not details.get("serverExeExists"):
        lines.append("Executable: missing")
    return {
        "name": display_name,
        "value": "\n".join(lines)[:1024],
        "inline": False,
    }
