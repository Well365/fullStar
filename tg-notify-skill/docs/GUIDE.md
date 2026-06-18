# tg-notify 使用指南

> 独立 Telegram 通知工具链：**tgkit**（Python 包）+ **tg_skill**（LLM Skill 与脚本）  
> 版本 tg-notify `0.1.2` · macOS / Linux · 截图仅 macOS

**文档路径：** `tg-notify-skill/docs/GUIDE.md`

---

## 目录

- [架构概览](#架构概览)
- [5 分钟快速开始](#5-分钟快速开始)
- [安装与配置](#安装与配置)
- [CLI 与 Python API](#cli-与-python-api)
- [LLM Agent](#llm-agent)
- [独立部署](#独立部署)
- [故障排查](#故障排查)

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│  Cursor / Claude Code / ChatGPT                             │
│       ↓ 读取 SKILL.md                                        │
├─────────────────────────────────────────────────────────────┤
│  tg_skill（编排层）                                          │
│  setup-all.sh · check-env.sh · tg-notify.sh · tg-screenshot │
├─────────────────────────────────────────────────────────────┤
│  tgkit（能力层）                                             │
│  CLI: tg-notify send / screenshot                               │
│  API: text() · file() · photo() · app_screenshot()          │
├─────────────────────────────────────────────────────────────┤
│  mobile-agent/                                               │
│  .env · mobagent · devkit                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
                  Telegram Bot API
```

| 组件 | 职责 | 典型用户 |
|------|------|----------|
| **tgkit** | Python 包 + CLI | 开发者、CI、构建脚本 |
| **tg_skill** | Skill 文档 + shell 脚本 | Agent 用户、一键部署 |
| **mobile-agent** | 自包含封装包 | 远程验收、设备自动化 |

推荐布局（mobile-agent 内）：

```
mobile-agent/
├── .env           # Telegram Token
├── tg-notify/
├── tg-notify-skill/
├── droid-ctl/ + droid-ctl-skill/
└── iphone-ctl/ + iphone-ctl-skill/
```

---

## 5 分钟快速开始

### 人类开发者（只要发消息）

```bash
cd mobile-agent
pip install -e "./tgkit[dotenv]"
cp .env.example .env   # 填入 TOKEN 和 CHAT_ID
tgkit send "Hello ✓"
```

### 一键配置（含 Agent Skill）

```bash
cd mobile-agent
chmod +x mobagent mob-compose/compose mob-compose/scripts/*.sh scripts/*.sh
cp .env.example .env
./mob setup --only tg --test
```

### 环境检查

```bash
./mob check
# 或
./tg-notify-skill/scripts/check-env.sh
```

---

## 安装与配置

### 安装 tgkit

| 方式 | 命令 |
|------|------|
| 本地开发 | `pip install -e "./tgkit[dotenv]"` |
| PyPI | `pip install "tg-notify[dotenv]"` |
| Git | `pip install "git+https://YOUR_GIT/tg_notify.git#egg=tgkit[dotenv]"` |
| mobagent | `./mob setup --only tg` |

### .env 配置

```bash
TELEGRAM_BOT_TOKEN=从@BotFather获取
TELEGRAM_CHAT_ID=你的chat_id
TGKIT_CONFIG_PATH=config.json
```

| 变量 | 必填 | 说明 |
|------|:----:|------|
| `TELEGRAM_BOT_TOKEN` | ✓ | Bot Token |
| `TELEGRAM_CHAT_ID` | 推荐 | 默认接收者 |
| `TGKIT_CONFIG_PATH` | — | JSON 中的 `chat_id` 作后备 |

**Chat ID 获取：** 给 Bot 发消息后访问  
`https://api.telegram.org/bot<TOKEN>/getUpdates`

**优先级：** CLI `--chat-id` → 环境变量 → config.json

---

## CLI 与 Python API

### CLI

```bash
# 文本 / 图片 / 文件
tgkit send "构建完成"
tgkit send --photo out.png --caption "UI"
tgkit send --file build.log

# 截屏（macOS）
tgkit screenshot
tgkit screenshot --mode interactive
tgkit screenshot --app Calculator --wait 3
tgkit screenshot --app-path "/Applications/Safari.app"
```

### Python

```python
from tg_notify import text, file, photo, screenshot, app_screenshot
from tg_notify.notify import notify

text("构建完成")
notify.file("build.log")
app_screenshot(app="Calculator", wait_seconds=2)
```

### Shell 包装

```bash
./tg-notify-skill/scripts/tg-notify.sh "消息"
./tg-notify-skill/scripts/tg-screenshot.sh --app Calculator
```

---

## LLM Agent

```bash
cd tg_skill && ./scripts/install-skill.sh
```

安装到 `~/.cursor/skills/tgkit` 与 `~/.claude/skills/tgkit`。

对 Agent 说：

- 「用 tg-notify 发 Telegram：构建完成」
- 「截取 Calculator 发到 Telegram」
- 「把 build.log 发到 Telegram」

详见 `SKILL.md`、`reference.md`、`platforms/cursor.md`。

---

## 独立部署

mobile-agent 是自包含包，`.env` 放在包根目录：

```bash
cp .env.example .env
./mob setup --test
```

**构建脚本示例：**

```python
from tg_notify.notify import notify
notify.text("Android 构建完成 ✅")
```

**CI 非交互：**

```bash
./mob setup --only tg \
  --token "$TELEGRAM_BOT_TOKEN" --chat-id "$CHAT_ID" \
  --non-interactive --test
```

也可通过 `TGKIT_ENV_FILE` 指向外部 `.env`（可选）。

---

## macOS 截图权限

系统设置 → 隐私与安全性 → **辅助功能** + **屏幕录制** → 授权 Terminal/Cursor。

`-1728` 错误时 tg-notify 自动降级为区域截图。

---

## 故障排查

| 现象 | 处理 |
|------|------|
| `.env not found` | `cp .env.example .env` 后 `./mob setup` |
| `tgkit not found` | `pip install -e "./tgkit[dotenv]"` |
| `TOKEN empty` | 编辑 `.env` |
| `Process not running` | 增大 `--wait`，注意应用名大小写 |
| Bot 无响应 | @BotFather 检查 token；给 Bot 发 /start |

```bash
./mob check
```

---

## 常见问题

- **两仓库必须同级？** 不必，`--tgkit-path` 可指定路径。
- **不用 Skill？** 只装 tg-notify + `.env` 即可。
- **Linux？** 发消息全平台；截图仅 macOS。
- **Token 泄露？** @BotFather `/revoke` 后更新 `.env`。

---

MIT License · 详见 `tg-notify/README.md` 与 `tg-notify-skill/README.md`
