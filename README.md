# VPS Fleet Automation

**English** · [Русский](README.ru.md)

Guarded Ansible automation for a small Ubuntu VPS fleet: secure baseline configuration, Docker-based application hosting, n8n deployment, Nginx/HTTPS, inventory generation, operational runbooks, and automated checks.

This repository is a public, sanitized portfolio project. It demonstrates infrastructure-as-code patterns and operational safety controls without containing production inventory, credentials, hostnames, addresses, domains, or private infrastructure state.

## What this project demonstrates

- **Ansible infrastructure automation** for Ubuntu Server 24.04 LTS.
- **Safe-by-default operations** with explicit single-host targeting, check mode, fail-fast assertions, and post-change verification.
- **Server hardening** with SSH policy, UFW, fail2ban, unattended upgrades, and conservative swap configuration.
- **Containerized automation workloads** using Docker Compose, PostgreSQL, Redis, n8n, and an n8n worker.
- **HTTPS publishing** through host Nginx while keeping application ports bound to loopback.
- **Inventory as code** using sanitized YAML examples and generated local inventory.
- **Operational documentation** designed for both human maintainers and AI coding agents.
- **Automated tests** for helper tools and safety guardrails.

## Safety model

The project deliberately separates reusable automation from real infrastructure data:

- tracked files contain only examples and placeholders;
- real inventory, environment files, keys, secrets, backups, exports, and runtime evidence must stay outside Git;
- mutating playbooks require an explicit `--limit` and, where appropriate, an explicit apply flag;
- SSH host key checking is not disabled globally;
- public services are exposed intentionally, while internal application ports remain loopback-only.

See [`docs/security-model.md`](docs/security-model.md) for the full policy.

## Repository layout

```text
.
├── ansible/
│   ├── inventories/          # Sanitized example inventory
│   ├── playbooks/            # Read-only checks and guarded mutations
│   └── roles/
│       ├── common/           # Ubuntu baseline and hardening
│       ├── n8n_stack/        # Docker Compose n8n stack
│       └── n8n_https_nginx/  # Nginx + ACME/HTTPS publication
├── config/                   # Sanitized declarative examples
├── docs/                     # Security model and runbooks
├── scripts/                  # Local helper tools
├── tests/                    # Automated checks
├── AGENTS.md                 # Project map for coding agents
└── ansible.cfg
```

## Quick start

Requirements on the control machine:

- Python 3.11+
- Ansible Core
- PyYAML

Create a local inventory from the sanitized example configuration:

```bash
cp config/nodes.example.yml config/nodes.yml
python3 scripts/generate-inventory.py --overwrite
ansible-inventory -i ansible/inventories/production.yml --list
```

Check connectivity:

```bash
ansible-playbook -i ansible/inventories/production.yml ansible/playbooks/ping.yml --limit server-01
```

Run a baseline in check mode before any mutation:

```bash
ansible-playbook -i ansible/inventories/production.yml \
  ansible/playbooks/common-baseline.yml \
  --limit server-01 --check --diff
```

Install the n8n stack only after reviewing the target host and explicitly enabling apply:

```bash
ansible-playbook -i ansible/inventories/production.yml \
  ansible/playbooks/n8n-install.yml \
  --limit automation-01 \
  -e n8n_stack_target_alias=automation-01 \
  -e allow_n8n_stack_apply=true
```

## Design principles

1. **Read before write.** Connectivity and audit steps precede configuration changes.
2. **Limit the blast radius.** Mutating operations target exactly one reviewed host by default.
3. **Fail closed.** Preconditions are assertions, not assumptions.
4. **Keep secrets local.** A private repository is not a secrets manager; a public one certainly is not.
5. **Verify after mutation.** Configuration changes are followed by service, listener, and health checks.
6. **Document rollback.** Runbooks describe expected changes and recovery paths.

## Portfolio context

This repository is a sanitized extraction of patterns used in a private VPS operations project. Production topology and service-specific private automation are intentionally excluded. The public version focuses on reusable infrastructure engineering: Ansible, Linux administration, Docker, Nginx, n8n, Python tooling, testing, and AI-agent-friendly project structure.

## License

MIT License. See [`LICENSE`](LICENSE).
