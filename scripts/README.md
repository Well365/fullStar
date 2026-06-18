# scripts/ — 包根脚本索引 / Root Scripts Index

> 完整安装与依赖说明：**[docs/INSTALL.md](../docs/INSTALL.md)** · **[docs/DEPENDENCIES.md](../docs/DEPENDENCIES.md)**  
> Telegram 配置：**[docs/TELEGRAM_SETUP.md](../docs/TELEGRAM_SETUP.md)**（中 / En / 日）  
> iTerm 多标签路由：**[docs/ITERM_MULTI_TAB.md](../docs/ITERM_MULTI_TAB.md)**

## 脚本一览

| 脚本 | 命令别名 | 作用 |
|------|----------|------|
| [setup-telegram.sh](setup-telegram.sh) | `./mob tg-setup` | ★ Telegram Token + Chat ID 一键配置 |
| [install-skill.sh](install-skill.sh) | `./mob install-skill` | 安装 Agent Skill 到 Cursor / Claude |
| [tg-relay-daemon.sh](tg-relay-daemon.sh) | `./mob tg-start` | ★ 单例守护进程（杀重复实例 + 崩溃自动重启） |
| [tg-relay.py](tg-relay.py) | `./mob tg-relay-once` | 单次前台运行（调试） |

---

## setup-telegram.sh

**用途：** 配置 `mobile-agent/.env` 中的 Telegram，安装 `tg-notify` 与 `python-telegram-bot`。

```bash
chmod +x tg-relay/setup-telegram.sh

./tg-relay/setup-telegram.sh --test              # 交互式 + 测试消息
./tg-relay/setup-telegram.sh --fetch-chat-id     # 自动获取 Chat ID
./tg-relay/setup-telegram.sh --token "T" --chat-id "ID" --non-interactive --test
```

| 选项 | 说明 |
|------|------|
| `--token` | Bot Token（跳过交互） |
| `--chat-id` | Chat ID |
| `--fetch-chat-id` | 通过 getUpdates 自动获取 |
| `--test` | 配置后发测试消息 |
| `--non-interactive` | 无 Token 时直接失败 |
| `--no-relay-deps` | 不安装 python-telegram-bot |

---

## install-skill.sh

**用途：** 将 Skill 文档复制到 `~/.cursor/skills` 与 `~/.claude/skills`。

```bash
./scripts/install-skill.sh                    # 全部：tg + adb + ios + mobile-agent
./scripts/install-skill.sh --only tg            # 仅 Telegram
./scripts/install-skill.sh --only adb,ios       # 双端设备，无 TG Skill
./scripts/install-skill.sh --list               # 列出可装 Skill
```

| Skill ID | 来源目录 | Cursor 名 |
|----------|----------|-----------|
| `tg` | `tg-notify-skill/` | `tg-notify` |
| `adb` | `droid-ctl-skill/` | `adb` |
| `ios` | `iphone-ctl-skill/` | `ios` |
| `mobile-agent` | mob-remote-skill/SKILL.md | `mobile-agent` |

各子 Skill 的 `*/scripts/install-skill.sh` 由本脚本统一调用。

---

## tg-relay-daemon.sh（推荐）

**用途：** 单例守护 `tg-relay.py`——启动前杀掉所有重复实例；进程退出后自动重启。

```bash
./mob tg-start              # 后台守护（推荐）
./mob tg-start --foreground # 前台守护（可看日志）
./mob tg-stop               # 停止守护 + 所有 tg-relay
./mob tg-restart            # 先杀后启
./mob tg-status             # 状态 + 日志尾部

# 或直接
./tg-relay-daemon.sh start
```

| 文件 | 说明 |
|------|------|
| `inbox/tg-relay-daemon.pid` | 守护进程 PID |
| `inbox/tg-relay.log` | 运行日志 |

环境变量：`TG_RELAY_RESTART_DELAY`（默认 3s）、`TG_RELAY_LOG`

---

## tg-relay.py

**用途：** 长轮询 Telegram Bot，接收命令并调用 `droid-ctl` / `iphone-ctl`。

```bash
pip install "python-telegram-bot>=20,<22"   # 或运行 setup-telegram.sh 自动装
./mob tg-start           # 守护进程（单例 + 自动重启）
./mob tg-stop            # 停止
./mob tg-relay-once      # 单次前台（调试）
./mob tg-inbox                         # 查看自然语言待办
python3 tg-relay.py --dry-run "/help"   # 本地测试命令解析
```

**依赖：** `mobile-agent/.env` 中的 `TELEGRAM_BOT_TOKEN`  
**Bot 命令：** `/shot` `/tap` `/swipe` `/check` `/devices` `/help`

---

## 与其他安装脚本的关系

```
mobagent setup [--only tg,adb,ios]     ← mob-compose/scripts/setup-all.sh（总装）
    ├── tg-notify/scripts/setup.sh         ← 仅 pip 装 tgkit
    ├── tg-notify-skill/scripts/setup-all.sh  ← tg-notify + .env + skill
    ├── droid-ctl/scripts/setup.sh        ← 仅 pip 装 droid-ctl + platform-tools
    ├── droid-ctl-skill/scripts/setup-all.sh
    ├── iphone-ctl/scripts/setup.sh
    └── iphone-ctl-skill/scripts/setup-all.sh

mobagent tg-setup                      ← tg-relay/setup-telegram.sh（仅 TG）
mobagent install-skill                 ← scripts/install-skill.sh（仅 Skill）
```

详见 **[docs/INSTALL.md](../docs/INSTALL.md)**。

---

## 各子目录 scripts/（索引）

| 目录 | 主要脚本 | 说明 |
|------|----------|------|
| `tg-notify/scripts/` | `setup.sh` | 仅 pip 安装 tg-notify |
| `tg-notify-skill/scripts/` | `setup-all.sh`, `check-env.sh`, `install-skill.sh`, `tg-notify.sh` | TG 完整配置 |
| `droid-ctl/scripts/` | `setup.sh`, `vendor-platform-tools.sh` | droid-ctl + platform-tools |
| `droid-ctl-skill/scripts/` | `setup-all.sh`, `adb-*.sh`, `check-env.sh` | Android 操作脚本 |
| `iphone-ctl/scripts/` | `setup.sh` | pip 安装 iphone-ctl |
| `iphone-ctl-skill/scripts/` | `setup-all.sh`, `setup-wda.sh`, `ios-*.sh` | iOS + WDA |
| `mob-compose/scripts/` | `setup-all.sh`, `check-env.sh`, `shot-*.sh`, `build-wda.sh` | 总装与日常运维 |

完整选项与组合见 **[docs/INSTALL.md](../docs/INSTALL.md)** · 依赖见 **[docs/DEPENDENCIES.md](../docs/DEPENDENCIES.md)**。
