from __future__ import annotations

import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from ardr.config.sample import sample_config
from ardr.integrations.discord.api import DiscordClient, DiscordError
from ardr.integrations.discord.embeds import build_status_payload
from ardr.integrations.discord.store import DiscordSettings


class DiscordEmbedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.tempdir.name) / "deployer.json"
        self.config = sample_config()
        self.config["instances"] = [self.config["instances"][0]]
        self.settings = DiscordSettings(
            bot_token="token",
            channel_id="123",
            poll_interval_seconds=30,
            query_live=False,
            title="Fleet Status",
            message_id=None,
            ini_path=Path(self.tempdir.name) / "discord.ini",
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_build_status_payload_shape(self) -> None:
        payload = build_status_payload(self.config_path, self.config, self.config["instances"], self.settings)
        self.assertIn("embeds", payload)
        embed = payload["embeds"][0]
        self.assertEqual(embed["title"], "Fleet Status")
        self.assertIn("0/1 online", embed["description"])
        self.assertEqual(len(embed["fields"]), 1)
        field = embed["fields"][0]
        self.assertIn("Offline", field["value"])
        self.assertIn("2001", field["value"])
        self.assertEqual(embed["footer"]["text"], "Reforger Deployer")


class DiscordApiTests(unittest.TestCase):
    @patch("ardr.integrations.discord.api.urllib.request.urlopen")
    def test_create_message_uses_bot_authorization(self, urlopen) -> None:
        response = BytesIO(json.dumps({"id": "1"}).encode("utf-8"))
        urlopen.return_value.__enter__.return_value = response
        client = DiscordClient("abc123")
        result = client.create_message("999", {"content": "hello"})
        self.assertEqual(result["id"], "1")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bot abc123")
        self.assertEqual(request.get_method(), "POST")

    @patch("ardr.integrations.discord.api.urllib.request.urlopen")
    def test_edit_message_uses_patch(self, urlopen) -> None:
        response = BytesIO(json.dumps({"id": "1"}).encode("utf-8"))
        urlopen.return_value.__enter__.return_value = response
        client = DiscordClient("abc123")
        client.edit_message("999", "1", {"embeds": []})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "PATCH")
        self.assertIn("/messages/1", request.full_url)

    @patch("ardr.integrations.discord.api.urllib.request.urlopen")
    def test_http_error_raises_discord_error(self, urlopen) -> None:
        import urllib.error

        urlopen.side_effect = urllib.error.HTTPError(
            url="https://discord.com/api/v10/channels/1/messages",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=BytesIO(b'{"message":"missing permissions"}'),
        )
        client = DiscordClient("abc123")
        with self.assertRaises(DiscordError) as ctx:
            client.create_message("1", {"content": "hello"})
        self.assertEqual(ctx.exception.status, 403)


if __name__ == "__main__":
    unittest.main()
