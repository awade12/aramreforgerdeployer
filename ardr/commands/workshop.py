from __future__ import annotations

import argparse

from ..config import resolve_instance_name
from ..workshop import apply_workshop_bundle, fetch_workshop_bundle, preview_workshop_bundle


def cmd_workshop(args: argparse.Namespace, load_with_ports) -> None:
    config_path, config = load_with_ports(args)
    instance_name = resolve_instance_name(config, _arg_instance(args), "workshop")
    bundle = fetch_workshop_bundle(args.url, args.scenario)
    preview_workshop_bundle(bundle)
    if args.dry_run:
        print("\nDry run. Re-run without --dry-run to save this setup.")
        return
    apply_workshop_bundle(
        config_path,
        config,
        instance_name,
        bundle,
        merge_mods=args.merge,
        set_server_name=args.set_name,
    )
    print("\nNext:")
    print(f"  reforger render {instance_name}")
    print(f"  reforger restart {instance_name}")


def _arg_instance(args: argparse.Namespace) -> str | None:
    return getattr(args, "instance", None) or getattr(args, "instance_name", None)
