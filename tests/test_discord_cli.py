from __future__ import annotations

import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ardr.cli.parser import build_parser
from ardr.commands.handlers import cmd_discord


class DiscordCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.ini_path = self.root / "discord.ini"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_parser_has_discord_actions(self) -> None:
        parser = build_parser()
        args = parser.parse_args(["discord", "status", "--ini", str(self.ini_path)])
        self.assertEqual(args.action, "status")
        self.assertEqual(args.ini, str(self.ini_path))

    def test_cmd_discord_status_missing_config(self) -> None:
        args = build_parser().parse_args(["discord", "status", "--ini", str(self.ini_path)])
        buffer = io.StringIO()
        with patch("sys.stdout", buffer):
            cmd_discord(args)
        self.assertIn("not configured", buffer.getvalue())

    def test_cmd_discord_configure(self) -> None:
        args = build_parser().parse_args(
            [
                "discord",
                "configure",
                "--ini",
                str(self.ini_path),
                "--channel-id",
                "123456789",
                "--token",
                "secret",
                "--title",
                "Ops Board",
            ]
        )
        buffer = io.StringIO()
        with patch("sys.stdout", buffer):
            cmd_discord(args)
        self.assertTrue(self.ini_path.exists())
        self.assertIn("Saved Discord config", buffer.getvalue())
        self.assertIn("channel_id: 123456789", buffer.getvalue())

    def test_entrypoint_help(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, str(repo / "reforger.py"), "discord", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("configure", result.stdout)
        self.assertIn("sync", result.stdout)


if __name__ == "__main__":
    unittest.main()
