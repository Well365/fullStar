# ios_skill

iOS **真机**：WDA 坐标 tap/swipe + 截图 + Telegram。能力层 [ioskit](../ioskit)。

> [docs/GUIDE.md](docs/GUIDE.md) — 能力表与 WDA 配置

## 能力表（与 droid-ctl 对齐）

| 能力 | iphone-ctl / 脚本 | 状态 |
|------|---------------|------|
| 列设备 | `ioskit devices` | ✅ |
| 截图 AI 看屏 | `ioskit shot --json` | ✅ idevicescreenshot |
| 坐标点击 | `ioskit tap X Y` | ✅ WDA |
| 坐标滑动 | `ioskit swipe` | ✅ WDA |
| 视觉循环 | `ios-analyze.sh` | ✅ |
| 截图发 TG | `ios-tg-shot.sh` | ✅ tg-notify |
| 装 ipa | — | Phase 2 |
| UI 树 | — | Phase 2 |

## 快速开始

```bash
# 1. 工具
brew install libimobiledevice
cd ios_skill && ./scripts/setup-all.sh

# 2. WDA（一次性，Xcode 装 WebDriverAgentRunner 到手机）

# 3. 端口转发（常驻终端）
iproxy 8100 8100 -u $IOS_UDID

# 4. 验证
ioskit wda status
ioskit shot --json
```

## Agent 话术

- 「iOS 真机截图分析一下」
- 「在 iPhone 上点坐标 200 400」
- 「把 iOS 画面发到 Telegram」

## License

MIT
