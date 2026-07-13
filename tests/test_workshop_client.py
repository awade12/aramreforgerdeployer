from __future__ import annotations

import unittest
from unittest.mock import patch

from ardr.workshop.client import WorkshopMod, fetch_workshop_bundle


class WorkshopClientTests(unittest.TestCase):
    def test_plain_mod_without_scenario_can_be_added(self) -> None:
        asset = {
            "name": "Utility Mod",
            "currentVersionNumber": "1.2.3",
            "updatedAt": "2026-07-13",
            "summary": "No scenario of its own",
            "scenarios": [],
        }
        resolved = [WorkshopMod("ABCDEF0123456789", "Utility Mod", "1.2.3")]
        with patch("ardr.workshop.client._fetch_asset", return_value=asset), patch(
            "ardr.workshop.client._resolve_mod_tree", return_value=resolved
        ):
            bundle = fetch_workshop_bundle("ABCDEF0123456789")
        self.assertIsNone(bundle.scenario)
        self.assertEqual((), bundle.scenarios)
        self.assertEqual("Utility Mod", bundle.mods[0].name)

    def test_plain_mod_rejects_nonzero_scenario_choice(self) -> None:
        asset = {"name": "Utility Mod", "scenarios": []}
        with patch("ardr.workshop.client._fetch_asset", return_value=asset):
            with self.assertRaisesRegex(SystemExit, "has no scenarios"):
                fetch_workshop_bundle("ABCDEF0123456789", 1)


if __name__ == "__main__":
    unittest.main()
