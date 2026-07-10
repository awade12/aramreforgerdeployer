from __future__ import annotations

import argparse

from ..commands import (
    cmd_battleye,
    cmd_backup,
    cmd_check,
    cmd_debug,
    cmd_deploy,
    cmd_discord,
    cmd_doctor,
    cmd_firewall,
    cmd_fix,
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
    cmd_setup,
    cmd_start,
    cmd_status,
    cmd_stop,
    cmd_systemd,
    cmd_update,
    cmd_web,
    cmd_windows_task,
    cmd_workshop,
)
from ..config.commands import cmd_configure, cmd_default, cmd_init, cmd_validate


def add_basic(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("init", help="Create a starter deployer.json.")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)
    p = sub.add_parser("default", help="Show or set the default server.")
    p.add_argument("instance_name", nargs="?")
    p.set_defaults(func=cmd_default)
    p = sub.add_parser("setup", aliases=["quickstart"], help="Easy first-time setup with only the important questions.")
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.set_defaults(func=cmd_setup)
    p = sub.add_parser("check", help="Validate config, show ports, and run doctor.")
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.set_defaults(func=cmd_check)
    p = sub.add_parser("fix", help="Fix safe ports, validate config, and run doctor.")
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.set_defaults(func=cmd_fix)
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
            p.add_argument("instance_name", nargs="?")
            p.add_argument("--instance")
        if name == "ports":
            p.add_argument("--fix", action="store_true", help="Assign safe ports and save instance files.")
        p.set_defaults(func=func)


def add_lifecycle(sub: argparse._SubParsersAction) -> None:
    for name, func in [
        ("start", cmd_start),
        ("up", cmd_start),
        ("stop", cmd_stop),
        ("down", cmd_stop),
        ("pause", cmd_pause),
        ("resume", cmd_resume),
        ("debug", cmd_debug),
    ]:
        help_text = {
            "up": "Start one instance.",
            "down": "Stop one instance.",
        }.get(name, f"{name.capitalize()} one instance.")
        p = sub.add_parser(name, help=help_text)
        p.add_argument("instance_name", nargs="?")
        p.add_argument("--instance")
        p.set_defaults(func=func)
    add_restart(sub)
    add_update(sub)
    add_logs(sub)


def add_restart(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("restart", help="Stop then start one instance.")
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.add_argument("--wait", type=float, default=2.0)
    p.set_defaults(func=cmd_restart)
    p = sub.add_parser("reload", help="Restart one instance.")
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.add_argument("--wait", type=float, default=2.0)
    p.set_defaults(func=cmd_restart)


def add_update(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("update", help="Update server files through SteamCMD.")
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.add_argument("--no-restart", dest="restart", action="store_false")
    p.add_argument("--start-stopped", action="store_true")
    p.set_defaults(func=cmd_update, restart=True)


def add_logs(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("logs", help="Show latest profile log or systemd journal.")
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.add_argument("--lines", type=int, default=80)
    p.add_argument("-f", "--follow", action="store_true")
    p.add_argument("--systemd", action="store_true")
    p.set_defaults(func=cmd_logs)
    p = sub.add_parser("tail", help="Follow server logs.")
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.add_argument("--lines", type=int, default=80)
    p.add_argument("--systemd", action="store_true")
    p.set_defaults(func=cmd_logs, follow=True)


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
    add_workshop(sub)


def add_workshop(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "workshop",
        help="Apply scenario ID and dependency mods from a Reforger workshop URL.",
    )
    p.add_argument("url", help="Workshop URL or 16-character mod ID.")
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.add_argument("--scenario", type=int, default=0, help="Scenario index when a mod has multiple scenarios.")
    p.add_argument("--dry-run", action="store_true", help="Show scenario and mods without saving.")
    p.add_argument("--merge", action="store_true", help="Merge mods instead of replacing the mods list.")
    p.add_argument("--set-name", action="store_true", help="Set server.name to the selected scenario name.")
    p.set_defaults(func=cmd_workshop)


def add_service(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("service", help="Control generated systemd services.")
    p.add_argument("action", choices=["start", "stop", "restart", "status", "enable", "disable", "logs"])
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.add_argument("--lines", type=int, default=80)
    p.add_argument("-f", "--follow", action="store_true")
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
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.add_argument("--include-downloads", action="store_true")
    p.add_argument("--archive")
    p.add_argument("--target", default=".")
    p.set_defaults(func=cmd_backup)


def add_mods(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("mods", help="Add, list, or remove Reforger mods in instance config.")
    p.add_argument("action", choices=["add", "list", "remove"])
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.add_argument("--id")
    p.add_argument("--name", default="")
    p.add_argument("--version", default="")
    p.set_defaults(func=cmd_mods)


def add_query(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("query", help="Query live A2S server status.")
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.add_argument("--host")
    p.add_argument("--timeout", type=float, default=3.0)
    p.set_defaults(func=cmd_query)


def add_deploy(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("deploy", help="Run first-deploy workflow for one instance.")
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.add_argument("--apply", action="store_true", help="Execute changes. Default is dry-run.")
    p.set_defaults(func=cmd_deploy)
    p = sub.add_parser("launch", help="Preview or run first-deploy workflow for one instance.")
    p.add_argument("instance_name", nargs="?")
    p.add_argument("--instance")
    p.add_argument("--apply", action="store_true", help="Execute changes. Default is dry-run.")
    p.set_defaults(func=cmd_deploy)


def add_web(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("web", help="Run authenticated HTMX/Tailwind dashboard.")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--password")
    p.add_argument("--auth-file", default=".ardr-web-auth.json")
    p.set_defaults(func=cmd_web)

    p = sub.add_parser("open", help="Run the web dashboard.")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--password")
    p.add_argument("--auth-file", default=".ardr-web-auth.json")
    p.set_defaults(func=cmd_web)


def add_discord(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("discord", help="Post or update a live Discord status embed.")
    p.add_argument(
        "action",
        choices=["configure", "status", "start", "sync", "post"],
        help="configure=save secrets locally, status=show config, start=loop, sync=edit once, post=force new embed",
    )
    p.add_argument("--ini", default=".ardr-discord.ini", help="Local Discord secrets/config file (mode 600).")
    p.add_argument("--channel-id", help="Discord channel ID override.")
    p.add_argument("--token", help="Bot token for configure only. Prefer the hidden prompt.")
    p.add_argument("--title", help="Embed title for configure.")
    p.add_argument("--interval", type=int, help="Poll interval in seconds.")
    p.set_defaults(func=cmd_discord)
