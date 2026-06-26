from __future__ import annotations

import argparse

from .config import load_config, normalize_config_ports, resolve_instance_name, sample_config, save_config, select_instances, validate_config
from .paths import norm_path
from .wizard import build_instance, prompt


def cmd_init(args: argparse.Namespace) -> None:
    path = norm_path(args.config)
    instance_dir = path.parent / "instances"
    if (path.exists() or instance_dir.exists()) and not args.force:
        raise SystemExit(f"{path} already exists. Use --force to overwrite.")
    config = sample_config()
    normalize_config_ports(config)
    save_config(path, config)
    print(f"Created {path} and {instance_dir}/*.json")


def cmd_configure(args: argparse.Namespace) -> None:
    path = norm_path(args.config)
    config = load_config(args.config)[1] if path.exists() else {"baseDir": "./deployments", "steamcmd": "steamcmd", "instanceDir": "instances", "instances": []}
    config["baseDir"] = prompt("Base deploy directory", str(config.get("baseDir", "./deployments")))
    config["steamcmd"] = prompt("SteamCMD command/path", str(config.get("steamcmd", "steamcmd")))
    config.setdefault("instances", [])
    _upsert_instance(config, _arg_instance(args))
    normalize_config_ports(config)
    save_config(path, config)
    _print_validation(config)
    print(f"Saved {path}")


def cmd_default(args: argparse.Namespace) -> None:
    path, config = load_config(args.config)
    name = _arg_instance(args)
    if not name:
        current = str(config.get("defaultInstance", "")).strip()
        if current:
            print(f"Default server: {current}")
            return
        resolved = resolve_instance_name(config, None, "default")
        print(f"Default server: {resolved}")
        return
    select_instances(config, name)
    config["defaultInstance"] = name
    save_config(path, config)
    print(f"Default server set to {name}")


def cmd_validate(args: argparse.Namespace) -> None:
    _, config = load_config(args.config)
    if normalize_config_ports(config):
        print("WARNING: config has missing or colliding ports. Run `reforger ports --fix` to save safe ports.")
    _print_validation(config)
    print("Config is valid.")


def _upsert_instance(config: dict, instance_name: str | None) -> None:
    if instance_name:
        for index, instance in enumerate(config["instances"]):
            if instance.get("name") == instance_name:
                config["instances"][index] = build_instance(config, instance)
                return
    config["instances"].append(build_instance(config))


def _print_validation(config: dict) -> None:
    normalize_config_ports(config)
    errors = validate_config(config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)


def _arg_instance(args: argparse.Namespace) -> str | None:
    return getattr(args, "instance", None) or getattr(args, "instance_name", None)
