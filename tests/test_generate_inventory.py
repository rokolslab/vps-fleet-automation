from pathlib import Path
import importlib.util

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate-inventory.py"
spec = importlib.util.spec_from_file_location("generate_inventory", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_build_inventory_uses_shared_defaults_and_roles():
    data = {
        "defaults": {"ansible_user": "ops", "ansible_port": 2322},
        "nodes": {
            "server-01": {
                "host": "192.0.2.10",
                "roles": ["baseline"],
            }
        },
    }

    result = module.build_inventory(data)
    assert result["all"]["vars"] == {"ansible_user": "ops", "ansible_port": 2322}
    host = result["all"]["children"]["managed_vps"]["hosts"]["server-01"]

    assert host["ansible_host"] == "192.0.2.10"
    assert host["node_roles"] == ["baseline"]
    assert "ansible_user" not in host
    assert "ansible_port" not in host


def test_build_inventory_keeps_node_overrides():
    data = {
        "defaults": {"ansible_user": "ops", "ansible_port": 2322},
        "nodes": {
            "server-01": {
                "host": "192.0.2.10",
                "ansible_user": "admin",
                "ansible_port": 2222,
                "roles": ["baseline"],
            }
        },
    }

    host = module.build_inventory(data)["all"]["children"]["managed_vps"]["hosts"]["server-01"]
    assert host["ansible_user"] == "admin"
    assert host["ansible_port"] == 2222


def test_validation_rejects_missing_host():
    with pytest.raises(ValueError, match="requires a non-empty host"):
        module.build_inventory({"nodes": {"server-01": {"roles": ["baseline"]}}})


def test_validation_rejects_invalid_port():
    with pytest.raises(ValueError, match="ansible_port"):
        module.build_inventory({
            "defaults": {"ansible_port": 70000},
            "nodes": {"server-01": {"host": "192.0.2.10"}},
        })
