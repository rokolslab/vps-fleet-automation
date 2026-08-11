# Security Model

This public repository contains reusable automation only. It must never become a source of production infrastructure state.

## Repository boundaries

Do not commit:

- real IP addresses, domains, provider identifiers, or host aliases;
- production inventories or host/group vars;
- private keys, passwords, API tokens, cookies, or environment files;
- application encryption keys;
- database files, backups, exports, runtime logs, or operational evidence.

Tracked examples use documentation-only addresses and generic aliases such as `server-01` and `automation-01`.

## Mutating automation

Mutating playbooks should:

1. require an explicit single-host `--limit` by default;
2. fail when the target does not match the reviewed role or alias;
3. use explicit apply flags for high-impact application deployment;
4. support check mode where the underlying modules make that meaningful;
5. document SSH/firewall lockout risks before apply;
6. verify listeners, services, or health endpoints after changes.

## SSH and firewall

SSH host-key checking stays enabled. During an SSH port migration, keep the previous access path available until the new port has been verified from a separate session or provider console. Public firewall ports are opt-in variables, not hard-coded assumptions.

## Application secrets

Generated n8n secrets are stored only in the remote protected `.env` file (`0600`). The role creates this file only when it does not already exist, preventing accidental encryption-key rotation on reruns.

For shared production environments, use a dedicated secret manager, SOPS/age, or Ansible Vault rather than storing secret material in this repository.
