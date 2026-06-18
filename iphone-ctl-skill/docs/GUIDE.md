# iOS 真机自动化指南（WDA + 坐标 + TG）

与 [adbkit](../adbkit) / [adb_skill](../adb_skill) 对齐。

## 架构

```
Telegram 指令 → Cursor Agent → ios_skill → ioskit
                                    ↓
              idevicescreenshot（截图）  WDA HTTP（tap/swipe）
                                    ↓
                              iPhone 真机
                                    ↓
                              tg-notify 回传截图
```

## 能力表

| # | 能力 | 命令 | 依赖 |
|---|------|------|------|
| 1 | 发现设备 | `ioskit devices` | libimobiledevice |
| 2 | 截图 | `ioskit shot --json` | idevicescreenshot |
| 3 | AI 分析 | 读 JSON `path` PNG | Agent 视觉 |
| 4 | 点击 | `ioskit tap X Y` | WDA + iproxy |
| 5 | 滑动 | `ioskit swipe ...` | WDA |
| 6 | 再截图验证 | `ioskit shot` | 同 #2 |
| 7 | 发 Telegram | `ios-tg-shot.sh` | tg-notify + .env |

## 一次性：WDA 装到真机

**详细图文步骤 → [WDA_SETUP.md](WDA_SETUP.md)**

```bash
./iphone-ctl-skill/scripts/setup-wda.sh   # clone + 打开 Xcode
```

简要：

1. Xcode 编译 **WebDriverAgentRunner** 到真机（Signing 选 Team）
2. 手机信任开发者证书、开启开发者模式
3. `iproxy 8100 8100 -u $IOS_UDID` 保持运行
4. `ioskit wda status` 确认 ready

## 每次使用

```bash
export IOS_UDID=$(ioskit devices | head -1)
export IOS_WDA_BUNDLE_ID=com.your.poker.game   # 建议

# 终端 A（保持）
iproxy 8100 8100 -u "$IOS_UDID"

# 终端 B
ioskit wda status
ioskit shot --json
ioskit tap 540 1200
./iphone-ctl-skill/scripts/ios-tg-shot.sh -c "验收"
```

## Cocos / 游戏注意

- 用 **坐标 tap**，不要依赖 accessibility 按钮名
- 每次操作后 **重新截图**
- 确保游戏在前台（可设 `IOS_WDA_BUNDLE_ID` 并 launch）

## 故障排查

| 现象 | 处理 |
|------|------|
| WDA connection refused | 开 Runner + iproxy |
| tap 无效 | 检查 bundle id、坐标、是否前台 |
| 无设备 | USB、信任、开发者模式 |

MIT
