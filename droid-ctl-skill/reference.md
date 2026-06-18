# adb_skill — Reference

## Environment

| Variable | Description |
|----------|-------------|
| `ADB_SERIAL` / `ANDROID_SERIAL` | Target device when multiple connected |
| `ADB_SHOT_DIR` | Screenshot output dir (default `/tmp/adb_skill`) |

## Scripts

| Script | Purpose |
|--------|---------|
| `adb-devices.sh` | List devices + active model/Android version |
| `adb-shot.sh` | `exec-out screencap -p` → PNG |
| `adb-analyze.sh` | Screenshot (+ optional UI dump) JSON for AI |
| `adb-tg-shot.sh` | Screenshot + `tgkit send --photo` |
| `adb-ui-dump.sh` | `uiautomator dump` → XML |
| `adb-tap.sh` | `input tap X Y` |
| `adb-swipe.sh` | `input swipe X1 Y1 X2 Y2 [ms]` |
| `adb-input.sh` | `input text` (spaces as `%s`) |
| `adb-key.sh` | `input keyevent` (HOME, BACK, …) |
| `adb-shell.sh` | Run arbitrary shell command |
| `adb-install.sh` | `adb install -r` |
| `adb-start.sh` | `am start -n PACKAGE/ACTIVITY` |
| `adb-pull.sh` | Pull file from device |
| `adb-push.sh` | Push file to device |
| `adb-logcat.sh` | `-n N` lines or `-f` follow |

## Key codes (adb-key.sh)

| Name | Code |
|------|------|
| HOME | 3 |
| BACK | 4 |
| ENTER | 66 |
| MENU | 82 |
| POWER | 26 |
| VOLUME_UP | 24 |
| VOLUME_DOWN | 25 |

## JSON output (`--json`)

`adb-shot.sh --json`:

```json
{
  "ok": true,
  "device": "ABC123",
  "path": "/tmp/droid-ctl-skill/20250616_120000.png",
  "screen": "1080x2400",
  "bytes": 123456
}
```

## Raw adb equivalents

| Script | adb command |
|--------|-------------|
| shot | `adb exec-out screencap -p > out.png` |
| tap | `adb shell input tap X Y` |
| swipe | `adb shell input swipe X1 Y1 X2 Y2 DURATION` |
| ui dump | `adb shell uiautomator dump /sdcard/window_dump.xml` |

## Pairing with tgkit

```bash
# Requires tg-notify + .env in mobile-agent root
./adb-tg-shot.sh -c "远程验收"
tgkit send --photo /tmp/droid-ctl-skill/latest.png --caption "done"
```

## Wireless adb

```bash
adb tcpip 5555
adb connect 192.168.1.100:5555
export ADB_SERIAL=192.168.1.100:5555
```
