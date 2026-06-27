from __future__ import annotations

import io
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ardr.integrations.discord.store import (
    configure_discord,
    load_settings,
    save_message_id,
    show_discord_status,
)


class DiscordStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.ini_path = Path(self.tempdir.name) / "discord.ini"

    def tearDown(self) -> None:
        self.tempdir.cleanup()
        os.environ.pop("DISCORD_BOT_TOKEN", None)

    def test_configure_writes_private_ini(self) -> None:
        configure_discord(
            self.ini_path,
            channel_id="111222333444555666",
            token="secret-token",
            interval=20,
            title="Test Servers",
            query_live=False,
        )
        self.assertTrue(self.ini_path.exists())
        mode = self.ini_path.stat().st_mode
        self.assertEqual(stat.S_IMODE(mode), 0o600)
        settings = load_settings(self.ini_path)
        self.assertEqual(settings.bot_token, "secret-token")
        self.assertEqual(settings.channel_id, "111222333444555666")
        self.assertEqual(settings.poll_interval_seconds, 20)
        self.assertEqual(settings.title, "Test Servers")
        self.assertFalse(settings.query_live)
        self.assertIsNone(settings.message_id)

    def test_env_token_overrides_ini(self) -> None:
        configure_discord(self.ini_path, channel_id="999", token="file-token")
        os.environ["DISCORD_BOT_TOKEN"] = "env-token"
        settings = load_settings(self.ini_path)
        self.assertEqual(settings.bot_token, "env-token")

    def test_save_message_id_round_trip(self) -> None:
        configure_discord(self.ini_path, channel_id="999", token="file-token")
        save_message_id(self.ini_path, "999", "message-123")
        settings = load_settings(self.ini_path)
        self.assertEqual(settings.message_id, "message-123")

    def test_message_id_ignored_for_different_channel_override(self) -> None:
        configure_discord(self.ini_path, channel_id="999", token="file-token")
        save_message_id(self.ini_path, "999", "message-123")
        settings = load_settings(self.ini_path, channel_id="888")
        self.assertIsNone(settings.message_id)

    def test_interval_has_minimum(self) -> None:
        configure_discord(self.ini_path, channel_id="999", token="file-token", interval=5)
        settings = load_settings(self.ini_path)
        self.assertEqual(settings.poll_interval_seconds, 15)

    def test_missing_ini_exits(self) -> None:
        with self.assertRaises(SystemExit):
            load_settings(self.ini_path)

    def test_show_status_without_token(self) -> None:
        configure_discord(self.ini_path, channel_id="999", token="file-token")
        buffer = io.StringIO()
        with patch("sys.stdout", buffer):
            show_discord_status(self.ini_path)
        output = buffer.getvalue()
        self.assertIn("channel_id: 999", output)
        self.assertNotIn("file-token", output)
        self.assertIn("bot_token: set via ini file", output)


if __name__ == "__main__":
    unittest.main()
