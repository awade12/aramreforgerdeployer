from __future__ import annotations

import argparse

from ..core.constants import DEFAULT_CONFIG
from .subparsers import add_basic, add_discord, add_lifecycle, add_management, add_platform, add_web


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deploy and manage many Arma Reforger dedicated servers.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Path to deployer JSON config.")
    sub = parser.add_subparsers(dest="command", required=True)
    add_basic(sub)
    add_lifecycle(sub)
    add_platform(sub)
    add_management(sub)
    add_web(sub)
    add_discord(sub)
    return parser
