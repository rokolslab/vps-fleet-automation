#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "config" / "nodes.yml"
DEFAULT_OUTPUT = ROOT / "ansible" / "inventories" / "production.yml"


def build_inventory(data: dict) -> dict:
    defaults = data.get("defaults", {})
    nodes = data.get("nodes", {})
    hosts = {}
    for alias, cfg in nodes.items():
        hosts[alias] = {
            "ansible_host": cfg["host"],
            "ansible_user": cfg.get("ansible_user", defaults.get("ansible_user", "ops")),
            "ansible_port": cfg.get("ansible_port", defaults.get("ansible_port", 22)),
            "node_roles": cfg.get("roles", []),
        }
    return {"all": {"children": {"managed_vps": {"hosts": hosts}}}}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate local Ansible inventory from config/nodes.yml")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.output.exists() and not args.overwrite:
        parser.error(f"{args.output} exists; pass --overwrite to replace it")

    data = yaml.safe_load(args.source.read_text(encoding="utf-8")) or {}
    inventory = build_inventory(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(inventory, sort_keys=False), encoding="utf-8")
    print(f"Generated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
