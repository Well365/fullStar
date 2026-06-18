---
name: ios
description: >-
  Controls real iOS devices via ioskit: idevicescreenshot for AI vision, WDA coordinate
  tap/swipe, screenshot to Telegram. Use when user asks iOS device screenshot, iPhone tap,
  WDA automation, ios remote test, or TG screenshot from iPhone. Requires libimobiledevice,
  WDA running on device, and iproxy. Pair with tg skill for Telegram. Composable with adb.
disable-model-invocation: true
---

# ios — iOS Real Device Skill (WDA + coordinate)

Operate a **USB-connected iPhone** via **ioskit**: screenshot with `idevicescreenshot`, tap/swipe with **WebDriverAgent** HTTP API. Aligned with adb_skill vision loop.

**Composable:** `./mob install-skill --only ios` or `--only tg,ios`. See `mobile-agent/docs/SKILL_COMPOSE.md`.

## Prerequisites

1. Install iphone-ctl + libimobiledevice:

```bash
brew install libimobiledevice
pip install -e "/path/to/ioskit"
```

2. Device: USB, trust computer, **Developer Mode** on.

3. **WDA** installed on device (WebDriverAgentRunner from Xcode, once per device/team).

4. Port forward (separate terminal, keep running):

```bash
export IOS_UDID=$(ioskit devices | head -1)
iproxy 8100 8100 -u "$IOS_UDID"
ioskit wda status   # ready: true
```

5. For games / Cocos, set bundle id:

```bash
export IOS_WDA_BUNDLE_ID=com.your.game.bundle
```

6. Optional Telegram: tg-notify + `.env` (see tg_skill).

## When to use

- iOS **real device** screenshot for AI analysis
- **Coordinate tap/swipe** on iPhone (WDA)
- Send iOS screenshot to **Telegram**
- Remote验收: TG instruction → Mac Agent → iphone-ctl → TG photo

## Agent workflow (vision loop)

Same as adb_skill:

```
1. iphone-ctl shot --json     → read PNG at path
2. AI analyzes screen     → pick x,y
3. iphone-ctl tap X Y         → WDA coordinate tap
4. iphone-ctl shot --json     → verify
5. ios-tg-shot.sh         → optional send to Telegram
```

Always re-screenshot after tap. Cocos games: use **coordinates from image**, not element ids.

## Commands

```bash
ioskit devices --json
ioskit shot --json
ioskit analyze
ioskit tap 200 400
ioskit swipe 200 600 200 200 --duration 0.4
ioskit wda status
ios-tg-shot.sh -c "iOS 验收"
```

Wrappers: `iphone-ctl-skill/scripts/ios-*.sh`

## vs adb_skill

| | adb (Android) | ios (iPhone) |
|--|---------------|--------------|
| Screenshot | adb screencap | idevicescreenshot |
| Tap/swipe | adb input | WDA HTTP |
| Extra setup | USB debug | WDA + iproxy |
| All apps | ~yes | own signed apps + coordinates for games |

## Safety

- Confirm before taps on production user devices
- Do not expose tokens
- WDA must be started by trusted developer build only

## Troubleshooting

| Issue | Fix |
|-------|-----|
| no device | USB, trust, unlock phone |
| WDA connection refused | Start WDA Runner, run iproxy |
| tap no effect | Set IOS_WDA_BUNDLE_ID, ensure app foreground |
| idevicescreenshot fail | `brew install libimobiledevice` |

See [reference.md](reference.md) and [docs/GUIDE.md](docs/GUIDE.md).
