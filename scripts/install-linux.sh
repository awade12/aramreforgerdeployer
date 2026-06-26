#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "ARDR Linux bootstrap"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required. Install it with your package manager, then rerun this script." >&2
  exit 1
fi

if ! command -v steamcmd >/dev/null 2>&1; then
  echo "SteamCMD was not found."
  if command -v apt-get >/dev/null 2>&1; then
    echo "Installing SteamCMD with apt. You may be asked to accept Steam license prompts."
    sudo dpkg --add-architecture i386 || true
    sudo apt-get update
    sudo apt-get install -y steamcmd lib32gcc-s1 ca-certificates
  else
    echo "Install SteamCMD using https://developer.valvesoftware.com/wiki/SteamCMD, then rerun this script." >&2
    exit 1
  fi
fi

chmod +x "$ROOT/ardr.py"

if [ ! -f "$ROOT/deployer.json" ]; then
  "$ROOT/ardr.py" init
fi

"$ROOT/ardr.py" validate
"$ROOT/ardr.py" render

echo
echo "Next steps:"
echo "  1. Edit $ROOT/deployer.json for names, admin password, ports, and scenarios."
echo "  2. Run: $ROOT/ardr.py install"
echo "  3. Run one server: $ROOT/ardr.py start --instance reforger-1"
echo "  4. Show firewall rules: $ROOT/ardr.py ports"

