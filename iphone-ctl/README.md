# ioskit

iOS **真机**工具包：libimobiledevice 截图 + **WebDriverAgent 坐标 tap/swipe**，可与 tg-notify 远程发 TG。

对标 [adbkit](../adbkit) + [adb_skill](../adb_skill)。

## 能力表（与 droid-ctl 对齐）

| 能力 | droid-ctl (Android) | iphone-ctl (iOS 真机) | 实现 |
|------|------------------|-------------------|------|
| 列设备 | `adbkit devices` | `ioskit devices` | `idevice_id -l` |
| 截图（AI 看屏） | `adbkit shot` | `ioskit shot` | `idevicescreenshot` |
| 坐标点击 | `adbkit tap X Y` | `ioskit tap X Y` | WDA HTTP |
| 坐标滑动 | `adbkit swipe` | `ioskit swipe` | WDA HTTP |
| 截图发 TG | `adb-tg-shot.sh` | `ios-tg-shot.sh` | tg-notify |
| 视觉循环 | shot→AI→tap→shot | 同左 | ios_skill |
| 装包 | `adbkit install` | Phase 2 `ideviceinstaller` | 待做 |
| UI 树 | `ui-dump` | Phase 2 WDA source | 待做 |

## 前置条件

1. **真机**：USB 连接、信任电脑、**开发者模式**开启  
2. **libimobiledevice**：`brew install libimobiledevice`（或放入 `vendor/bin/`）  
3. **WDA**：在设备上安装并启动 WebDriverAgent（Xcode 编译一次）  
4. **端口转发**（另开终端保持运行）：

```bash
export IOS_UDID=$(ioskit devices | head -1)
iproxy 8100 8100 -u "$IOS_UDID"
ioskit wda status
```

5. 可选：`export IOS_WDA_BUNDLE_ID=com.your.game`（Cocos 游戏建议设置）

## 安装

```bash
cd ioskit
pip install -e ".[dev]"
./scripts/setup.sh
```

## CLI

```bash
ioskit which
ioskit devices --json
ioskit shot --json
ioskit analyze
ioskit tap 200 400
ioskit swipe 200 600 200 200 --duration 0.4
ioskit wda status
ioskit wda proxy    # 打印 iproxy 命令
```

## Python

```python
from iphone_ctl import IOSDevice

dev = IOSDevice(bundle_id="com.example.app")
path = dev.screenshot()
dev.tap(540, 1200)
data = dev.analyze()
```

## 环境变量

| 变量 | 说明 |
|------|------|
| `IOS_UDID` | 设备 UDID |
| `IOS_WDA_URL` | WDA 地址，默认 `http://127.0.0.1:8100` |
| `IOS_WDA_BUNDLE_ID` | WDA session 用的 Bundle ID |
| `IOS_SHOT_DIR` | 截图目录，默认 `/tmp/ioskit` |

## WDA 安装（一次性）

与 Appium 相同，详见 **[iphone-ctl-skill/docs/WDA_SETUP.md](../iphone-ctl-skill/docs/WDA_SETUP.md)**。

```bash
./iphone-ctl-skill/scripts/setup-wda.sh
# Xcode → WebDriverAgentRunner → 真机 Run
iproxy 8100 8100 -u $IOS_UDID
```

## 相关

- [ios_skill](../ios_skill) — LLM Skill  
- [tgkit](../tg-notify) — 发 Telegram  

## License

MIT
