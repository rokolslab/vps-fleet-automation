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
2. fail when the target does not match the reviewed inventory role or alias;
3. use explicit apply flags for application deployment;
4. support check mode where the underlying modules make that meaningful;
5. document SSH/firewall lockout risks before apply;
6. verify effective configuration, listeners, services, or health endpoints after changes.

## Bootstrap and privilege model

A newly provisioned VPS starts from a local, gitignored provider-access inventory. `bootstrap-admin.yml` creates the managed `ops` account, installs a reviewed SSH public key, and by default creates a `visudo`-validated `NOPASSWD` sudoers drop-in for non-interactive Ansible automation. Password SSH authentication is later disabled by the baseline.

The post-baseline production inventory must not be treated as valid until the managed SSH path has been independently verified.

## SSH and firewall

SSH host-key checking stays enabled. The common baseline owns SSH access and default UFW policy only. Application roles own their explicit public listeners; for example, the n8n HTTPS role owns `80/tcp` and `443/tcp`.

During an SSH port migration, keep port `22` available until the target port has been verified from a separate session or provider console. The baseline uses an early OpenSSH drop-in and verifies effective `sshd -T` policy before restarting SSH.

## Application secrets

Generated n8n secrets are stored only in the remote protected `.env` file (`0600`). The role creates this file only when it does not already exist. If persistent n8n database data exists while `.env` is missing, the role fails closed rather than generating replacement credentials or an encryption key.

For shared production environments, use a dedicated secret manager, SOPS/age, or Ansible Vault rather than storing secret material in this repository.

## CI boundary

CI validates Python tests and Ansible syntax against sanitized examples only. CI must never receive production inventory or secrets.
