# AGENTS.md

Project map for AI coding agents and maintainers.

## Purpose

`vps-fleet-automation` is a sanitized public Infrastructure-as-Code portfolio project for managing Ubuntu VPS hosts with Ansible. It focuses on reusable baseline hardening, Docker application hosting, n8n deployment, HTTPS publication, and guarded operational workflows.

## Key paths

- `README.md` / `README.ru.md` — project overview and quick start.
- `ansible.cfg` — repository-root Ansible defaults.
- `ansible/inventories/bootstrap.example.yml` — provider-access bootstrap inventory example.
- `ansible/inventories/production.example.yml` — sanitized post-baseline inventory example.
- `ansible/playbooks/bootstrap-admin.yml` — guarded managed-admin onboarding.
- `ansible/playbooks/ping.yml` — read-only connectivity check.
- `ansible/playbooks/common-baseline.yml` — guarded Ubuntu baseline rollout.
- `ansible/roles/common/` — reusable SSH/UFW/fail2ban/swap/update hardening role.
- `ansible/playbooks/n8n-install.yml` — guarded n8n deployment.
- `ansible/roles/n8n_stack/` — n8n/PostgreSQL/Redis Docker Compose role.
- `ansible/playbooks/n8n-https-nginx.yml` — guarded public HTTPS publication.
- `ansible/roles/n8n_https_nginx/` — Nginx, UFW and ACME/HTTPS role.
- `config/nodes.example.yml` — sanitized post-baseline node source example.
- `scripts/generate-inventory.py` — local inventory generator.
- `docs/security-model.md` — repository and operational safety rules.
- `docs/runbook-bootstrap-baseline.md` — bootstrap, baseline and SSH migration workflow.
- `docs/runbook-n8n.md` — n8n stack and HTTPS rollout workflow.
- `.github/workflows/ci.yml` — pytest and Ansible syntax validation.

## Agent rules

- Never introduce real production addresses, domains, aliases, credentials, tokens, keys, backups, logs, exports, or runtime evidence.
- Keep examples documentation-only and generic.
- Do not disable SSH host-key checking globally.
- Mutating playbooks must retain explicit single-host blast-radius controls and role/target guards.
- Preserve the two-stage onboarding model: provider access first, verified managed access second.
- Prefer read-only checks and `--check --diff` before mutation.
- Preserve idempotency; never rotate persistent application secrets merely because a role is rerun.
- Application roles own their public firewall listeners; the common baseline owns only host-access policy.
- When adding a new role, document its target, expected public listeners, secret strategy, verification, and rollback considerations.
