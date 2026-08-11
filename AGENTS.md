# AGENTS.md

Project map for AI coding agents and maintainers.

## Purpose

`vps-fleet-automation` is a sanitized public Infrastructure-as-Code portfolio project for managing Ubuntu VPS hosts with Ansible. It focuses on reusable baseline hardening, Docker application hosting, n8n deployment, and guarded operational workflows.

## Key paths

- `README.md` — project overview and quick start.
- `ansible.cfg` — repository-root Ansible defaults.
- `ansible/inventories/production.example.yml` — sanitized inventory example.
- `ansible/playbooks/ping.yml` — read-only connectivity check.
- `ansible/playbooks/common-baseline.yml` — guarded Ubuntu baseline rollout.
- `ansible/roles/common/` — reusable hardening role.
- `ansible/playbooks/n8n-install.yml` — guarded n8n deployment.
- `ansible/roles/n8n_stack/` — n8n/PostgreSQL/Redis Docker Compose role.
- `config/nodes.example.yml` — sanitized node source example.
- `scripts/generate-inventory.py` — local inventory generator.
- `docs/security-model.md` — repository and operational safety rules.

## Agent rules

- Never introduce real production addresses, domains, aliases, credentials, tokens, keys, backups, or runtime evidence.
- Keep examples documentation-only and generic.
- Do not disable SSH host-key checking globally.
- Mutating playbooks must retain explicit blast-radius controls.
- Prefer read-only checks and `--check --diff` before mutation.
- Preserve idempotency; in particular, never rotate persistent application secrets merely because a role is rerun.
- Do not add proxy/VPN circumvention functionality to this public portfolio repository.
- When adding a new role, document its target, expected public listeners, secret strategy, verification, and rollback considerations.
