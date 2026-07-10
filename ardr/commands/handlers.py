from __future__ import annotations

import argparse
from pathlib import Path

from ..config import load_config, normalize_config_ports, save_config, select_instances
from ..core.terminal import heading, table
from ..platform.doctor import run_doctor
from ..platform.linux_setup import setup_linux_user
from ..platform.linuxgsm import render_linuxgsm
from ..platform.services import manage_windows_task, render_systemd
from ..deploy.backup import create_backup
from ..server.battleye import append_rcon
from ..server.info import show_info
from ..server.invite import print_invite
from ..server.ops import install_instances, show_ports, update_instances
from ..server.resources import show_resources
from ..server.render import render_instances
from ..server.status import status_row
from ..ui.menu import interactive_loop
from ..ui.hub import server_hub
from ..integrations.discord import (
    configure_discord,
    resolve_ini_path,
    serve_discord,
    show_discord_status,
    sync_discord_status,
    load_settings,
)
from ..web import serve_web
from .helpers import load_with_ports, many_instance_name, one_instance, print_validation
from .management import cmd_backup as run_backup
from .management import cmd_deploy as run_deploy
from .management import cmd_firewall as run_firewall
from .management import cmd_mods as run_mods
from .management import cmd_query as run_query
from .management import cmd_service as run_service
from .workshop import cmd_workshop as run_workshop


def cmd_render(args: argparse.Namespace) -> None:
    config_path, config = load_with_ports(args)
    render_instances(config_path, config, many_instance_name(args))


def cmd_install(args: argparse.Namespace) -> None:
    config_path, config = load_with_ports(args)
    install_instances(config_path, config, many_instance_name(args))


def cmd_update(args: argparse.Namespace) -> None:
    config_path, config = load_with_ports(args)
    target = many_instance_name(args)
    from ..ui.prompts import confirm

    label = target or "all configured servers"
    if not confirm(args, f"Update {label}? It may briefly restart a running server."):
        print("Update cancelled.")
        return
    if not getattr(args, "no_backup", False):
        print("Creating a safety backup before updating…")
        create_backup(config_path, config, target, False)
    update_instances(config_path, config, target, args.restart, args.start_stopped)


def cmd_status(args: argparse.Namespace) -> None:
    config_path, config = load_with_ports(args)
    targets = select_instances(config, many_instance_name(args))
    heading("Status", f"{len(targets)} server{'s' if len(targets) != 1 else ''}")
    table(
        ["Server", "State", "Details", "Systemd"],
        [list(status_row(config_path, config, instance)) for instance in targets],
    )


def cmd_info(args: argparse.Namespace) -> None:
    config_path, config, instance = one_instance(args, "info")
    show_info(config_path, config, instance)


def cmd_resources(args: argparse.Namespace) -> None:
    config_path, config, instance = one_instance(args, "resources")
    show_resources(config_path, config, instance, float(args.watch))


def cmd_invite(args: argparse.Namespace) -> None:
    _, _, instance = one_instance(args, "invite")
    print_invite(instance)


def cmd_export(args: argparse.Namespace) -> None:
    from ..config.transfer import export_instance

    export_instance(args.config, args.instance_name or args.instance, args.output)


def cmd_import(args: argparse.Namespace) -> None:
    from ..config.transfer import import_instance

    import_instance(args.config, args.source, args.new_name)


def cmd_query(args: argparse.Namespace) -> None:
    run_query(args, one_instance)


def cmd_ports(args: argparse.Namespace) -> None:
    path, config = load_config(args.config)
    changed = normalize_config_ports(config)
    if getattr(args, "fix", False):
        save_config(path, config)
        print("Ports checked and saved." if changed else "Ports already safe.")
    elif changed:
        print("WARNING: missing or colliding ports detected. Run `reforger ports --fix` to save safe ports.")
    show_ports(config, many_instance_name(args))


def cmd_systemd(args: argparse.Namespace) -> None:
    render_systemd(*load_with_ports(args), many_instance_name(args), args.action == "install")


def cmd_service(args: argparse.Namespace) -> None:
    run_service(args, one_instance)


def cmd_firewall(args: argparse.Namespace) -> None:
    run_firewall(args, load_with_ports)


def cmd_backup(args: argparse.Namespace) -> None:
    run_backup(args, load_with_ports)


def cmd_mods(args: argparse.Namespace) -> None:
    run_mods(args, load_with_ports)


def cmd_windows_task(args: argparse.Namespace) -> None:
    manage_windows_task(*load_with_ports(args), many_instance_name(args), args.action == "install")


def cmd_battleye(args: argparse.Namespace) -> None:
    append_rcon(*one_instance(args, "battleye"), args.rcon_port, args.rcon_password)


def cmd_linuxgsm(args: argparse.Namespace) -> None:
    render_linuxgsm(*load_with_ports(args), args.instance)


def cmd_menu(args: argparse.Namespace) -> None:
    from .registry import dispatch_table

    interactive_loop(args, dispatch_table())


def cmd_hub(args: argparse.Namespace) -> None:
    from .registry import dispatch_table

    server_hub(args, dispatch_table())


def cmd_completion(args: argparse.Namespace) -> None:
    from ..cli.completion import cmd_completion as run_completion

    run_completion(args)


def cmd_doctor(args: argparse.Namespace) -> None:
    config_path, config = load_with_ports(args)
    failures = run_doctor(config_path, config)
    if failures:
        raise SystemExit(1)


def cmd_linux_user(args: argparse.Namespace) -> None:
    setup_linux_user(args.user, args.target, Path.cwd(), args.apply)


def cmd_deploy(args: argparse.Namespace) -> None:
    run_deploy(args, one_instance)


def cmd_check(args: argparse.Namespace) -> None:
    config_path, config = load_with_ports(args)
    print_validation(config)
    show_ports(config, many_instance_name(args))
    failures = run_doctor(config_path, config)
    if failures:
        raise SystemExit(1)
    print("Ready.")


def cmd_fix(args: argparse.Namespace) -> None:
    config_path, config = load_config(args.config)
    changed = normalize_config_ports(config)
    save_config(config_path, config)
    print("Ports fixed and saved." if changed else "Ports already safe.")
    print_validation(config)
    failures = run_doctor(config_path, config)
    if failures:
        raise SystemExit(1)
    print("No fixable issues found.")


def cmd_setup(args: argparse.Namespace) -> None:
    from ..config.commands import cmd_setup

    cmd_setup(args)


def cmd_web(args: argparse.Namespace) -> None:
    serve_web(args.config, args.host, args.port, args.password, args.auth_file)


def cmd_discord(args: argparse.Namespace) -> None:
    ini_path = resolve_ini_path(args.ini)
    if args.action == "configure":
        path = configure_discord(
            ini_path,
            channel_id=args.channel_id,
            token=args.token,
            interval=args.interval,
            title=args.title,
        )
        print(f"Saved Discord config to {path} (mode 600).")
        show_discord_status(path)
        return
    if args.action == "status":
        show_discord_status(ini_path)
        return
    config_path, config = load_config(args.config)
    settings = load_settings(ini_path, channel_id=args.channel_id, interval=args.interval)
    if args.action == "start":
        serve_discord(args.config, ini_path, args.interval)
        return
    message = sync_discord_status(
        config_path,
        config,
        settings,
        force_post=args.action == "post",
    )
    print(message)


def cmd_workshop(args: argparse.Namespace) -> None:
    run_workshop(args, load_with_ports)
