from __future__ import annotations

import argparse
from pathlib import Path

from ..config import resolve_instance_name
from ..deploy.backup import backup_archives, create_backup, list_backups, restore_backup
from ..deploy.workflow import deploy_instance
from ..platform.firewall import apply_firewall
from ..platform.services import control_service
from ..server.mods import add_mod, list_mods, remove_mod
from ..server.query import query_server
from ..ui.prompts import confirm


def cmd_service(args: argparse.Namespace, one) -> None:
    _, _, instance = one(args, "service")
    control_service(instance, args.action, args.lines, args.follow)


def cmd_firewall(args: argparse.Namespace, load_with_ports) -> None:
    _, config = load_with_ports(args)
    if not args.dry_run and not confirm(args, "Apply firewall changes?"):
        print("Firewall changes cancelled.")
        return
    apply_firewall(config, args.instance, args.dry_run)


def cmd_backup(args: argparse.Namespace, load_with_ports) -> None:
    config_path, config = load_with_ports(args)
    instance_name = _arg_instance(args)
    if args.action == "create":
        create_backup(config_path, config, instance_name, args.include_downloads)
    elif args.action == "list":
        list_backups(config_path, config)
    elif args.action == "restore":
        archive = Path(args.archive) if args.archive else _choose_backup(config_path, config)
        if not confirm(args, f"Restore {archive.name} into {args.target}? Existing files may be overwritten."):
            print("Restore cancelled.")
            return
        restore_backup(archive, Path(args.target))


def cmd_mods(args: argparse.Namespace, load_with_ports) -> None:
    config_path, config = load_with_ports(args)
    instance_name = resolve_instance_name(config, _arg_instance(args), "mods")
    if args.action == "add":
        if not args.id:
            raise SystemExit("mods add requires --id")
        add_mod(config_path, config, instance_name, args.id, args.name, args.version)
    elif args.action == "list":
        list_mods(config, instance_name)
    elif args.action == "remove":
        if not args.id:
            raise SystemExit("mods remove requires --id")
        remove_mod(config_path, config, instance_name, args.id)


def cmd_query(args: argparse.Namespace, one) -> None:
    _, _, instance = one(args, "query")
    host = args.host or instance.get("server", {}).get("publicAddress") or "127.0.0.1"
    query_server(instance, host, args.timeout)


def cmd_deploy(args: argparse.Namespace, one) -> None:
    config_path, config, instance = one(args, "deploy")
    deploy_instance(config_path, config, instance, args.apply)


def _arg_instance(args: argparse.Namespace) -> str | None:
    return getattr(args, "instance", None) or getattr(args, "instance_name", None)


def _choose_backup(config_path: Path, config: dict) -> Path:
    archives = backup_archives(config_path, config)
    if not archives:
        raise SystemExit("No backups found. Create one first with `reforger backup create`.")
    print("Choose a backup to restore:")
    for index, archive in enumerate(archives, start=1):
        print(f"  {index}. {archive.name}")
    while True:
        try:
            return archives[int(input("Backup number: ").strip()) - 1]
        except (ValueError, IndexError):
            print("Choose one of the listed numbers.")
