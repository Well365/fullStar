# Claude Code

## Install

```bash
git clone https://YOUR_GIT/tg_skill.git
cd tg_skill
./scripts/install-skill.sh
```

安装目标：`~/.claude/skills/tg-notify/SKILL.md`

## Usage

在 Claude Code 会话中：

```
/tgkit 发消息：部署完成
```

或直接自然语言（若 skill 已被加载）：

> 用 tg-notify 把这段日志发到 Telegram：……

## Prerequisites

```bash
pip install "tg-notify[dotenv]"
cp .env.example .env   # 在项目目录配置 token
```

## macOS 截图

需要为运行 Claude Code 的终端授予 **辅助功能** 与 **屏幕录制** 权限。
