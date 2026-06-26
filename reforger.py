#!/usr/bin/env python3
"""Windows-friendly launcher for the Reforger server command line."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ardr.cli import main


if __name__ == "__main__":
    main()
