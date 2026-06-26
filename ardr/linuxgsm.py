from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import select_instances
from .paths import generated_dir


def linuxgsm_script(instance: dict[str, Any]) -> str:
    name = instance["name"]
    return f"""#!/usr/bin/env bash
set -euo pipefail

echo "LinuxGSM bootstrap for {name}"
echo "Recommended: run this as a dedicated non-root server user."

if [ ! -f linuxgsm.sh ]; then
  curl -Lo linuxgsm.sh https://linuxgsm.sh
  chmod +x linuxgsm.sh
fi

bash linuxgsm.sh armarserver
echo
echo "Next: ./armarserver install"
echo "Useful commands:"
echo "  ./armarserver start"
echo "  ./armarserver stop"
echo "  ./armarserver restart"
echo "  ./armarserver console"
echo "  ./armarserver update"
echo "  ./armarserver force-update"
echo "  ./armarserver validate"
echo "  ./armarserver monitor"
echo "  ./armarserver details"
echo "  ./armarserver debug"
"""


def render_linuxgsm(config_path: Path, config: dict[str, Any], instance_name: str | None) -> None:
    for instance in select_instances(config, instance_name):
        out = generated_dir(config_path, config, instance) / "linuxgsm-bootstrap.sh"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(linuxgsm_script(instance), encoding="utf-8")
        out.chmod(0o755)
        print(f"Rendered {out}")
    print_linuxgsm_notes()


def print_linuxgsm_notes() -> None:
    print()
    print("LinuxGSM is the best Linux option when you want mature monitor, console, backup, debug, and cron workflows.")
    print("Official page: https://linuxgsm.com/servers/armarserver/")
    print("Common commands: start, stop, restart, console, update, force-update, validate, monitor, details, debug, backup.")
    print("Recommended cron:")
    print("  */5 * * * * /home/armarserver/armarserver monitor > /dev/null 2>&1")
    print("  */30 * * * * /home/armarserver/armarserver update > /dev/null 2>&1")
    print("  0 0 * * 0 /home/armarserver/armarserver update-lgsm > /dev/null 2>&1")

