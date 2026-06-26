from __future__ import annotations

import argparse

from .commands import (
    cmd_battleye,
    cmd_backup,
    cmd_debug,
    cmd_deploy,
    cmd_doctor,
    cmd_firewall,
    cmd_install,
    cmd_info,
    cmd_linuxgsm,
    cmd_linux_user,
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
    cmd_start,
    cmd_status,
    cmd_stop,
    cmd_systemd,
    cmd_update,
    cmd_web,
    cmd_windows_task,
)
from .config_commands import cmd_configure, cmd_init, cmd_validate
from .constants import DEFAULT_CONFIG


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deploy and manage many Arma Reforger dedicated servers.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Path to deployer JSON config.")
    sub = parser.add_subparsers(dest="command", required=True)
    add_basic(sub)
    add_lifecycle(sub)
    add_platform(sub)
    add_management(sub)
    add_web(sub)
    return parser


def add_basic(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("init", help="Create a starter deployer.json.")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)
    for name, func, help_text in [
        ("configure", cmd_configure, "Add or edit an instance with prompts."),
        ("validate", cmd_validate, "Validate deployer config."),
        ("render", cmd_render, "Render server configs and start scripts."),
        ("install", cmd_install, "Install/update server files through SteamCMD."),
        ("status", cmd_status, "Show tracked instance status."),
        ("info", cmd_info, "Show one-view instance details and useful commands."),
        ("ports", cmd_ports, "Print port and firewall guidance."),
        ("linuxgsm", cmd_linuxgsm, "Render LinuxGSM helper scripts and notes."),
        ("doctor", cmd_doctor, "Run preflight checks for this host."),
        ("menu", cmd_menu, "Open an interactive management menu."),
    ]:
        p = sub.add_parser(name, help=help_text)
        if name not in {"validate", "menu"}:
            p.add_argument("--instance")
        if name == "ports":
            p.add_argument("--fix", action="store_true", help="Assign safe ports and save instance files.")
        p.set_defaults(func=func)


def add_lifecycle(sub: argparse._SubParsersAction) -> None:
    for name, func in [("start", cmd_start), ("stop", cmd_stop), ("pause", cmd_pause), ("resume", cmd_resume), ("debug", cmd_debug)]:
        p = sub.add_parser(name, help=f"{name.capitalize()} one instance.")
        p.add_argument("--instance", required=True)
        p.set_defaults(func=func)
    add_restart(sub)
    add_update(sub)
    add_logs(sub)


def add_restart(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("restart", help="Stop then start one instance.")
    p.add_argument("--instance", required=True)
    p.add_argument("--wait", type=float, default=2.0)
    p.set_defaults(func=cmd_restart)


def add_update(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("update", help="Update server files through SteamCMD.")
    p.add_argument("--instance")
    p.add_argument("--no-restart", dest="restart", action="store_false")
    p.add_argument("--start-stopped", action="store_true")
    p.set_defaults(func=cmd_update, restart=True)


def add_logs(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("logs", help="Show latest profile log or systemd journal.")
    p.add_argument("--instance", required=True)
    p.add_argument("--lines", type=int, default=80)
    p.add_argument("--follow", action="store_true")
    p.add_argument("--systemd", action="store_true")
    p.set_defaults(func=cmd_logs)


def add_platform(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("systemd", help="Render or install Linux systemd services.")
    p.add_argument("action", choices=["render", "install"])
    p.add_argument("--instance")
    p.set_defaults(func=cmd_systemd)
    p = sub.add_parser("windows-task", help="Install or remove Windows startup Scheduled Tasks.")
    p.add_argument("action", choices=["install", "remove"])
    p.add_argument("--instance")
    p.set_defaults(func=cmd_windows_task)
    p = sub.add_parser("battleye", help="Append BattlEye RCon settings for an instance.")
    p.add_argument("--instance", required=True)
    p.add_argument("--rcon-port", type=int, required=True)
    p.add_argument("--rcon-password", required=True)
    p.set_defaults(func=cmd_battleye)
    p = sub.add_parser("linux-user", help="Prepare a non-root Linux user and deployment directory.")
    p.add_argument("--user", default="armar")
    p.add_argument("--target", default="/opt/ardr")
    p.add_argument("--apply", action="store_true", help="Execute changes. Default is dry-run.")
    p.set_defaults(func=cmd_linux_user)


def add_management(sub: argparse._SubParsersAction) -> None:
    add_service(sub)
    add_firewall(sub)
    add_backup(sub)
    add_mods(sub)
    add_query(sub)
    add_deploy(sub)


def add_service(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("service", help="Control generated systemd services.")
    p.add_argument("action", choices=["start", "stop", "restart", "status", "enable", "disable", "logs"])
    p.add_argument("--instance", required=True)
    p.add_argument("--lines", type=int, default=80)
    p.add_argument("--follow", action="store_true")
    p.set_defaults(func=cmd_service)


def add_firewall(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("firewall", help="Apply local firewall rules for instance UDP ports.")
    p.add_argument("action", choices=["apply"])
    p.add_argument("--instance")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_firewall)


def add_backup(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("backup", help="Create, list, or restore backups.")
    p.add_argument("action", choices=["create", "list", "restore"])
    p.add_argument("--instance")
    p.add_argument("--include-downloads", action="store_true")
    p.add_argument("--archive")
    p.add_argument("--target", default=".")
    p.set_defaults(func=cmd_backup)


def add_mods(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("mods", help="Add, list, or remove Reforger mods in instance config.")
    p.add_argument("action", choices=["add", "list", "remove"])
    p.add_argument("--instance", required=True)
    p.add_argument("--id")
    p.add_argument("--name", default="")
    p.add_argument("--version", default="")
    p.set_defaults(func=cmd_mods)


def add_query(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("query", help="Query live A2S server status.")
    p.add_argument("--instance", required=True)
    p.add_argument("--host")
    p.add_argument("--timeout", type=float, default=3.0)
    p.set_defaults(func=cmd_query)


def add_deploy(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("deploy", help="Run first-deploy workflow for one instance.")
    p.add_argument("--instance", required=True)
    p.add_argument("--apply", action="store_true", help="Execute changes. Default is dry-run.")
    p.set_defaults(func=cmd_deploy)


def add_web(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("web", help="Run authenticated HTMX/Tailwind dashboard.")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--password")
    p.add_argument("--auth-file", default=".ardr-web-auth.json")
    p.set_defaults(func=cmd_web)


def main() -> None:
    (args := build_parser().parse_args()).func(args)
