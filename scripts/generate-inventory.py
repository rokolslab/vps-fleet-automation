#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "config" / "nodes.yml"
DEFAULT_OUTPUT = ROOT / "ansible" / "inventories" / "production.yml"


def _valid_port(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 65535


def validate_config(data: Any) -> dict:
    if not isinstance(data, dict):
        raise ValueError("configuration root must be a mapping")

    defaults = data.get("defaults", {})
    nodes = data.get("nodes", {})
    if not isinstance(defaults, dict):
        raise ValueError("defaults must be a mapping")
    if not isinstance(nodes, dict) or not nodes:
        raise ValueError("nodes must be a non-empty mapping")

    default_user = defaults.get("ansible_user", "ops")
    default_port = defaults.get("ansible_port", 22)
    if not isinstance(default_user, str) or not default_user.strip():
        raise ValueError("defaults.ansible_user must be a non-empty string")
    if not _valid_port(default_port):
        raise ValueError("defaults.ansible_port must be an integer from 1 to 65535")

    for alias, cfg in nodes.items():
        if not isinstance(alias, str) or not alias.strip():
            raise ValueError("node aliases must be non-empty strings")
        if not isinstance(cfg, dict):
            raise ValueError(f"node {alias!r} must be a mapping")
        host = cfg.get("host")
        if not isinstance(host, str) or not host.strip():
            raise ValueError(f"node {alias!r} requires a non-empty host")
        roles = cfg.get("roles", [])
        if not isinstance(roles, list) or not all(isinstance(role, str) and role for role in roles):
            raise ValueError(f"node {alias!r} roles must be a list of non-empty strings")
        if "ansible_user" in cfg and (not isinstance(cfg["ansible_user"], str) or not cfg["ansible_user"].strip()):
            raise ValueError(f"node {alias!r} ansible_user must be a non-empty string")
        if "ansible_port" in cfg and not _valid_port(cfg["ansible_port"]):
            raise ValueError(f"node {alias!r} ansible_port must be an integer from 1 to 65535")

    return data


def build_inventory(data: dict) -> dict:
    data = validate_config(data)
    defaults = data.get("defaults", {})
    nodes = data["nodes"]
    default_user = defaults.get("ansible_user", "ops")
    default_port = defaults.get("ansible_port", 22)

    hosts: dict[str, dict[str, Any]] = {}
    for alias, cfg in nodes.items():
        host_vars: dict[str, Any] = {
            "ansible_host": cfg["host"],
            "node_roles": cfg.get("roles", []),
        }
        if cfg.get("ansible_user", default_user) != default_user:
            host_vars["ansible_user"] = cfg["ansible_user"]
        if cfg.get("ansible_port", default_port) != default_port:
            host_vars["ansible_port"] = cfg["ansible_port"]
        hosts[alias] = host_vars

    return {
        "all": {
            "vars": {
                "ansible_user": default_user,
                "ansible_port": default_port,
            },
            "children": {"managed_vps": {"hosts": hosts}},
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate local Ansible inventory from config/nodes.yml")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    if args.output.exists() and not args.overwrite:
        parser.error(f"{args.output} exists; pass --overwrite to replace it")

    try:
        data = yaml.safe_load(args.source.read_text(encoding="utf-8")) or {}
        inventory = build_inventory(data)
    except (OSError, yaml.YAMLError, ValueError) as exc:
        parser.error(str(exc))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(inventory, sort_keys=False), encoding="utf-8")
    print(f"Generated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
