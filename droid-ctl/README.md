# adbkit

Android ADB 工具包：**`vendor/platform-tools` 随仓库分发**，clone 即可离线使用，无需联网。

独立 Python 包 + CLI，配套 LLM Skill 见 [adb_skill](../adb_skill)。

## 核心设计

| 方式 | 说明 |
|------|------|
| **默认（离线）** | `vendor/platform-tools/` 已包含在 git 仓库中 |
| **更新（联网）** | `adbkit install-tools --download` 从 Google 拉最新版 |

用户 `git clone` 后即有完整 adb，不依赖本机 Android SDK，也**不会自动联网**。

## 安装

```bash
git clone .../adbkit
cd adbkit
pip install -e ".[dev]"
adbkit which
# → .../droid-ctl/vendor/platform-tools/adb
```

## adb 解析顺序

1. `ADBKIT_ADB_PATH`
2. **`vendor/platform-tools/adb`**（仓库自带，离线）
3. `~/.droid-ctl/platform-tools/adb`（可选用户缓存）
4. `$ANDROID_HOME` / 系统 PATH（可选回退）

## 维护 / 更新

```bash
# 用户：更新本机 ~/.adbkit 缓存（可选）
adbkit install-tools --download

# 维护者：刷新仓库 vendor/ 以便下次发版（需联网）
adbkit install-tools --download --update-vendor
# 或
./scripts/vendor-platform-tools.sh --from-sdk
./scripts/vendor-platform-tools.sh --download
```

当前 `vendor/platform-tools/` 为 **macOS (darwin)**。Linux/Windows 维护者可填充 `vendor/platform-tools-linux` 等，或让用户 `--download`。

详见 [vendor/README.md](vendor/README.md)。

## CLI

```bash
adbkit devices
adbkit shot --json
adbkit analyze --ui
adbkit tap 540 1200
adbkit install app.apk
```

## Python API

```python
from droid_ctl import Device, screenshot, tap, analyze

dev = Device()
dev.screenshot()
dev.tap(540, 1200)
```

## 测试

```bash
pytest tests/ -q
```

## 相关项目

| 仓库 | 说明 |
|------|------|
| **adbkit**（本仓库） | Python 包 + CLI + **vendor platform-tools** |
| **adb_skill** | LLM Skill |
| **tgkit** / **tg_skill** | Telegram 远程 |

## License

MIT · platform-tools 见 `vendor/platform-tools/NOTICE.txt`（Google SDK）
