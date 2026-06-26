from __future__ import annotations

import argparse
from pathlib import Path

from .backup import create_backup, list_backups, restore_backup
from .firewall import apply_firewall
from .mods import add_mod, list_mods, remove_mod
from .services import control_service


def cmd_service(args: argparse.Namespace, one) -> None:
    _, _, instance = one(args, "service")
    control_service(instance, args.action, args.lines, args.follow)


def cmd_firewall(args: argparse.Namespace, load_with_ports) -> None:
    _, config = load_with_ports(args)
    apply_firewall(config, args.instance, args.dry_run)


def cmd_backup(args: argparse.Namespace, load_with_ports) -> None:
    config_path, config = load_with_ports(args)
    if args.action == "create":
        create_backup(config_path, config, args.instance, args.include_downloads)
    elif args.action == "list":
        list_backups(config_path, config)
    elif args.action == "restore":
        if not args.archive:
            raise SystemExit("backup restore requires --archive")
        restore_backup(Path(args.archive), Path(args.target))


def cmd_mods(args: argparse.Namespace, load_with_ports) -> None:
    config_path, config = load_with_ports(args)
    if args.action == "add":
        if not args.id:
            raise SystemExit("mods add requires --id")
        add_mod(config_path, config, args.instance, args.id, args.name, args.version)
    elif args.action == "list":
        list_mods(config, args.instance)
    elif args.action == "remove":
        if not args.id:
            raise SystemExit("mods remove requires --id")
        remove_mod(config_path, config, args.instance, args.id)

