from __future__ import annotations

import argparse

from ..core.constants import DEFAULT_CONFIG
from .subparsers import add_basic, add_discord, add_lifecycle, add_management, add_platform, add_web


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="The friendly command-line manager for Arma Reforger dedicated servers.",
        epilog="New here? Run `reforger setup`. Day to day, `reforger`, `reforger info`, and `reforger menu` are great places to start.",
    )
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Path to deployer JSON config.")
    sub = parser.add_subparsers(dest="command")
    add_basic(sub)
    add_lifecycle(sub)
    add_platform(sub)
    add_management(sub)
    add_web(sub)
    add_discord(sub)
    return parser
