from __future__ import annotations

import io
import contextlib

from ..config import load_config, normalize_config_ports, save_config, select_instances
from ..deploy.backup import create_backup
from ..platform.services import control_service
from ..server.render import render_instances
from ..server.status import print_status
from .state import WebState


def run_action(action: str, instance_name: str, state: WebState) -> None:
    from ..commands.management import cmd_query

    config_path, config = load_config(state.config)
    if normalize_config_ports(config):
        save_config(config_path, config)
    instance = select_instances(config, instance_name)[0]
    if action in {"start", "stop", "restart"}:
        control_service(instance, action)
    elif action == "backup":
        create_backup(config_path, config, instance_name, False)
    elif action == "render":
        render_instances(config_path, config, instance_name)
    elif action == "query":
        args = type("Args", (), {"instance": instance_name, "host": None, "timeout": 2.0})()
        cmd_query(args, lambda *_: (config_path, config, instance))
    elif action == "logs":
        control_service(instance, "logs", lines=80, follow=False)
    elif action == "status":
        print_status(config_path, config, instance)
    else:
        print(f"Unknown action: {action}")


def capture_output(fn) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            fn()
        except BaseException as exc:
            print(f"ERROR: {exc}")
    return buf.getvalue()
