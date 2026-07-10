from __future__ import annotations

import sys


def confirm(args, question: str) -> bool:
    """Require an explicit yes for operations that can interrupt or overwrite."""
    if getattr(args, "yes", False):
        return True
    if not sys.stdin.isatty():
        print(f"Not run: {question} Re-run with --yes when running non-interactively.")
        return False
    reply = input(f"{question} [y/N]: ").strip().lower()
    return reply in {"y", "yes"}
