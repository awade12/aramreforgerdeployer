from __future__ import annotations

import signal
import time
from pathlib import Path
from typing import Any

from ...config import load_config
from .api import DiscordClient, DiscordError
from .embeds import build_status_payload
from .store import DiscordSettings, load_settings, save_message_id


def sync_discord_status(
    config_path: Path,
    config: dict[str, Any],
    settings: DiscordSettings,
    force_post: bool = False,
) -> str:
    instances = config.get("instances", [])
    if not isinstance(instances, list) or not instances:
        raise SystemExit("No instances configured.")
    client = DiscordClient(settings.bot_token)
    payload = build_status_payload(config_path, config, instances, settings)
    message_id = None if force_post else settings.message_id
    if message_id:
        try:
            client.edit_message(settings.channel_id, message_id, payload)
            return f"Updated Discord status embed {message_id} in channel {settings.channel_id}."
        except DiscordError as exc:
            if exc.status != 404:
                raise SystemExit(f"Discord update failed ({exc.status}): {exc}") from exc
    response = client.create_message(settings.channel_id, payload)
    new_id = str(response["id"])
    save_message_id(settings.ini_path, settings.channel_id, new_id)
    return f"Posted Discord status embed {new_id} in channel {settings.channel_id}."


def serve_discord(config: str, ini_path: Path, interval: int | None) -> None:
    config_path, _ = load_config(config)
    settings = load_settings(ini_path, interval=interval)
    stop = False

    def handle_stop(_signum: int, _frame: object) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)
    print(
        f"Discord status updater running for channel {settings.channel_id} "
        f"every {settings.poll_interval_seconds}s. Press Ctrl+C to stop."
    )
    poll_seconds = settings.poll_interval_seconds
    while not stop:
        try:
            _, current = load_config(config)
            settings = load_settings(ini_path, interval=interval)
            poll_seconds = settings.poll_interval_seconds
            message = sync_discord_status(config_path, current, settings)
            print(message)
        except SystemExit as exc:
            print(f"Discord sync failed: {exc}")
        except DiscordError as exc:
            print(f"Discord API error ({exc.status}): {exc}")
        for _ in range(poll_seconds):
            if stop:
                break
            time.sleep(1)
