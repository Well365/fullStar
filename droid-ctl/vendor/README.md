# platform-tools (Android SDK)

本目录随 **adbkit** 仓库一起分发，clone 后即可离线使用，**无需联网下载**。

## 布局

| 路径 | 说明 |
|------|------|
| `vendor/platform-tools/` | 默认目录（当前为 **macOS / darwin**） |
| `vendor/platform-tools-linux/` | 可选：Linux 版（维护者填充） |
| `vendor/platform-tools-windows/` | 可选：Windows 版（维护者填充） |

`adbkit` 会按当前系统自动选择对应 vendor 目录。

## 用户

```bash
git clone .../adbkit
pip install -e ./adbkit
adbkit which    # → .../adbkit/vendor/platform-tools/adb
```

## 维护者：刷新 vendor

从本机 SDK 复制（macOS 示例）：

```bash
./scripts/vendor-platform-tools.sh --from-sdk
```

从 Google 下载最新版并写入 vendor（需联网，用于发版更新）：

```bash
./scripts/vendor-platform-tools.sh --download
```

更新用户本机缓存（不影响仓库 vendor）：

```bash
adbkit install-tools --download
```

## 许可

platform-tools 来自 Google Android SDK，见目录内 `NOTICE.txt`。
