from __future__ import annotations

import argparse
from pathlib import Path

from .battleye import append_rcon
from .config import load_config, normalize_config_ports, save_config, select_instances
from .doctor import run_doctor
from .info import show_info
from .linux_setup import setup_linux_user
from .linuxgsm import render_linuxgsm
from .management_commands import cmd_backup as run_backup
from .management_commands import cmd_firewall as run_firewall
from .management_commands import cmd_mods as run_mods
from .management_commands import cmd_query as run_query
from .management_commands import cmd_service as run_service
from .management_commands import cmd_deploy as run_deploy
from .menu import interactive_loop
from .ops import install_instances, restart_instance, show_logs, show_ports, update_instances
from .processes import pause_instance, resume_instance, start_instance, stop_instance
from .render import render_instances
from .services import manage_windows_task, render_systemd
from .status import print_status
from .web import serve_web

def cmd_render(args: argparse.Namespace) -> None:
    config_path, config = _load_with_ports(args)
    render_instances(config_path, config, args.instance)


def cmd_install(args: argparse.Namespace) -> None:
    config_path, config = _load_with_ports(args)
    install_instances(config_path, config, args.instance)


def cmd_update(args: argparse.Namespace) -> None:
    config_path, config = _load_with_ports(args)
    update_instances(config_path, config, args.instance, args.restart, args.start_stopped)


def cmd_start(args: argparse.Namespace) -> None:
    config_path, config, instance = _one(args, "start")
    render_instances(config_path, config, args.instance)
    start_instance(config_path, config, instance)


def cmd_stop(args: argparse.Namespace) -> None:
    stop_instance(*_one(args, "stop"))


def cmd_restart(args: argparse.Namespace) -> None:
    restart_instance(*_one(args, "restart"), float(args.wait))


def cmd_pause(args: argparse.Namespace) -> None:
    pause_instance(*_one(args, "pause"))


def cmd_resume(args: argparse.Namespace) -> None:
    resume_instance(*_one(args, "resume"))


def cmd_debug(args: argparse.Namespace) -> None:
    config_path, config, instance = _one(args, "debug")
    render_instances(config_path, config, args.instance)
    start_instance(config_path, config, instance, foreground=True)


def cmd_status(args: argparse.Namespace) -> None:
    config_path, config = _load_with_ports(args)
    for instance in select_instances(config, args.instance):
        print_status(config_path, config, instance)


def cmd_info(args: argparse.Namespace) -> None:
    config_path, config, instance = _one(args, "info")
    show_info(config_path, config, instance)


def cmd_query(args: argparse.Namespace) -> None:
    run_query(args, _one)


def cmd_logs(args: argparse.Namespace) -> None:
    show_logs(*_one(args, "logs"), args.lines, args.follow, args.systemd)


def cmd_ports(args: argparse.Namespace) -> None:
    path, config = load_config(args.config)
    changed = normalize_config_ports(config)
    if getattr(args, "fix", False):
        save_config(path, config)
        print("Ports checked and saved." if changed else "Ports already safe.")
    elif changed:
        print("WARNING: missing or colliding ports detected. Run `ardr.py ports --fix` to save safe ports.")
    show_ports(config, args.instance)

def cmd_systemd(args: argparse.Namespace) -> None:
    render_systemd(*_load_with_ports(args), args.instance, args.action == "install")


def cmd_service(args: argparse.Namespace) -> None:
    run_service(args, _one)

def cmd_firewall(args: argparse.Namespace) -> None:
    run_firewall(args, _load_with_ports)

def cmd_backup(args: argparse.Namespace) -> None:
    run_backup(args, _load_with_ports)

def cmd_mods(args: argparse.Namespace) -> None:
    run_mods(args, _load_with_ports)


def cmd_windows_task(args: argparse.Namespace) -> None:
    manage_windows_task(*_load_with_ports(args), args.instance, args.action == "install")


def cmd_battleye(args: argparse.Namespace) -> None:
    append_rcon(*_one(args, "battleye"), args.rcon_port, args.rcon_password)

def cmd_linuxgsm(args: argparse.Namespace) -> None:
    render_linuxgsm(*_load_with_ports(args), args.instance)

def cmd_menu(args: argparse.Namespace) -> None:
    from .command_registry import dispatch_table
    interactive_loop(args, dispatch_table())


def cmd_doctor(args: argparse.Namespace) -> None:
    config_path, config = _load_with_ports(args)
    failures = run_doctor(config_path, config)
    if failures:
        raise SystemExit(1)


def cmd_linux_user(args: argparse.Namespace) -> None:
    setup_linux_user(args.user, args.target, Path.cwd(), args.apply)


def cmd_deploy(args: argparse.Namespace) -> None:
    run_deploy(args, _one)


def cmd_web(args: argparse.Namespace) -> None:
    serve_web(args.config, args.host, args.port, args.password, args.auth_file)


def _one(args: argparse.Namespace, command: str) -> tuple[Path, dict, dict]:
    if not args.instance:
        raise SystemExit(f"{command} requires --instance")
    cfg_path, config = _load_with_ports(args)
    return cfg_path, config, select_instances(config, args.instance)[0]


def _load_with_ports(args: argparse.Namespace) -> tuple[Path, dict]:
    config_path, config = load_config(args.config)
    if normalize_config_ports(config):
        save_config(config_path, config)
    return config_path, config
