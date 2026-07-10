import sys

from .parser import build_parser
from ..ui.home import show_home


# People naturally think "server, then action".  Keep the traditional
# command-first interface, but accept that friendlier order too.
_COMMANDS = {
    "init", "default", "setup", "quickstart", "check", "fix", "configure", "validate",
    "render", "install", "status", "info", "ports", "linuxgsm", "doctor", "menu",
    "start", "up", "stop", "down", "pause", "resume", "debug", "restart", "reload",
    "update", "logs", "tail", "systemd", "windows-task", "battleye", "linux-user",
    "service", "firewall", "backup", "mods", "query", "deploy", "launch", "workshop",
    "web", "open", "discord",
}
_EASY_ACTIONS = {
    "on": "start", "run": "start", "start": "start", "up": "start",
    "off": "stop", "stop": "stop", "down": "stop",
    "restart": "restart", "reload": "restart",
    "log": "logs", "logs": "logs", "tail": "tail",
    "status": "status", "check": "check", "health": "check",
    "update": "update", "install": "install", "render": "render", "deploy": "deploy",
    "query": "query", "ports": "ports", "pause": "pause", "resume": "resume", "debug": "debug",
    "fix": "fix", "repair": "fix", "backup": "backup", "info": "info", "help": "info",
}


def main() -> None:
    args = build_parser().parse_args(_friendly_argv(sys.argv[1:]))
    if not hasattr(args, "func"):
        show_home(args)
        return
    args.func(args)


def _friendly_argv(argv: list[str]) -> list[str]:
    """Support `reforger my-server start` alongside `reforger start my-server`."""
    prefix, remainder = _global_options(argv)
    if not remainder or remainder[0] in _COMMANDS or remainder[0].startswith("-"):
        return argv
    server = remainder[0]
    if len(remainder) == 1:
        return prefix + ["info", server]
    action = _EASY_ACTIONS.get(remainder[1].lower())
    if action:
        if action == "backup":
            return prefix + ["backup", "create", server] + remainder[2:]
        return prefix + [action, server] + remainder[2:]
    # An unknown word is much nicer as an unknown server than an opaque
    # argparse command error: the existing resolver lists valid server names.
    return prefix + ["info", server] + remainder[1:]


def _global_options(argv: list[str]) -> tuple[list[str], list[str]]:
    """Keep leading global options in front of the generated command."""
    prefix: list[str] = []
    index = 0
    while index < len(argv):
        item = argv[index]
        if item == "--config" and index + 1 < len(argv):
            prefix.extend(argv[index:index + 2])
            index += 2
        elif item.startswith("--config=") or item in {"-h", "--help"}:
            prefix.append(item)
            index += 1
        else:
            break
    return prefix, argv[index:]
