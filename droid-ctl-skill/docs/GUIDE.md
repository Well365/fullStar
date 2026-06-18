# adb_skill 使用指南

> Android 设备 ADB 控制 + AI 视觉分析 + Telegram 远程协作  
> 独立仓库，与 tg-notify / tg_skill 同级部署

---

## 目录

- [能做什么](#能做什么)
- [快速开始](#快速开始)
- [脚本一览](#脚本一览)
- [AI 视觉操作循环](#ai-视觉操作循环)
- [与 Telegram 远程协作](#与-telegram-远程协作)
- [故障排查](#故障排查)

---

## 能做什么

| 能力 | 脚本 |
|------|------|
| 设备截图（供 AI 看屏） | `adb-shot.sh` |
| UI 层次结构（坐标） | `adb-ui-dump.sh` |
| 截图 + UI 一并输出 | `adb-analyze.sh --ui` |
| 点击 / 滑动 / 输入 | `adb-tap.sh` `adb-swipe.sh` `adb-input.sh` |
| 按键（返回/Home） | `adb-key.sh` |
| 安装 APK / 启动应用 | `adb-install.sh` `adb-start.sh` |
| 截图发 Telegram | `adb-tg-shot.sh` |

推荐布局：

```
workspace/
├── droid-ctl-skill/     ← 本仓库
├── tg-notify-skill/
├── tg-notify/
└── mobile-agent/  ← .env（Telegram Token）
```

---

## 快速开始

### 1. 安装 adbkit（vendor 已随仓库自带 adb，无需联网）

```bash
git clone .../adbkit
pip install -e ../adbkit
adbkit which   # → .../droid-ctl/vendor/platform-tools/adb
```

更新 platform-tools（可选，需联网）：

```bash
adbkit install-tools --download
```

手机：**设置 → 开发者选项 → USB 调试** 打开，USB 连接 Mac，点「允许调试」。

### 2. 安装 Skill

```bash
cd adb_skill
chmod +x scripts/*.sh
./scripts/setup-all.sh
```

### 3. 验证

```bash
./scripts/adb-devices.sh
./scripts/check-env.sh
./scripts/adb-shot.sh --json
```

### 4. 在 Cursor 中使用

对 Agent 说：

> adb 截图分析当前界面

> 点击屏幕中央

> 把手机画面发到 Telegram

---

## 脚本一览

```bash
# 设备
./scripts/adb-devices.sh

# 截图（--json 输出路径给 AI 读图）
./scripts/adb-shot.sh --json
./scripts/adb-analyze.sh --ui

# 操作
./scripts/adb-tap.sh 540 1200
./scripts/adb-swipe.sh 540 1800 540 600 300
./scripts/adb-input.sh "hello"
./scripts/adb-key.sh BACK

# 应用
./scripts/adb-install.sh app.apk
./scripts/adb-start.sh com.pkg/.Activity

# Telegram
./scripts/adb-tg-shot.sh -c "验收截图"
```

多设备时：

```bash
export ADB_SERIAL=你的设备序列号
```

---

## AI 视觉操作循环

Agent 操作 Android 的标准流程：

```
┌─────────────┐
│  adb-shot   │  截图 → AI 读 PNG
└──────┬──────┘
       ▼
┌─────────────┐
│  分析界面    │  决定点哪里、滑哪里
└──────┬──────┘
       ▼
┌─────────────┐
│ tap / swipe │  执行操作
└──────┬──────┘
       ▼
┌─────────────┐
│  再截图验证  │  直到目标达成
└─────────────┘
```

需要精确定位时加 `--ui`：

```bash
./scripts/adb-analyze.sh --ui
# AI 同时读 PNG + XML 中的 bounds="[x1,y1][x2,y2]"
```

---

## 与 Telegram 远程协作

完整链路：**手机发 Telegram 指令 → 本机 Agent 执行 adb → 截图回传 Telegram**

```bash
# 同时配置 tg + adb
./scripts/setup-all.sh --with-tg
```

详见 [REMOTE_WORKFLOW.md](REMOTE_WORKFLOW.md)。

---

## 故障排查

| 现象 | 处理 |
|------|------|
| `no device connected` | 开 USB 调试；换线；`adb kill-server && adb start-server` |
| `unauthorized` | 手机上点允许 USB 调试 |
| `multiple devices` | `export ADB_SERIAL=...` |
| 截图全黑 | `adb-key.sh POWER` 唤醒屏幕 |
| `tgkit not found` | `pip install -e "../tg-notify[dotenv]"` |

```bash
./scripts/check-env.sh --with-tg
```

---

MIT · 配套 [tg-notify-skill/docs/GUIDE.md](../../tg-notify-skill/docs/GUIDE.md)
