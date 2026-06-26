#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "== compile =="
python3 -m compileall -q ardr

echo "== imports =="
python3 <<'PY'
import importlib
import pkgutil

for mod in pkgutil.walk_packages(["ardr"], prefix="ardr."):
    importlib.import_module(mod.name)

from ardr.commands import (
    cmd_backup,
    cmd_battleye,
    cmd_check,
    cmd_debug,
    cmd_deploy,
    cmd_doctor,
    cmd_firewall,
    cmd_fix,
    cmd_info,
    cmd_install,
    cmd_linux_user,
    cmd_linuxgsm,
    cmd_logs,
    cmd_menu,
    cmd_mods,
    cmd_pause,
    cmd_ports,
    cmd_query,
    cmd_render,
    cmd_restart,
    cmd_resume,
    cmd_service,
    cmd_setup,
    cmd_start,
    cmd_status,
    cmd_stop,
    cmd_systemd,
    cmd_update,
    cmd_web,
    cmd_windows_task,
)
from ardr.config.commands import cmd_configure, cmd_default, cmd_init, cmd_validate
from ardr.commands.registry import dispatch_table

for name, func in dispatch_table().items():
    if not callable(func):
        raise SystemExit(f"dispatch entry not callable: {name}")

print("smoke imports ok")
PY

echo "== cli =="
if [ ! -f deployer.json ]; then
  python3 ardr.py init --force >/dev/null
fi

run_cmd() {
  python3 ardr.py --config deployer.json "$@" >/dev/null || test $? -eq 1
}

run_cmd validate
run_cmd status
run_cmd status reforger-1
run_cmd ports
run_cmd doctor
run_cmd default
run_cmd backup list
run_cmd mods list reforger-1
run_cmd render reforger-1
run_cmd info reforger-1
run_cmd deploy reforger-1
run_cmd firewall apply --dry-run
run_cmd systemd render

python3 ardr.py validate
python3 ardr.py status
python3 ardr.py status reforger-1

echo "All smoke checks passed."
