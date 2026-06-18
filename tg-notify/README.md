# tgkit

通用 Telegram 通知 Python 包：发文字、文件、图片，以及 macOS 截屏发送到 Telegram。

自包含 Python 包，属于 mobile-agent 的一部分。  
配套 LLM Skill 见 [tg_skill](../tg_skill)。

> **完整使用文档 → [tg-notify-skill/docs/GUIDE.md](../tg-notify-skill/docs/GUIDE.md)**  
> 两个独立仓库的安装、配置、CLI、Python API 与 Agent 集成说明。

## 安装

```bash
pip install "tg-notify[dotenv]"
```

或一键（仅 Python 包）：

```bash
./scripts/setup.sh
```

完整配置（含 .env + LLM Skill）：

```bash
cd mobile-agent
cp .env.example .env
./mob setup --only tg --test
```

开发模式（本仓库）：

```bash
git clone https://YOUR_GIT/tg_notify.git
cd tgkit
pip install -e ".[dotenv]"
```

作为 mobile-agent 内本地依赖：

```bash
pip install -e "./tgkit[dotenv]"
```

## 配置

```bash
cp .env.example .env
```

| 变量 | 必填 | 说明 |
|------|------|------|
| `TELEGRAM_BOT_TOKEN` | 是 | @BotFather 获取 |
| `TELEGRAM_CHAT_ID` | 推荐 | 默认接收 chat id |
| `TGKIT_CONFIG_PATH` | 否 | 含 `chat_id` 的 JSON 路径 |

## Python API

```python
from tg_notify import text, file, photo, screenshot, app_screenshot

text("构建完成")
file("build.log")
photo("shot.png", caption="结果")
screenshot()
app_screenshot(app="Calculator", wait_seconds=2)
app_screenshot(app_path="/Applications/CocosCreator.app", wait_seconds=5)
```

## CLI

```bash
tgkit send "deploy done"
tgkit send --photo out.png --caption "UI"
tgkit send --file build.log
tgkit screenshot
tgkit screenshot --app Calculator --wait 3
tgkit screenshot --app-path "/Applications/Telegram.app"
```

## macOS 截图权限

- 系统设置 → 隐私与安全性 → **辅助功能** → 授权终端
- 系统设置 → 隐私与安全性 → **屏幕录制** → 授权终端

部分 SwiftUI 应用不支持 window id 截屏时，tgkit 会自动降级为区域截图。

## 测试

```bash
pip install -e ".[dotenv]" pytest
pytest tests/ -q
```

## 相关项目

| 仓库 | 说明 |
|------|------|
| **tgkit**（本仓库） | Python 包 + CLI |
| **tg_skill** | Cursor / Claude Code LLM Skill |
| **adb_skill** | Android ADB 控制 + AI 截图分析（见 [droid-ctl-skill/docs/GUIDE.md](../droid-ctl-skill/docs/GUIDE.md)） |

## License

MIT
