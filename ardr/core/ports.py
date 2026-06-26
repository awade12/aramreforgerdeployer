from __future__ import annotations

from typing import Any


GAME_START = 2001
QUERY_START = 17777
STEP = 2


def assign_missing_ports(config: dict[str, Any]) -> bool:
    used = _used_ports([])
    changed = False
    for instance in config.get("instances", []):
        port = _valid_port(instance.get("port"))
        query = _valid_port(instance.get("queryPort"))
        if port and port not in used:
            used.add(port)
        else:
            port = _next_free(used, GAME_START)
            instance["port"] = port
            used.add(port)
            changed = True
        if query and query not in used:
            used.add(query)
        else:
            query = _next_free(used, QUERY_START)
            instance["queryPort"] = query
            used.add(query)
            changed = True
    return changed


def next_port_pair(config: dict[str, Any]) -> tuple[int, int]:
    used = _used_ports(config.get("instances", []))
    return _next_free(used, GAME_START), _next_free(used, QUERY_START)


def _used_ports(instances: list[dict[str, Any]]) -> set[int]:
    used: set[int] = set()
    for instance in instances:
        for key in ("port", "queryPort"):
            port = _valid_port(instance.get(key))
            if port:
                used.add(port)
    return used


def _valid_port(value: Any) -> int | None:
    try:
        port = int(value)
    except (TypeError, ValueError):
        return None
    return port if 1 <= port <= 65535 else None


def _next_free(used: set[int], start: int) -> int:
    port = start
    while port in used:
        port += STEP
    return port
