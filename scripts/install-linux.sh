#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "Reforger Linux bootstrap"

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

chmod +x "$ROOT/reforger" "$ROOT/reforger.py" "$ROOT/ardr.py"

BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR"
ln -sf "$ROOT/reforger" "$BIN_DIR/reforger"
INSTALLED_COMMAND="$BIN_DIR/reforger"

if [ -d /usr/local/bin ]; then
  if [ -w /usr/local/bin ]; then
    ln -sf "$ROOT/reforger" /usr/local/bin/reforger
    INSTALLED_COMMAND="/usr/local/bin/reforger"
  elif command -v sudo >/dev/null 2>&1; then
    sudo ln -sf "$ROOT/reforger" /usr/local/bin/reforger
    INSTALLED_COMMAND="/usr/local/bin/reforger"
  fi
fi

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) export PATH="$BIN_DIR:$PATH" ;;
esac

echo "Installed command: $INSTALLED_COMMAND"
if [ "$INSTALLED_COMMAND" = "$BIN_DIR/reforger" ]; then
  echo "Add this to your shell profile if reforger is not found in a new terminal:"
  echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

if [ ! -f "$ROOT/deployer.json" ]; then
  reforger init
fi

reforger validate
reforger render

echo
echo "Next steps:"
echo "  1. Run: reforger setup"
echo "  2. Preview deploy: reforger launch reforger-1"
echo "  3. Apply deploy: sudo reforger launch reforger-1 --apply"
echo "  4. Watch logs: reforger tail reforger-1"
