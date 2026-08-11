# Bootstrap and Baseline Runbook

This runbook describes the safe path from a newly provisioned Ubuntu 24.04 VPS to the managed `ops` user and hardened baseline.

## 1. Prepare dependencies on the control machine

```bash
python3 -m pip install -r requirements-dev.txt ansible-core
ansible-galaxy collection install -r collections/requirements.yml
```

## 2. Prepare a bootstrap inventory

Copy the sanitized example and replace only local, gitignored values:

```bash
cp ansible/inventories/bootstrap.example.yml ansible/inventories/bootstrap.yml
```

The bootstrap inventory represents the provider's initial SSH access path, commonly `root` on port `22`. Keep it local; it is ignored by Git.

## 3. Bootstrap the managed admin user

Use a local public key and target exactly one host:

```bash
ansible-playbook -i ansible/inventories/bootstrap.yml \
  ansible/playbooks/bootstrap-admin.yml \
  --limit server-01 \
  -e bootstrap_admin_public_key_file="$HOME/.ssh/id_ed25519.pub"
```

If the provider image requires a different initial user or privilege path, adjust only the local bootstrap inventory.

## 4. Create the managed inventory

```bash
cp config/nodes.example.yml config/nodes.yml
python3 scripts/generate-inventory.py --overwrite
ansible-inventory -i ansible/inventories/production.yml --list
```

The managed example uses `ops` and SSH port `2322` as the desired post-baseline state. During the first baseline rollout, keep SSH port `22` enabled until `2322` is verified from a separate session.

## 5. Validate connectivity and baseline in check mode

Before applying changes:

```bash
ansible-playbook -i ansible/inventories/production.yml ansible/playbooks/ping.yml --limit server-01

ansible-playbook -i ansible/inventories/production.yml \
  ansible/playbooks/common-baseline.yml \
  --limit server-01 --check --diff
```

Keep provider console access available while changing SSH and firewall settings.

## 6. Apply the baseline

```bash
ansible-playbook -i ansible/inventories/production.yml \
  ansible/playbooks/common-baseline.yml \
  --limit server-01
```

## 7. Verify before closing legacy SSH

From a separate terminal, verify the target port:

```bash
ssh -p 2322 ops@<host>
```

Only after independent verification should local configuration set `baseline_keep_ssh_port_22: false` and rerun the scoped baseline.

## Recovery

If the target SSH path fails, use the still-open legacy access path or the provider console. Do not remove port `22` until port `2322` has been independently verified.
