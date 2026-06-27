from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

DISCORD_API = "https://discord.com/api/v10"


class DiscordError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


class DiscordClient:
    def __init__(self, token: str):
        self.token = token

    def create_message(self, channel_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", f"/channels/{channel_id}/messages", payload)

    def edit_message(self, channel_id: str, message_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("PATCH", f"/channels/{channel_id}/messages/{message_id}", payload)

    def _request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{DISCORD_API}{path}",
            data=body,
            method=method,
            headers={
                "Authorization": f"Bot {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "ReforgerDeployer/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise DiscordError(exc.code, detail or exc.reason) from exc
