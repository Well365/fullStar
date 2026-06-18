---
name: mobile-agent
description: >-
  通过 Telegram 远程控制自动化 Android 与 iOS 真机。可与子 Skill tg、adb、ios 自由组合，按需安装。
  适用于远程手机控制、TG 设备操作、移动端验收、WDA 点击、Telegram adb 截图，或 mobile-agent/mobagent 工作流。
  iOS 仅支持 macOS。
disable-model-invocation: true
---

# mobile-agent — Telegram + Android + iOS

通过 **Telegram** 实现**远程移动设备自动化**的统一 Skill。

包根目录：`mobile-agent/` — 自包含，无需外部项目。

## 可组合 Skill

各子 Skill **独立**，可任意组合安装：

| Skill | 单独使用场景 | 常搭配 |
|-------|-------------|--------|
| **tg** | 仅发送 TG 通知 | adb、ios |
| **adb** | Android USB 自动化 | tg（远程验收） |
| **ios** | iPhone + WDA 自动化 | tg（远程验收） |
| **mobile-agent** | 完整编排文档 | 以上全部 |

```bash
./mob install-skill --only tg          # 仅 Telegram
./mob install-skill --only adb,ios     # 双平台，不含 TG Skill
./mob install-skill --only tg,adb    # Android 远程验收
./mob install-skill                    # 全部安装

./mob setup --only tg,adb
```

组合配方见 [docs/SKILL_COMPOSE.md](docs/SKILL_COMPOSE.md)。

Agent 规则：仅加载与任务相关的 Skill（tg / adb / ios）。  
子 Skill 详情：`tg-notify-skill/SKILL.md`、`droid-ctl-skill/SKILL.md`、`iphone-ctl-skill/SKILL.md`。

## 组件

| 部分 | 路径 | 作用 |
|------|------|------|
| **mobagent** | `./mob` | 统一 CLI 入口 |
| **devkit** | `mob-compose/` | setup / check / shot-android / shot-ios |
| **adbkit + adb_skill** | `droid-ctl/`、`droid-ctl-skill/` | Android 控制 |
| **ioskit + ios_skill** | `iphone-ctl/`、`iphone-ctl-skill/` | iOS 控制（WDA） |
| **tgkit + tg_skill** | `tg-notify/`、`tg-notify-skill/` | Telegram 发送 |
| **tg-relay** | `tg-relay.py` | 接收 TG 指令 |
| **WebDriverAgent** | `WebDriverAgent/` | iOS 点击/滑动 |
| **game-qa-autopilot** | `game-qa-autopilot/` | 浏览器游戏 QA（可选） |

## 一次性配置

```bash
cd mobile-agent
chmod +x mobagent mob-compose/compose mob-compose/scripts/*.sh scripts/*.sh

cp .env.example .env
./mob setup --test
./mob install-skill
./mob check
```

iOS 日常使用：`./mob ios-start`，并确保设备上已运行 WDA Runner。

## 三种运行模式

### A. Agent + TG 发送（默认）

用户在 Cursor 粘贴 TG 指令 → Agent 执行设备脚本 → 通过 `tg-notify` 发送结果。

```
TG 指令 → Agent → droid-ctl/ioskit → tg-notify send --photo
```

### B. TG Bot 指令（半自动）

```bash
./mob tg-start
```

Bot 命令：`/shot android`、`/shot ios`、`/tap 540 1200`、`/swipe ...`、`/check`、`/devices`  
自然语言 → 写入 `inbox/pending.txt` → Agent 读取 `./mob tg-inbox`。

### C. 视觉循环（全自动）

```
1. shot --json          → 读取 PNG
2. 分析画面             → 决定 x,y
3. tap / swipe          → 执行操作
4. shot --json          → 验证结果
5. tg-notify send --photo   → 向用户汇报
```

## Agent 工作流

1. 运行 `./mob check` — 先修复缺失工具/设备。
2. 选择平台：**android**（`droid-ctl`）或 **ios**（`iphone-ctl` + WDA + iproxy）。
3. 点击后**务必重新截图**以验证。
4. 发送结果：`./mob shot-android -c "..."` 或 `tgkit send --photo`。
5. 切勿打印 `TELEGRAM_BOT_TOKEN`。

## 常用命令

```bash
# 环境
./mob check
./mob ios-start

# 截图 → Telegram
./mob shot-android -c "Android 验收"
./mob shot-ios -c "iOS 验收"

# 直接 CLI
adbkit shot --json && droid-ctl tap 540 1200
ioskit shot --json && iphone-ctl tap 540 1200

# TG 监听
./mob tg-start
./mob tg-inbox
```

## 坐标提示

- 原点 (0,0) 在左上角；从 `shot --json` 的 `screen` 字段获取尺寸
- Cocos 游戏：使用**图像坐标**，不要用元素 id
- iOS 游戏：在 `mob-compose/compose.env` 中设置 `IOS_WDA_BUNDLE_ID`

## 安全

- 破坏性操作前与用户确认
- 远程 tap/swipe 使用测试设备
- 不要提交 `.env` 或 token

## 故障排查

| 问题 | 处理 |
|------|------|
| 无 Android 设备 | 开启 USB 调试；`adbkit devices` |
| WDA 未就绪 | Xcode Run WDA Runner；`./mob ios-start` |
| TG token 缺失 | `mobile-agent/.env`（从 `.env.example` 复制） |
| 点击无效（iOS） | 设置 `IOS_WDA_BUNDLE_ID`；应用需在前台 |

## 子 Skill（单独安装）

| Skill | 安装 | 文档 |
|-------|------|------|
| tg | `./mob install-skill --only tg` | `tg-notify-skill/SKILL.md` |
| adb | `./mob install-skill --only adb` | `droid-ctl-skill/SKILL.md` |
| ios | `./mob install-skill --only ios` | `iphone-ctl-skill/SKILL.md` |

## 更多资料

- [docs/SKILL_COMPOSE.md](docs/SKILL_COMPOSE.md) — **组合安装与场景**
- [README.md](README.md) — 完整包指南
- `droid-ctl-skill/docs/REMOTE_WORKFLOW.md` — TG 远程架构
- `iphone-ctl-skill/docs/WDA_SETUP.md` — iOS WDA 配置

## 其他语言

- [English](SKILL.md)
- [日本語](mob-remote-skill/SKILL.ja.md)
