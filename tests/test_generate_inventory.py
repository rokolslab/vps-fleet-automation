from pathlib import Path
import importlib.util


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate-inventory.py"
spec = importlib.util.spec_from_file_location("generate_inventory", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_build_inventory_uses_defaults_and_roles():
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
    host = result["all"]["children"]["managed_vps"]["hosts"]["server-01"]

    assert host["ansible_host"] == "192.0.2.10"
    assert host["ansible_user"] == "ops"
    assert host["ansible_port"] == 2322
    assert host["node_roles"] == ["baseline"]
