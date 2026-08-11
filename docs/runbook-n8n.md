# n8n Deployment Runbook

This runbook covers the guarded deployment of the n8n Docker Compose stack and optional HTTPS publication.

## Preconditions

- the host already passed the common Ubuntu baseline;
- managed SSH access works through the production inventory;
- the host has `automation` in `node_roles`;
- the intended public DNS name resolves to the host before ACME/HTTPS apply;
- provider console access remains available for recovery.

## 1. Read-only connectivity check

```bash
ansible-playbook -i ansible/inventories/production.yml \
  ansible/playbooks/ping.yml \
  --limit automation-01
```

## 2. Review the n8n stack in check mode

For a public deployment, provide the final external URL when installing the stack so n8n generates correct editor and webhook URLs behind the reverse proxy:

```bash
ansible-playbook -i ansible/inventories/production.yml \
  ansible/playbooks/n8n-install.yml \
  --limit automation-01 \
  -e n8n_stack_target_alias=automation-01 \
  -e n8n_public_url=https://automation.example.com/ \
  -e allow_n8n_stack_apply=true \
  --check --diff
```

The application port remains loopback-only (`127.0.0.1:5678`) by default.

## 3. Apply the n8n stack

After reviewing check mode, repeat without `--check --diff`:

```bash
ansible-playbook -i ansible/inventories/production.yml \
  ansible/playbooks/n8n-install.yml \
  --limit automation-01 \
  -e n8n_stack_target_alias=automation-01 \
  -e n8n_public_url=https://automation.example.com/ \
  -e allow_n8n_stack_apply=true
```

The role creates the protected `.env` only once. If persistent database data exists but `.env` is missing, it refuses to regenerate encryption/database secrets automatically.

## 4. Publish through Nginx and HTTPS

The HTTPS role checks that the loopback n8n upstream is reachable before changing Nginx, opens `80/tcp` and `443/tcp` through UFW, obtains the initial certificate with HTTP-01, and then installs the final reverse proxy configuration.

Check mode:

```bash
ansible-playbook -i ansible/inventories/production.yml \
  ansible/playbooks/n8n-https-nginx.yml \
  --limit automation-01 \
  -e n8n_https_target_alias=automation-01 \
  -e n8n_https_domain=automation.example.com \
  -e n8n_https_certbot_email=admin@example.com \
  -e allow_n8n_https_apply=true \
  --check --diff
```

Apply only after DNS and the check-mode result are reviewed.

## 5. Verification

Verify locally on the host:

```bash
curl -fsS http://127.0.0.1:5678/healthz
sudo nginx -t
sudo ufw status
```

Verify externally:

```bash
curl -I https://automation.example.com/
```

Confirm that port `5678` is not publicly reachable and that generated webhook URLs use the external HTTPS origin.

## Recovery

If HTTPS publication fails, keep n8n on its loopback listener and inspect Nginx/ACME configuration before retrying. Existing n8n data volumes and the protected `.env` must not be deleted or regenerated as part of HTTPS recovery.
