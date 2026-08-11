# Bootstrap and Baseline Runbook

This runbook describes the safe path from a newly provisioned Ubuntu 24.04 VPS to the managed `ops` user and hardened baseline.

## 1. Prepare dependencies on the control machine

```bash
python3 -m pip install -r requirements-dev.txt ansible-core
ansible-galaxy collection install -r collections/requirements.yml
```

## 2. Prepare the provider-access inventory

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

## 4. Validate and apply the baseline over the original access path

Keep using the provider-access inventory for the first baseline rollout. This avoids assuming that SSH `2322` already exists before the role creates it.

```bash
ansible-playbook -i ansible/inventories/bootstrap.yml \
  ansible/playbooks/common-baseline.yml \
  --limit server-01 --check --diff

ansible-playbook -i ansible/inventories/bootstrap.yml \
  ansible/playbooks/common-baseline.yml \
  --limit server-01
```

Keep provider console access available. The default baseline keeps port `22` while adding and hardening port `2322`.

## 5. Verify the managed access path independently

From a separate terminal:

```bash
ssh -p 2322 ops@<host>
```

Do not continue until this login succeeds.

## 6. Create the post-baseline managed inventory

```bash
cp config/nodes.example.yml config/nodes.yml
python3 scripts/generate-inventory.py --overwrite
ansible-inventory -i ansible/inventories/production.yml --list
ansible-playbook -i ansible/inventories/production.yml ansible/playbooks/ping.yml --limit server-01
```

The managed example uses `ops` on SSH `2322`, which is now a verified state rather than an assumption.

## 7. Close legacy SSH only after verification

Set `baseline_keep_ssh_port_22: false` in local inventory/group variables and rerun the baseline against the verified production inventory:

```bash
ansible-playbook -i ansible/inventories/production.yml \
  ansible/playbooks/common-baseline.yml \
  --limit server-01 --check --diff
```

Review the planned SSH/UFW changes, then apply the same scoped command without `--check --diff`.

## Recovery

If the target SSH path fails, use port `22` or the provider console. Never close the legacy path before independently verifying `ops:2322`.
