---
name: adb
description: >-
  Controls Android devices via adb: screenshot for AI vision analysis, tap, swipe,
  input text, key events, UI dump, install APK, shell. Use when the user asks to
  adb screenshot, control Android phone, remote test on device, tap/swipe on phone,
  or combine with Telegram remote ops. Requires adb and USB debugging. Pair with
  tg-notify skill for sending screenshots to Telegram.
disable-model-invocation: true
---

# adb — Android Device Control Skill

Teach the agent to operate a connected Android device via **adb_skill** shell scripts.  
Standalone — self-contained package. Pair with **tg** skill for Telegram remote workflows.

**Composable:** install alone (`./mob install-skill --only adb`) or with `tg` / `ios`. See `mobile-agent/docs/SKILL_COMPOSE.md`.

## Prerequisites

1. Install **adbkit** (includes platform-tools bootstrap — no system adb required):

```bash
pip install -e "/path/to/adbkit"
# or: ./droid-ctl/scripts/setup.sh
adbkit install-tools   # downloads adb to ~/.droid-ctl/platform-tools/
adbkit which
```

2. Connect Android device (USB debugging on) or `adb connect HOST:5555`.

3. Verify:

```bash
adbkit devices
/path/to/droid-ctl-skill/scripts/check-env.sh
```

4. Optional (Telegram remote): install **tgkit** — see [docs/REMOTE_WORKFLOW.md](docs/REMOTE_WORKFLOW.md).

## When to use

- User wants **adb screenshot** for AI to analyze the current screen
- User wants to **tap / swipe / type** on Android remotely
- User wants **UI hierarchy** (uiautomator dump) to find element bounds
- User wants **install APK**, start activity, pull logs
- User describes **Telegram remote control** of local Android via AI

## Agent workflow (vision loop)

Standard **see → think → act** loop for Android automation:

```
1. adb-analyze.sh --ui        → JSON with screenshot path (+ optional UI XML)
2. Read/analyze the PNG       → decide next action (coordinates from image or XML)
3. adb-tap.sh / adb-swipe.sh  → perform action
4. Repeat from step 1         → verify result
5. Optional: adb-tg-shot.sh   → send screenshot to Telegram for human
```

Always prefer **adbkit CLI** or **droid-ctl-skill/scripts** over raw adb.

## Command reference

Script root: `droid-ctl-skill/scripts/` (delegates to `droid-ctl`)

### Screenshot & analysis

```bash
adbkit shot --json
adbkit analyze --ui
adb-analyze.sh --ui
adb-tg-shot.sh -c "当前界面"
```

After `--json`, **read the PNG file** at `path` for vision analysis.

### Touch & input

```bash
adb-tap.sh X Y
adb-swipe.sh X1 Y1 X2 Y2 [DURATION_MS]
adb-input.sh "hello world"
adb-key.sh BACK
adb-key.sh HOME
```

Screen size: run `adb shell wm size` or read from `adb-shot.sh --json` field `screen`.

### Apps & files

```bash
adb-install.sh app.apk
adb-start.sh com.pkg/.MainActivity
adb-pull.sh /sdcard/file.txt
adb-push.sh local.txt /sdcard/
adb-shell.sh "pm list packages | grep poker"
```

### Debug

```bash
adb-devices.sh
adb-logcat.sh -n 100
adb-logcat.sh -f
```

## Coordinate tips

- Origin (0,0) is **top-left**
- Get resolution: `wm size` → e.g. `1080x2400` → center tap ≈ `540 1200`
- After tap, **always re-screenshot** to confirm UI changed
- For precise targets, use `adb-ui-dump.sh` and parse `bounds="[x1,y1][x2,y2]"` → tap center

## Remote Telegram workflow

When user sends instructions via Telegram and expects Android actions on the **local Mac**:

1. User messages Bot on phone (remote)
2. Local Agent (Cursor) receives task — user pastes or Bot webhook triggers session
3. Agent runs adb_skill scripts on the Mac (USB-connected test phone)
4. Agent sends result screenshot via `adb-tg-shot.sh` or `tgkit send --photo`

See [docs/REMOTE_WORKFLOW.md](docs/REMOTE_WORKFLOW.md) for full architecture.

## Safety rules

- Confirm destructive actions (uninstall, factory reset, `rm -rf`) with user
- Do not expose `TELEGRAM_BOT_TOKEN`
- Truncate logcat before sending; use `--file` for full logs
- On production devices, warn before automated tapping

## Troubleshooting

| Error | Fix |
|-------|-----|
| `no device connected` | USB debug on; authorize RSA prompt on phone |
| `multiple devices` | `export ADB_SERIAL=...` |
| `adb not found` | `brew install android-platform-tools` |
| `tgkit not installed` | `pip install "tg-notify[dotenv]"` for `--tg` features |
| Screenshot black/empty | Wake screen: `adb shell input keyevent 26` then retry |
| `uiautomator dump` fails | Try Android 7+; some OEMs need accessibility |

## More detail

- [reference.md](reference.md) — full command tables
- [examples.md](examples.md) — common scenarios
- [docs/GUIDE.md](docs/GUIDE.md) — setup guide
