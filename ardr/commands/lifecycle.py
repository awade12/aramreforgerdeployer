from __future__ import annotations

import argparse

from ..platform.services import control_service, service_available
from ..server.ops import restart_instance, show_logs
from ..server.processes import pause_instance, resume_instance, start_instance, stop_instance
from ..server.render import render_instances
from ..ui.prompts import confirm
from .helpers import load_with_ports, one_instance


def cmd_start(args: argparse.Namespace) -> None:
    config_path, config, instance = one_instance(args, "start")
    if service_available(instance):
        control_service(instance, "start")
        return
    render_instances(config_path, config, instance["name"])
    start_instance(config_path, config, instance)


def cmd_stop(args: argparse.Namespace) -> None:
    config_path, config, instance = one_instance(args, "stop")
    if not confirm(args, f"Stop {instance['name']}? Connected players will be disconnected."):
        print("Stop cancelled.")
        return
    if service_available(instance):
        control_service(instance, "stop")
        return
    stop_instance(config_path, config, instance)


def cmd_restart(args: argparse.Namespace) -> None:
    config_path, config, instance = one_instance(args, "restart")
    if not confirm(args, f"Restart {instance['name']}? Connected players will be disconnected."):
        print("Restart cancelled.")
        return
    if service_available(instance):
        control_service(instance, "restart")
        return
    restart_instance(config_path, config, instance, float(args.wait))


def cmd_pause(args: argparse.Namespace) -> None:
    pause_instance(*one_instance(args, "pause"))


def cmd_resume(args: argparse.Namespace) -> None:
    resume_instance(*one_instance(args, "resume"))


def cmd_debug(args: argparse.Namespace) -> None:
    config_path, config, instance = one_instance(args, "debug")
    render_instances(config_path, config, instance["name"])
    start_instance(config_path, config, instance, foreground=True)


def cmd_logs(args: argparse.Namespace) -> None:
    config_path, config, instance = one_instance(args, "logs")
    if args.systemd or service_available(instance):
        control_service(instance, "logs", args.lines, args.follow)
        return
    show_logs(config_path, config, instance, args.lines, args.follow, False)
