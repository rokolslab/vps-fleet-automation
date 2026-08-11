from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_baseline_requires_single_host_and_baseline_role():
    text = read("ansible/playbooks/common-baseline.yml")
    assert "ansible_play_hosts_all | length == 1" in text
    assert "'baseline' in (node_roles | default([]))" in text


def test_n8n_requires_explicit_apply_and_automation_role():
    text = read("ansible/playbooks/n8n-install.yml")
    assert "allow_n8n_stack_apply | bool" in text
    assert "'automation' in (node_roles | default([]))" in text


def test_https_requires_explicit_apply_and_domain():
    text = read("ansible/playbooks/n8n-https-nginx.yml")
    assert "allow_n8n_https_apply | bool" in text
    assert "n8n_https_domain | default('') | length > 0" in text


def test_n8n_is_loopback_only_by_default():
    text = read("ansible/roles/n8n_stack/defaults/main.yml")
    assert "n8n_bind_host: 127.0.0.1" in text


def test_public_repository_contains_no_private_proxy_markers():
    forbidden = ("3x-ui", "VLESS", "Hysteria", "fi-1", "fi-2", "ge-1", "ge-2", "us-1")
    searchable = [
        ROOT / "README.md",
        ROOT / "README.ru.md",
        ROOT / "AGENTS.md",
        ROOT / "ansible",
        ROOT / "config",
        ROOT / "docs",
        ROOT / "scripts",
    ]
    for item in searchable:
        files = [item] if item.is_file() else item.rglob("*")
        for path in files:
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                for marker in forbidden:
                    assert marker not in text, f"private marker {marker!r} found in {path}"
