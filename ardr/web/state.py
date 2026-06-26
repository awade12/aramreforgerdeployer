from __future__ import annotations

from pathlib import Path


class WebState:
    def __init__(self, config: str, auth_file: Path):
        self.config = config
        self.auth_file = auth_file
        self.csrf: dict[str, str] = {}
