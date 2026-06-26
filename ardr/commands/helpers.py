from __future__ import annotations

import argparse
from pathlib import Path

from ..config import load_config, normalize_config_ports, resolve_instance_name, save_config, select_instances, validate_config


def one_instance(args: argparse.Namespace, command: str) -> tuple[Path, dict, dict]:
    cfg_path, config = load_with_ports(args)
    name = resolve_instance_name(config, arg_instance(args), canonical_command(command))
    return cfg_path, config, select_instances(config, name)[0]


def load_with_ports(args: argparse.Namespace) -> tuple[Path, dict]:
    config_path, config = load_config(args.config)
    if normalize_config_ports(config):
        save_config(config_path, config)
    return config_path, config


def arg_instance(args: argparse.Namespace) -> str | None:
    return getattr(args, "instance", None) or getattr(args, "instance_name", None)


def many_instance_name(args: argparse.Namespace) -> str | None:
    return arg_instance(args)


def canonical_command(command: str) -> str:
    return {"up": "start", "down": "stop", "reload": "restart", "tail": "logs", "launch": "deploy"}.get(command, command)


def print_validation(config: dict) -> None:
    errors = validate_config(config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("Config is valid.")
