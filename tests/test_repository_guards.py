from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".yml", ".yaml", ".py", ".j2", ".txt", ".cfg"}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_baseline_requires_single_host_and_baseline_role():
    text = read("ansible/playbooks/common-baseline.yml")
    assert "ansible_play_hosts_all | length == 1" in text
    assert "'baseline' in (node_roles | default([]))" in text


def test_ssh_hardening_uses_early_dropin_and_handles_socket_activation():
    defaults = read("ansible/roles/common/defaults/main.yml")
    tasks = read("ansible/roles/common/tasks/ssh.yml")
    assert "/00-vps-baseline.conf" in defaults
    assert "/usr/sbin/sshd -T" in tasks
    assert "ansible.builtin.service_facts" in tasks
    assert "ansible_facts.services['ssh.socket']" in tasks
    assert "daemon_reload: true" in tasks


def test_n8n_requires_explicit_apply_and_automation_role():
    text = read("ansible/playbooks/n8n-install.yml")
    assert "allow_n8n_stack_apply | bool" in text
    assert "'automation' in (node_roles | default([]))" in text


def test_n8n_is_loopback_only_and_version_pinned_by_default():
    text = read("ansible/roles/n8n_stack/defaults/main.yml")
    assert "n8n_bind_host: 127.0.0.1" in text
    assert "n8n:latest" not in text


def test_n8n_refuses_secret_regeneration_for_existing_data():
    text = read("ansible/roles/n8n_stack/tasks/main.yml")
    assert "docker volume inspect n8n_postgres_data" in text
    assert "automatic secret rotation is refused" in text


def test_https_requires_explicit_apply_domain_and_manages_firewall():
    playbook = read("ansible/playbooks/n8n-https-nginx.yml")
    tasks = read("ansible/roles/n8n_https_nginx/tasks/main.yml")
    assert "allow_n8n_https_apply | bool" in playbook
    assert "n8n_https_domain | default('') | length > 0" in playbook
    assert "port: '80'" in tasks
    assert "port: '443'" in tasks


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
            if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                assert marker not in text, f"private marker {marker!r} found in {path}"
