from __future__ import annotations

from typing import Any

from ..core.network import connect_address
from ..core.terminal import heading, note


def print_invite(instance: dict[str, Any]) -> None:
    server = instance.get("server", {})
    host, source = connect_address(instance)
    heading("Player Invite", "Copy and send the message below.")
    print()
    print(f"🎮 Join {server.get('name', instance['name'])} on Arma Reforger!")
    print(f"Server: {host}:{instance['port']}")
    password = str(server.get("password", ""))
    print(f"Password: {password}" if password else "Password: none — it is open to everyone")
    print(f"Players: up to {server.get('maxPlayers', 64)}")
    print()
    note(f"Address source: {source}. Set publicAddress in `reforger configure` if this is not your public VPS address.")
