from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch

from ardr.config.sample import sample_config
from ardr.integrations.discord.api import DiscordClient, DiscordError
from ardr.integrations.discord.bot import sync_discord_status
from ardr.integrations.discord.store import DiscordSettings, configure_discord


class DiscordSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.ini_path = self.root / "discord.ini"
        configure_discord(
            self.ini_path,
            channel_id="111222333444555666",
            token="secret-token",
        )
        self.settings = DiscordSettings(
            bot_token="secret-token",
            channel_id="111222333444555666",
            poll_interval_seconds=30,
            query_live=False,
            title="Status",
            message_id=None,
            ini_path=self.ini_path,
        )
        self.config_path = self.root / "deployer.json"
        self.config = sample_config()
        self.config["instances"] = [self.config["instances"][0]]

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @patch("ardr.integrations.discord.bot.DiscordClient")
    def test_sync_posts_new_message(self, client_cls: MagicMock) -> None:
        client = client_cls.return_value
        client.create_message.return_value = {"id": "999888777666555444"}
        message = sync_discord_status(self.config_path, self.config, self.settings)
        client.create_message.assert_called_once()
        self.assertIn("Posted Discord status embed", message)
        updated = load_settings_from_ini(self.ini_path)
        self.assertEqual(updated.message_id, "999888777666555444")

    @patch("ardr.integrations.discord.bot.DiscordClient")
    def test_sync_edits_existing_message(self, client_cls: MagicMock) -> None:
        settings = DiscordSettings(
            **{**self.settings.__dict__, "message_id": "111111111111111111"}
        )
        client = client_cls.return_value
        message = sync_discord_status(self.config_path, self.config, settings)
        client.edit_message.assert_called_once_with(
            settings.channel_id,
            settings.message_id,
            ANY,
        )
        client.create_message.assert_not_called()
        self.assertIn("Updated Discord status embed", message)

    @patch("ardr.integrations.discord.bot.DiscordClient")
    def test_sync_reposts_when_message_missing(self, client_cls: MagicMock) -> None:
        settings = DiscordSettings(
            **{**self.settings.__dict__, "message_id": "111111111111111111"}
        )
        client = client_cls.return_value
        client.edit_message.side_effect = DiscordError(404, "Unknown Message")
        client.create_message.return_value = {"id": "222222222222222222"}
        message = sync_discord_status(self.config_path, self.config, settings)
        client.create_message.assert_called_once()
        self.assertIn("Posted Discord status embed", message)
        updated = load_settings_from_ini(self.ini_path)
        self.assertEqual(updated.message_id, "222222222222222222")

    @patch("ardr.integrations.discord.bot.DiscordClient")
    def test_force_post_skips_edit(self, client_cls: MagicMock) -> None:
        settings = DiscordSettings(
            **{**self.settings.__dict__, "message_id": "111111111111111111"}
        )
        client = client_cls.return_value
        client.create_message.return_value = {"id": "333333333333333333"}
        sync_discord_status(self.config_path, self.config, settings, force_post=True)
        client.edit_message.assert_not_called()
        client.create_message.assert_called_once()


def load_settings_from_ini(ini_path: Path):
    from ardr.integrations.discord.store import load_settings

    return load_settings(ini_path)


if __name__ == "__main__":
    unittest.main()
