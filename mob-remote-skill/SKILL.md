---
name: mobile-agent
description: >-
  Automates Android and iOS real devices via Telegram remote control. Composable
  with sub-skills tg, adb, ios — install only what you need. Use for remote phone
  control, TG device ops, mobile验收, WDA tap, adb screenshot from Telegram,
  or mobile-agent/mobagent workflows. macOS only for iOS.
disable-model-invocation: true
---

# mobile-agent — Telegram + Android + iOS

Unified skill for **remote mobile device automation** via Telegram.

Package root: `mobile-agent/` — self-contained, no external project required.

## Composable skills

Each sub-skill is **standalone**. Install any combination:

| Skill | When to use alone | Pairs with |
|-------|-------------------|------------|
| **tg** | Send TG notifications only | adb, ios |
| **adb** | Android USB automation | tg (remote验收) |
| **ios** | iPhone + WDA automation | tg (remote验收) |
| **mobile-agent** | Full orchestration doc | all above |

```bash
./mob install-skill --only tg          # Telegram only
./mob install-skill --only adb,ios     # dual platform, no TG skill
./mob install-skill --only tg,adb      # Android remote验收
./mob install-skill                    # all

./mob setup --only tg,adb
```

See [docs/SKILL_COMPOSE.md](docs/SKILL_COMPOSE.md) for recipes.

Agent rule: load only the skills relevant to the task (tg / adb / ios).  
Sub-skill details: `tg-notify-skill/SKILL.md`, `droid-ctl-skill/SKILL.md`, `iphone-ctl-skill/SKILL.md`.

## Components

| Part | Path | Role |
|------|------|------|
| **mobagent** | `./mob` | Unified CLI entry |
| **devkit** | `mob-compose/` | setup / check / shot-android / shot-ios |
| **adbkit + adb_skill** | `droid-ctl/`, `droid-ctl-skill/` | Android control |
| **ioskit + ios_skill** | `iphone-ctl/`, `iphone-ctl-skill/` | iOS control (WDA) |
| **tgkit + tg_skill** | `tg-notify/`, `tg-notify-skill/` | Telegram send |
| **tg-relay** | `tg-relay.py` | Receive TG commands |
| **WebDriverAgent** | `WebDriverAgent/` | iOS tap/swipe |

## One-time setup

```bash
cd mobile-agent
chmod +x mobagent mob-compose/compose mob-compose/scripts/*.sh scripts/*.sh

./mob setup --test
./mob install-skill
./mob check
```

For iOS daily: `./mob ios-start` then ensure WDA Runner is on device.

## Three operating modes

### A. Agent + TG send (default)

User pastes TG instruction in Cursor → Agent runs device scripts → sends result via `tg-notify`.

```
TG instruction → Agent → droid-ctl/ioskit → tg-notify send --photo
```

### B. TG bot commands (semi-auto)

```bash
./mob tg-start
```

Bot commands: `/shot android`, `/shot ios`, `/tap 540 1200`, `/swipe ...`, `/check`, `/devices`  
Natural language → `inbox/pending.txt` → Agent reads `./mob tg-inbox`.

### C. Vision loop (full auto)

```
1. shot --json          → read PNG
2. analyze screen       → decide x,y
3. tap / swipe          → act
4. shot --json          → verify
5. tg-notify send --photo   → report to user
```

## Agent workflow

1. Run `./mob check` — fix missing tools/devices first.
2. Pick platform: **android** (`droid-ctl`) or **ios** (`iphone-ctl` + WDA + iproxy).
3. Always **re-screenshot after tap** to verify.
4. Send results: `./mob shot-android -c "..."` or `tgkit send --photo`.
5. Never print `TELEGRAM_BOT_TOKEN`.

## Quick commands

```bash
# Environment
./mob check
./mob ios-start

# Screenshot → Telegram
./mob shot-android -c "Android 验收"
./mob shot-ios -c "iOS 验收"

# Direct CLI
adbkit shot --json && droid-ctl tap 540 1200
ioskit shot --json && iphone-ctl tap 540 1200

# TG listener
./mob tg-start
./mob tg-inbox
```

## Coordinate tips

- Origin (0,0) top-left; get size from `shot --json` field `screen`
- Cocos games: use **image coordinates**, not element ids
- iOS games: set `IOS_WDA_BUNDLE_ID` in `mob-compose/compose.env`

## Safety

- Confirm destructive actions with user
- Use test devices for remote tap/swipe
- Do not commit `.env` or tokens

## Troubleshooting

| Issue | Fix |
|-------|-----|
| no android device | USB debug on; `adbkit devices` |
| WDA not ready | Xcode Run WDA Runner; `./mob ios-start` |
| TG token missing | `mobile-agent/.env` (copy from `.env.example`) |
| tap no effect (iOS) | Set `IOS_WDA_BUNDLE_ID`; app foreground |

## Sub-skills (individual)

| Skill | Install | Doc |
|-------|---------|-----|
| tg | `./mob install-skill --only tg` | `tg-notify-skill/SKILL.md` |
| adb | `./mob install-skill --only adb` | `droid-ctl-skill/SKILL.md` |
| ios | `./mob install-skill --only ios` | `iphone-ctl-skill/SKILL.md` |

## More detail

- [docs/SKILL_COMPOSE.md](docs/SKILL_COMPOSE.md) — **组合安装与场景**
- [README.md](README.md) — full package guide
- `droid-ctl-skill/docs/REMOTE_WORKFLOW.md` — TG remote architecture
- `iphone-ctl-skill/docs/WDA_SETUP.md` — iOS WDA setup

## Other languages

- [简体中文](mob-remote-skill/SKILL.zh-CN.md)
- [日本語](mob-remote-skill/SKILL.ja.md)
