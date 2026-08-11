# VPS Fleet Automation

[![CI](https://github.com/rokolslab/vps-fleet-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/rokolslab/vps-fleet-automation/actions/workflows/ci.yml)

[English](README.md) · **Русский**

Защищённая по умолчанию Ansible-автоматизация для небольшого парка Ubuntu VPS: первичный bootstrap, hardening сервера, развёртывание n8n в Docker, публикация через Nginx/HTTPS, генерация inventory, эксплуатационные runbook'и, тесты и CI.

Это публичный обезличенный портфолио-проект. Он демонстрирует Infrastructure as Code и безопасную эксплуатацию без production inventory, учётных данных, реальных имён серверов, IP-адресов, доменов и приватного состояния инфраструктуры.

## Что демонстрирует проект

- **Ansible-автоматизация** для Ubuntu Server 24.04 LTS.
- **Двухэтапный onboarding**: сначала исходный доступ провайдера, затем проверенный управляемый доступ `ops`.
- **Safe-by-default mutations**: явный single-host `--limit`, проверки ролей, check mode и fail-closed assertions.
- **Hardening сервера**: проверка эффективной политики SSH, UFW, fail2ban, unattended upgrades и управляемый swap.
- **Контейнеризированный n8n** с PostgreSQL, Redis, worker, постоянными секретами и закреплёнными версиями образов.
- **Корректная работа за reverse proxy** с внешними editor/webhook URL.
- **Nginx + ACME/HTTPS** при сохранении n8n только на `127.0.0.1:5678`.
- **Inventory as Code** с обезличенными YAML-примерами и генератором локального inventory.
- **Runbook'и** для bootstrap/baseline и n8n/HTTPS.
- **Закреплённый validation toolchain** для воспроизводимого CI.
- **GitHub Actions CI** с pytest, yamllint, ansible-lint и `ansible-playbook --syntax-check`.

## Модель безопасности

Проект намеренно разделяет переносимую автоматизацию и реальные данные инфраструктуры:

- в Git хранятся только примеры и placeholders;
- реальные inventory, `.env`, ключи, секреты, backups, exports, logs и эксплуатационные данные остаются вне Git;
- изменяющие состояние playbook'и требуют явного single-host `--limit` и подходящей inventory-role;
- application deployment дополнительно требует explicit apply flag;
- SSH host-key checking остаётся включённым;
- common baseline управляет доступом к хосту, application-role — своими публичными портами;
- секреты n8n не регенерируются автоматически, если обнаружены существующие данные БД.

Подробнее: [`docs/security-model.md`](docs/security-model.md).

## Структура

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

## Быстрый старт

Установите закреплённый validation toolchain и Ansible collections:

```bash
python3 -m pip install -r requirements-dev.txt
ansible-galaxy collection install -r collections/requirements.yml
```

### 1. Bootstrap нового VPS

Начинайте с исходного SSH-доступа провайдера, например `root:22`:

```bash
cp ansible/inventories/bootstrap.example.yml ansible/inventories/bootstrap.yml

ansible-playbook -i ansible/inventories/bootstrap.yml \
  ansible/playbooks/bootstrap-admin.yml \
  --limit server-01 \
  -e bootstrap_admin_public_key_file="$HOME/.ssh/id_ed25519.pub"
```

### 2. Примените baseline по исходному каналу доступа

```bash
ansible-playbook -i ansible/inventories/bootstrap.yml \
  ansible/playbooks/common-baseline.yml \
  --limit server-01 --check --diff
```

После проверки повторите без `--check --diff`. По умолчанию baseline оставляет SSH `22` и добавляет/усиливает `2322`.

### 3. Проверьте `ops:2322` и только затем создайте production inventory

```bash
cp config/nodes.example.yml config/nodes.yml
python3 scripts/generate-inventory.py --overwrite
ansible-inventory -i ansible/inventories/production.yml --list
ansible-playbook -i ansible/inventories/production.yml ansible/playbooks/ping.yml --limit server-01
```

Полный порядок: [`docs/runbook-bootstrap-baseline.md`](docs/runbook-bootstrap-baseline.md).

### 4. Разверните n8n

```bash
ansible-playbook -i ansible/inventories/production.yml \
  ansible/playbooks/n8n-install.yml \
  --limit automation-01 \
  -e n8n_stack_target_alias=automation-01 \
  -e n8n_public_url=https://automation.example.com/ \
  -e allow_n8n_stack_apply=true \
  --check --diff
```

После review примените изменения и выполните guarded HTTPS-playbook. Подробно: [`docs/runbook-n8n.md`](docs/runbook-n8n.md).

## Принципы проектирования

1. **Сначала bootstrap, затем managed state.** Желаемые SSH-настройки не считаются уже существующими.
2. **Минимальный blast radius.** Mutation выполняется только на одном явно выбранном хосте.
3. **Fail closed.** Preconditions и effective configuration проверяются явно.
4. **Секреты остаются вне Git.** Git не является secrets manager.
5. **Раздельная ответственность.** Host baseline и публикация приложений управляются разными roles.
6. **Проверка после изменений.** Контролируются SSH policy, listeners, services и health endpoints.
7. **Документированное восстановление.** Runbook'и содержат rollback/recovery path.

## Проверка качества

CI устанавливает закреплённый toolchain и объявленные Ansible collections, затем выполняет:

```bash
python -m pytest -q
yamllint .github ansible collections config
ansible-lint --profile basic ansible/playbooks/*.yml
ansible-playbook --syntax-check ...
```

Проверки выполняются только на обезличенных примерах.

## Контекст для портфолио

Репозиторий представляет собой обезличенную публичную выборку инженерных паттернов из приватного проекта управления VPS. Production-топология и специализированная приватная автоматизация намеренно исключены. Публичная версия показывает Ansible, Linux administration, Docker, Nginx, n8n, Python tooling, testing, linting, CI и структуру проекта для совместной работы с AI coding agents.

## Лицензия

MIT License. См. [`LICENSE`](LICENSE).
