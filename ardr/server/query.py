from __future__ import annotations

import socket
import struct
import time
from typing import Any

from ..core.terminal import heading, kv


A2S_INFO = b"\xff\xff\xff\xffTSource Engine Query\x00"


def query_server(instance: dict[str, Any], host: str, timeout: float) -> None:
    port = int(instance["queryPort"])
    started = time.monotonic()
    try:
        data = _request(host, port, timeout)
        info = _parse_info(data)
    except OSError as exc:
        raise SystemExit(f"Query failed for {host}:{port}: {exc}") from exc
    ping_ms = (time.monotonic() - started) * 1000
    heading("Live Query", f"{host}:{port} - {ping_ms:.0f} ms")
    kv((key.replace("_", " ").title(), info[key]) for key in ("name", "map", "folder", "game", "players", "max_players", "bots", "version") if key in info)


def _request(host: str, port: int, timeout: float) -> bytes:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.sendto(A2S_INFO, (host, port))
        data, _ = sock.recvfrom(4096)
        if len(data) > 5 and data[4] == 0x41:
            challenge = data[5:9]
            sock.sendto(A2S_INFO + challenge, (host, port))
            data, _ = sock.recvfrom(4096)
        return data


def _parse_info(data: bytes) -> dict[str, Any]:
    if len(data) < 6 or data[:4] != b"\xff\xff\xff\xff" or data[4] != 0x49:
        raise OSError("unexpected A2S_INFO response")
    offset = 6
    name, offset = _read_cstr(data, offset)
    map_name, offset = _read_cstr(data, offset)
    folder, offset = _read_cstr(data, offset)
    game, offset = _read_cstr(data, offset)
    offset += 2
    players, max_players, bots = struct.unpack_from("BBB", data, offset)
    offset += 4
    offset += 3
    version, offset = _read_cstr(data, offset)
    return {
        "name": name,
        "map": map_name,
        "folder": folder,
        "game": game,
        "players": players,
        "max_players": max_players,
        "bots": bots,
        "version": version,
    }


def _read_cstr(data: bytes, offset: int) -> tuple[str, int]:
    end = data.index(0, offset)
    return data[offset:end].decode("utf-8", errors="replace"), end + 1
