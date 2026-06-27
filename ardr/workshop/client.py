from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

WORKSHOP_BASE = "https://reforger.armaplatform.com/workshop"
_MOD_ID = re.compile(r"[0-9A-Fa-f]{16}")
_NEXT_DATA = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', re.DOTALL)


@dataclass(frozen=True)
class WorkshopMod:
    mod_id: str
    name: str
    version: str


@dataclass(frozen=True)
class WorkshopScenario:
    name: str
    scenario_id: str
    game_mode: str
    player_count: int | None


@dataclass(frozen=True)
class WorkshopBundle:
    mod_id: str
    name: str
    version: str
    updated_at: str
    summary: str
    scenario: WorkshopScenario | None
    scenarios: tuple[WorkshopScenario, ...]
    mods: tuple[WorkshopMod, ...]


def parse_workshop_ref(value: str) -> str:
    match = _MOD_ID.search(value.strip())
    if not match:
        raise SystemExit(f"Could not parse workshop mod ID from: {value}")
    return match.group(0).upper()


def fetch_workshop_bundle(url_or_id: str, scenario_index: int = 0) -> WorkshopBundle:
    mod_id = parse_workshop_ref(url_or_id)
    asset = _fetch_asset(mod_id)
    scenarios = _parse_scenarios(asset)
    if not scenarios:
        raise SystemExit(f"No scenarios found for workshop item {mod_id}.")
    if scenario_index < 0 or scenario_index >= len(scenarios):
        raise SystemExit(f"Scenario index {scenario_index} is out of range (0-{len(scenarios) - 1}).")
    mods = _resolve_mod_tree(mod_id)
    return WorkshopBundle(
        mod_id=mod_id,
        name=str(asset.get("name", mod_id)),
        version=str(asset.get("currentVersionNumber", "")),
        updated_at=str(asset.get("updatedAt", "")),
        summary=str(asset.get("summary", "")),
        scenario=scenarios[scenario_index],
        scenarios=scenarios,
        mods=tuple(mods),
    )


def _fetch_asset(mod_id: str) -> dict[str, Any]:
    url = f"{WORKSHOP_BASE}/{mod_id}?_={int(time.time() * 1000)}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "reforger-deployer/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"Workshop item not found ({exc.code}): {url}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach Reforger workshop: {exc.reason}") from exc
    match = _NEXT_DATA.search(html)
    if not match:
        raise SystemExit(f"Workshop page did not return mod data: {url}")
    payload = json.loads(match.group(1))
    asset = payload.get("props", {}).get("pageProps", {}).get("asset")
    if not asset:
        raise SystemExit(f"Workshop item data missing on page: {url}")
    return asset


def _parse_scenarios(asset: dict[str, Any]) -> tuple[WorkshopScenario, ...]:
    scenarios: list[WorkshopScenario] = []
    for item in asset.get("scenarios", []):
        scenario_id = str(item.get("gameId", "")).strip()
        if not scenario_id:
            continue
        player_count = item.get("playerCount")
        scenarios.append(
            WorkshopScenario(
                name=str(item.get("name", scenario_id)),
                scenario_id=scenario_id,
                game_mode=str(item.get("gameMode", "")),
                player_count=int(player_count) if player_count is not None else None,
            )
        )
    return tuple(scenarios)


def _resolve_mod_tree(root_id: str) -> list[WorkshopMod]:
    ordered: list[WorkshopMod] = []
    seen: set[str] = set()
    cache: dict[str, dict[str, Any]] = {}

    def walk(mod_id: str) -> None:
        mod_id = mod_id.upper()
        if mod_id in seen:
            return
        asset = cache.get(mod_id)
        if asset is None:
            asset = _fetch_asset(mod_id)
            cache[mod_id] = asset
        for dep in asset.get("dependencies", []):
            dep_asset = dep.get("asset") or {}
            dep_id = str(dep_asset.get("id", "")).upper()
            if dep_id:
                walk(dep_id)
        seen.add(mod_id)
        ordered.append(
            WorkshopMod(
                mod_id=mod_id,
                name=str(asset.get("name", mod_id)),
                version=str(asset.get("currentVersionNumber", "")),
            )
        )

    walk(root_id)
    return ordered


def mod_payload(mod: WorkshopMod) -> dict[str, str]:
    return {"modId": mod.mod_id, "name": mod.name, "version": mod.version}
