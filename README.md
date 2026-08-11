# VPS Fleet Automation

[![CI](https://github.com/rokolslab/vps-fleet-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/rokolslab/vps-fleet-automation/actions/workflows/ci.yml)

**English** · [Русский](README.ru.md)

Guarded Ansible automation for a small Ubuntu VPS fleet: first-access bootstrap, secure host baseline, Docker-based n8n deployment, Nginx/HTTPS publication, inventory generation, operational runbooks, tests, and CI validation.

This repository is a public, sanitized portfolio project. It demonstrates Infrastructure as Code and operational safety controls without containing production inventory, credentials, real hostnames, addresses, domains, or private infrastructure state.

## What this project demonstrates

- **Ansible infrastructure automation** for Ubuntu Server 24.04 LTS.
- **Two-stage onboarding**: provider SSH access first, verified managed `ops` access second.
- **Safe-by-default mutations** with explicit single-host targeting, role guards, check mode, and fail-closed assertions.
- **Server hardening** with effective SSH policy verification, UFW, fail2ban, unattended upgrades, and managed swap.
- **Containerized n8n** with PostgreSQL, Redis, a worker, persistent secrets, and pinned image versions.
- **Reverse-proxy-aware n8n settings** for external HTTPS editor/webhook URLs.
- **Nginx + ACME/HTTPS publication** while keeping n8n bound to `127.0.0.1:5678`.
- **Inventory as code** using sanitized YAML examples and generated local inventory.
- **Operational runbooks** for bootstrap/baseline and n8n/HTTPS workflows.
- **Pinned validation toolchain** for reproducible CI runs.
- **GitHub Actions CI** with pytest, yamllint, ansible-lint, and Ansible syntax checks.

## Safety model

The project deliberately separates reusable automation from real infrastructure data:

- tracked files contain examples and placeholders only;
- real inventories, environment files, keys, secrets, backups, exports, logs, and runtime evidence stay outside Git;
- mutating playbooks require an explicit single-host `--limit` and appropriate inventory roles;
- application deployments additionally require explicit apply flags;
- SSH host-key checking remains enabled;
- the common baseline owns host-access policy, while application roles own their public service ports;
- persistent n8n secrets are never silently regenerated when existing database data is detected.

See [`docs/security-model.md`](docs/security-model.md).

## Repository layout

```text
.
├── .github/workflows/ci.yml
├── ansible/
│   ├── inventories/
│   │   ├── bootstrap.example.yml
│   │   └── production.example.yml
│   ├── playbooks/
│   │   ├── bootstrap-admin.yml
│   │   ├── ping.yml
│   │   ├── common-baseline.yml
│   │   ├── n8n-install.yml
│   │   └── n8n-https-nginx.yml
│   └── roles/
│       ├── common/
│       ├── n8n_stack/
│       └── n8n_https_nginx/
├── collections/requirements.yml
├── config/nodes.example.yml
├── docs/
├── scripts/
├── tests/
├── .yamllint
├── AGENTS.md
└── ansible.cfg
```

## Quick start

Install the pinned local validation toolchain and Ansible collections:

```bash
python3 -m pip install -r requirements-dev.txt
ansible-galaxy collection install -r collections/requirements.yml
```

### 1. Bootstrap a new VPS

Start from the provider's original SSH path (for example `root:22`):

```bash
cp ansible/inventories/bootstrap.example.yml ansible/inventories/bootstrap.yml

ansible-playbook -i ansible/inventories/bootstrap.yml \
  ansible/playbooks/bootstrap-admin.yml \
  --limit server-01 \
  -e bootstrap_admin_public_key_file="$HOME/.ssh/id_ed25519.pub"
```

### 2. Apply the common baseline over the original access path

```bash
ansible-playbook -i ansible/inventories/bootstrap.yml \
  ansible/playbooks/common-baseline.yml \
  --limit server-01 --check --diff
```

Review the plan, then repeat without `--check --diff`. The default migration keeps SSH `22` while adding and hardening `2322`.

### 3. Verify managed access, then generate production inventory

Verify `ops:2322` from a separate terminal before closing legacy access.

```bash
cp config/nodes.example.yml config/nodes.yml
python3 scripts/generate-inventory.py --overwrite
ansible-inventory -i ansible/inventories/production.yml --list
ansible-playbook -i ansible/inventories/production.yml ansible/playbooks/ping.yml --limit server-01
```

Full workflow: [`docs/runbook-bootstrap-baseline.md`](docs/runbook-bootstrap-baseline.md).

### 4. Deploy n8n

For a public HTTPS deployment, provide the final external URL during stack installation:

```bash
ansible-playbook -i ansible/inventories/production.yml \
  ansible/playbooks/n8n-install.yml \
  --limit automation-01 \
  -e n8n_stack_target_alias=automation-01 \
  -e n8n_public_url=https://automation.example.com/ \
  -e allow_n8n_stack_apply=true \
  --check --diff
```

Then review and apply, followed by the guarded HTTPS playbook. See [`docs/runbook-n8n.md`](docs/runbook-n8n.md).

## Design principles

1. **Bootstrap before assuming managed state.** Desired SSH settings are not treated as already available.
2. **Limit the blast radius.** Mutating operations target exactly one reviewed host.
3. **Fail closed.** Preconditions and effective configuration are checked explicitly.
4. **Keep secrets local.** Git is not a secrets manager.
5. **Separate ownership.** Host baseline and application exposure are managed by different roles.
6. **Verify after mutation.** SSH policy, listeners, services, and health endpoints are checked.
7. **Document recovery.** Runbooks describe rollback and provider-console recovery paths.

## Validation

CI installs the pinned toolchain and declared Ansible collections, then runs:

```bash
python -m pytest -q
yamllint .github ansible collections config
ansible-lint --profile basic ansible/playbooks/*.yml
ansible-playbook --syntax-check ...
```

against sanitized example inventories only.

## Portfolio context

This repository is a sanitized extraction of engineering patterns from a private VPS operations project. Production topology and service-specific private automation are intentionally excluded. The public version focuses on reusable infrastructure engineering: Ansible, Linux administration, Docker, Nginx, n8n, Python tooling, testing, linting, CI, and AI-agent-friendly project structure.

## License

MIT License. See [`LICENSE`](LICENSE).
