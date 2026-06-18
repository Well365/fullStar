# ios_skill Reference

## Environment

| Variable | Description |
|----------|-------------|
| `IOS_UDID` | Device UDID |
| `IOS_WDA_URL` | Default `http://127.0.0.1:8100` |
| `IOS_WDA_BUNDLE_ID` | WDA session bundle id |
| `IOS_SHOT_DIR` | Screenshot dir (`/tmp/ioskit`) |

## iphone-ctl CLI

| Command | Description |
|---------|-------------|
| `ioskit which` | libimobiledevice binary paths |
| `ioskit devices [--json]` | List UDIDs |
| `ioskit shot [-o PATH] [--json]` | idevicescreenshot |
| `ioskit analyze` | shot JSON for AI |
| `ioskit tap X Y [-b BUNDLE]` | WDA coordinate tap |
| `ioskit swipe X1 Y1 X2 Y2 [--duration]` | WDA swipe |
| `ioskit wda status` | WDA health |
| `ioskit wda proxy` | Print iproxy command |

## WDA HTTP (used internally)

- `GET /status`
- `POST /session` + `bundleId`
- `POST /session/{id}/wda/tap` `{"x", "y"}`
- `POST /session/{id}/wda/dragfromtoforduration`

## Scripts

| Script | Delegates to |
|--------|--------------|
| `ios-shot.sh` | `ioskit shot` |
| `ios-tap.sh` | `ioskit tap` |
| `ios-swipe.sh` | `ioskit swipe` |
| `ios-tg-shot.sh` | shot + tg-notify |
| `ios-analyze.sh` | `ioskit analyze` |

## Pairing tgkit

```bash
./ios-tg-shot.sh -c "登录页验收"
```
