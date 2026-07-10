from __future__ import annotations

import io
import contextlib
from argparse import Namespace

from ..config import load_config, normalize_config_ports, save_config, select_instances
from ..deploy.backup import create_backup
from ..server.render import render_instances
from ..server.status import print_status
from .state import WebState


def run_action(action: str, instance_name: str, state: WebState) -> None:
    from ..commands.handlers import cmd_check, cmd_doctor, cmd_install, cmd_logs, cmd_ports, cmd_update
    from ..commands.management import cmd_query
    from ..commands.lifecycle import cmd_pause, cmd_resume, cmd_start, cmd_stop, cmd_restart

    config_path, config = load_config(state.config)
    if normalize_config_ports(config):
        save_config(config_path, config)
    instance = select_instances(config, instance_name)[0]
    # A click is the web dashboard's explicit confirmation for these actions.
    args = Namespace(config=state.config, instance=instance_name, instance_name=instance_name, yes=True, no_backup=False)
    if action == "start":
        cmd_start(args)
    elif action == "stop":
        cmd_stop(args)
    elif action == "restart":
        args.wait = 2.0
        cmd_restart(args)
    elif action == "pause":
        cmd_pause(args)
    elif action == "resume":
        cmd_resume(args)
    elif action == "install":
        cmd_install(args)
    elif action == "update":
        args.restart = True
        args.start_stopped = False
        cmd_update(args)
    elif action == "check":
        cmd_check(args)
    elif action == "doctor":
        cmd_doctor(args)
    elif action == "ports":
        args.fix = False
        cmd_ports(args)
    elif action == "backup":
        create_backup(config_path, config, instance_name, False)
    elif action == "render":
        render_instances(config_path, config, instance_name)
    elif action == "query":
        args = type("Args", (), {"instance": instance_name, "host": None, "timeout": 2.0})()
        cmd_query(args, lambda *_: (config_path, config, instance))
    elif action == "logs":
        args.lines = 80
        args.follow = False
        args.systemd = False
        cmd_logs(args)
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
