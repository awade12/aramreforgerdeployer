from __future__ import annotations

import argparse
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from ardr.cli import _friendly_argv, main
from ardr.cli.parser import build_parser
from ardr.config import load_config
from ardr.config.discovery import resolve_config_path
from ardr.config.commands import cmd_configure, cmd_setup
from ardr.config.io import save_config
from ardr.config.sample import sample_config
from ardr.ui.helpdesk import _find_topic, _topics, show_helpdesk
from ardr.ui.menu import _actions, _selected_action


class EasyCliTests(unittest.TestCase):
    def test_no_command_explains_how_to_start(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch("sys.argv", ["reforger", "--config", str(Path(directory) / "missing.json")]):
            output = io.StringIO()
            with redirect_stdout(output):
                main()
        self.assertIn("reforger setup", output.getvalue())
        self.assertIn("No server is set up", output.getvalue())

    def test_quickstart_alias_keeps_setup_handler(self) -> None:
        args = build_parser().parse_args(["quickstart"])
        self.assertEqual("quickstart", args.command)
        self.assertEqual("cmd_setup", args.func.__name__)

    def test_setup_creates_a_ready_default_server(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deployer.json"
            args = argparse.Namespace(config=str(path), instance=None, instance_name=None)
            with patch("builtins.input", side_effect=["Friendly Server", "admin-secret", "", "32", "", "n"]):
                with redirect_stdout(io.StringIO()):
                    cmd_setup(args)
            _, config = load_config(str(path))
        self.assertEqual("reforger-1", config["defaultInstance"])
        self.assertEqual("Friendly Server", config["instances"][0]["server"]["name"])
        self.assertEqual(32, config["instances"][0]["server"]["maxPlayers"])
        self.assertIn("port", config["instances"][0])
        self.assertIn("queryPort", config["instances"][0])

    def test_menu_keeps_everyday_actions_short(self) -> None:
        labels = [label for _, label, _ in _actions(False)]
        self.assertLessEqual(len(labels), 10)
        self.assertIn("Open selected server control room", labels)
        self.assertIn("Open the Reforger help desk", labels)
        self.assertIn("Setup and admin tools", labels)

    def test_zero_quits_menu(self) -> None:
        self.assertEqual("quit", _selected_action(_actions(False), "0")[0])

    def test_helpdesk_has_mod_update_runbook(self) -> None:
        topic = _find_topic(_topics("testingserver"), "mod-update")
        self.assertIsNotNone(topic)
        self.assertIn("reforger testingserver mod add <workshop-url>", dict(topic.commands))
        self.assertGreaterEqual(len(topic.steps), 4)

    def test_helpdesk_topic_can_be_printed_without_config(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            show_helpdesk("server-update", "testingserver")
        self.assertIn("How do I update", output.getvalue())
        self.assertIn("reforger testingserver update", output.getvalue())

    def test_helpdesk_command_and_alias_parse(self) -> None:
        args = build_parser().parse_args(["helpdesk", "mod-update", "--instance", "testingserver"])
        self.assertEqual("cmd_helpdesk", args.func.__name__)
        self.assertEqual("testingserver", args.instance)
        alias = build_parser().parse_args(["guide", "logs"])
        self.assertEqual("cmd_helpdesk", alias.func.__name__)

    def test_configure_shows_preview_and_can_cancel(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deployer.json"
            save_config(path, sample_config())
            args = argparse.Namespace(config=str(path), instance="reforger-1", instance_name=None)
            answers = ["", "", "", "", "", "", "", "Preview Name", "", "", "", "", "", "", "n"]
            output = io.StringIO()
            with patch("builtins.input", side_effect=answers), redirect_stdout(output):
                cmd_configure(args)
            _, config = load_config(str(path))
        self.assertIn("Config preview", output.getvalue())
        self.assertIn("No changes were saved", output.getvalue())
        self.assertNotEqual("Preview Name", config["instances"][0]["server"]["name"])

    def test_explicit_config_path_is_never_overridden(self) -> None:
        self.assertEqual("/tmp/custom.json", resolve_config_path("/tmp/custom.json"))

    def test_config_is_found_next_to_installed_launcher(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "aramreforgerdeployer"
            root.mkdir()
            (root / "deployer.json").write_text("{}", encoding="utf-8")
            with patch("ardr.config.discovery.Path.cwd", return_value=Path(directory) / "elsewhere"), patch("sys.argv", [str(root / "reforger")]):
                self.assertEqual(str((root / "deployer.json").resolve()), resolve_config_path(None))

    def test_server_first_shortcuts_are_translated(self) -> None:
        self.assertEqual(["hub", "testingserver"], _friendly_argv(["testingserver"]))
        self.assertEqual(["start", "testingserver"], _friendly_argv(["testingserver", "on"]))
        self.assertEqual(["logs", "testingserver", "--lines", "20"], _friendly_argv(["testingserver", "logs", "--lines", "20"]))
        self.assertEqual(["--config", "mine.json", "stop", "testingserver"], _friendly_argv(["--config", "mine.json", "testingserver", "off"]))
        self.assertEqual(["backup", "create", "testingserver"], _friendly_argv(["testingserver", "backup"]))
        self.assertEqual(
            ["workshop", "https://reforger.armaplatform.com/workshop/ABC", "testingserver", "--merge"],
            _friendly_argv(["testingserver", "mod", "add", "https://reforger.armaplatform.com/workshop/ABC"]),
        )
        self.assertEqual(["where", "testingserver"], _friendly_argv(["testingserver", "where"]))
        self.assertEqual(["edit", "testingserver"], _friendly_argv(["testingserver", "edit"]))
        self.assertEqual(["edit", "testingserver", "--raw"], _friendly_argv(["testingserver", "edit", "raw"]))
        self.assertEqual(["helpdesk", "--instance", "testingserver"], _friendly_argv(["testingserver", "helpdesk"]))
