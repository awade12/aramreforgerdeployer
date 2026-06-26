from __future__ import annotations

from . import commands as c
from . import config_commands as cc


def dispatch_table() -> dict[str, callable]:
    return {
        "init": cc.cmd_init,
        "configure": cc.cmd_configure,
        "validate": cc.cmd_validate,
        "render": c.cmd_render,
        "install": c.cmd_install,
        "update": c.cmd_update,
        "start": c.cmd_start,
        "stop": c.cmd_stop,
        "restart": c.cmd_restart,
        "pause": c.cmd_pause,
        "resume": c.cmd_resume,
        "debug": c.cmd_debug,
        "status": c.cmd_status,
        "info": c.cmd_info,
        "query": c.cmd_query,
        "logs": c.cmd_logs,
        "ports": c.cmd_ports,
        "service": c.cmd_service,
        "firewall": c.cmd_firewall,
        "backup": c.cmd_backup,
        "mods": c.cmd_mods,
        "systemd": c.cmd_systemd,
        "windows-task": c.cmd_windows_task,
        "battleye": c.cmd_battleye,
        "linuxgsm": c.cmd_linuxgsm,
        "doctor": c.cmd_doctor,
        "linux-user": c.cmd_linux_user,
        "deploy": c.cmd_deploy,
        "web": c.cmd_web,
        "menu": c.cmd_menu,
    }
