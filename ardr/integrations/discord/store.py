from __future__ import annotations

import configparser
import getpass
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_INI = ".ardr-discord.ini"


@dataclass
class DiscordSettings:
    bot_token: str
    channel_id: str
    poll_interval_seconds: int
    query_live: bool
    title: str
    message_id: str | None
    ini_path: Path


def resolve_ini_path(path: str | None) -> Path:
    return Path(path or DEFAULT_INI)


def load_settings(
    ini_path: Path,
    channel_id: str | None = None,
    interval: int | None = None,
) -> DiscordSettings:
    if not ini_path.exists():
        raise SystemExit(
            f"Discord config not found: {ini_path}\n"
            "Run `reforger discord configure` to create it."
        )
    parser = _read_ini(ini_path)
    if not parser.has_section("discord"):
        raise SystemExit(f"Discord config is missing a [discord] section: {ini_path}")

    discord = parser["discord"]
    env_token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    file_token = discord.get("bot_token", "").strip()
    bot_token = env_token or file_token
    if not bot_token:
        raise SystemExit(
            "Discord bot token not set. Add bot_token to your ini file with "
            "`reforger discord configure`, or export DISCORD_BOT_TOKEN."
        )

    stored_channel = discord.get("channel_id", "").strip()
    resolved_channel = (channel_id or stored_channel).strip()
    if not resolved_channel:
        raise SystemExit(
            "Discord channel ID not set. Run `reforger discord configure` "
            "or pass --channel-id."
        )

    stored_interval = max(15, int(discord.get("poll_interval_seconds", "30")))
    message_id = None
    if parser.has_section("state"):
        stored_channel_id = parser["state"].get("channel_id", "").strip()
        if stored_channel_id == resolved_channel:
            message_id = parser["state"].get("message_id", "").strip() or None

    return DiscordSettings(
        bot_token=bot_token,
        channel_id=resolved_channel,
        poll_interval_seconds=max(15, interval if interval is not None else stored_interval),
        query_live=_as_bool(discord.get("query_live", "true")),
        title=discord.get("title", "Arma Reforger Server Status").strip() or "Arma Reforger Server Status",
        message_id=message_id,
        ini_path=ini_path,
    )


def save_message_id(ini_path: Path, channel_id: str, message_id: str) -> None:
    parser = _read_ini(ini_path) if ini_path.exists() else configparser.ConfigParser()
    if not parser.has_section("discord"):
        raise SystemExit(f"Discord config not found: {ini_path}")
    if not parser.has_section("state"):
        parser.add_section("state")
    parser["state"]["channel_id"] = channel_id
    parser["state"]["message_id"] = message_id
    _write_ini(ini_path, parser)


def configure_discord(
    ini_path: Path,
    channel_id: str | None = None,
    token: str | None = None,
    interval: int | None = None,
    title: str | None = None,
    query_live: bool | None = None,
) -> Path:
    parser = _read_ini(ini_path) if ini_path.exists() else configparser.ConfigParser()
    if not parser.has_section("discord"):
        parser.add_section("discord")

    discord = parser["discord"]
    current_token = discord.get("bot_token", "").strip()
    resolved_token = (token or os.environ.get("DISCORD_BOT_TOKEN", "").strip() or "").strip()
    if not resolved_token:
        prompt = "Discord bot token"
        if current_token:
            prompt += " (leave blank to keep current)"
        resolved_token = getpass.getpass(f"{prompt}: ").strip() or current_token
    if not resolved_token:
        raise SystemExit("A Discord bot token is required.")

    resolved_channel = (channel_id or discord.get("channel_id", "").strip() or input("Discord channel ID: ")).strip()
    if not resolved_channel:
        raise SystemExit("A Discord channel ID is required.")

    resolved_title = (title or discord.get("title", "Arma Reforger Server Status")).strip()
    resolved_interval = max(15, interval if interval is not None else int(discord.get("poll_interval_seconds", "30")))
    resolved_query_live = query_live if query_live is not None else _as_bool(discord.get("query_live", "true"))

    discord["bot_token"] = resolved_token
    discord["channel_id"] = resolved_channel
    discord["poll_interval_seconds"] = str(resolved_interval)
    discord["query_live"] = "true" if resolved_query_live else "false"
    discord["title"] = resolved_title
    _write_ini(ini_path, parser)
    return ini_path


def show_discord_status(ini_path: Path) -> None:
    if not ini_path.exists():
        print(f"Discord config: not configured ({ini_path})")
        print("Run `reforger discord configure` to set it up.")
        return
    settings = load_settings(ini_path)
    token_source = "environment" if os.environ.get("DISCORD_BOT_TOKEN", "").strip() else "ini file"
    print(f"Discord config: {ini_path}")
    print(f"  channel_id: {settings.channel_id}")
    print(f"  poll_interval_seconds: {settings.poll_interval_seconds}")
    print(f"  query_live: {'yes' if settings.query_live else 'no'}")
    print(f"  title: {settings.title}")
    print(f"  bot_token: set via {token_source}")
    print(f"  saved embed: {settings.message_id or 'none'}")


def _read_ini(path: Path) -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    return parser


def _write_ini(path: Path, parser: configparser.ConfigParser) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        parser.write(fh)
    path.chmod(0o600)


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}
