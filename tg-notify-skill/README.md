# tg-notify Skill

跨平台 LLM Skill：教 Agent 通过 **tgkit CLI** 发送 Telegram 通知、文件和 macOS 截图。

本目录 **仅包含 Skill 文档与 shell 包装脚本**，为 mobile-agent 自包含包的一部分。  
实际发送能力来自同包内的 Python 包 **[tgkit](../tg-notify)**。

> **完整使用文档 → [docs/GUIDE.md](docs/GUIDE.md)**  
> 涵盖安装、配置、CLI、Python API、Agent 集成与故障排查。

## 目录结构

```
tg-notify-skill/
├── SKILL.md           # 主 Skill（复制到 Cursor / Claude Code）
├── reference.md       # 完整命令参考
├── .env.example
├── README.md
├── scripts/
│   ├── setup-all.sh       # ★ 一键完整配置
│   ├── check-env.sh       # 环境检查
│   ├── load-env.sh        # 向上查找 .env
│   ├── tg-notify.sh       # 发消息/文件/图片
│   ├── tg-screenshot.sh   # 截屏发送
│   └── install-skill.sh   # 安装到 ~/.cursor/skills 与 ~/.claude/skills
└── platforms/
    ├── cursor.md
    ├── claude-code.md
    └── chatgpt.md
```

## 一键配置（推荐）

```bash
chmod +x scripts/*.sh

# 完整配置：安装 tg-notify + 写 .env + 安装 Cursor/Claude Skill + 校验
./scripts/setup-all.sh --project-dir ..

# 配置 mobile-agent 并发送测试消息
./scripts/setup-all.sh --test

# 非交互（CI / 已有 token）
./scripts/setup-all.sh \
  --token "YOUR_BOT_TOKEN" --chat-id 123456789 --non-interactive --test
```

仅检查当前环境：

```bash
./scripts/check-env.sh
```

## 快速开始（手动分步）

### 1. 安装 tgkit（Python）

```bash
pip install "tg-notify[dotenv]"
```

若尚未发布 PyPI，从 tg-notify 源码安装（与 tg_skill 同级目录）：

```bash
pip install -e "../tg-notify[dotenv]"
# 或
pip install "git+https://YOUR_GIT/tg_notify.git#egg=tgkit[dotenv]"
```

### 2. 配置 .env

```bash
cp .env.example .env
# 编辑 TELEGRAM_BOT_TOKEN、TELEGRAM_CHAT_ID
```

### 3. 安装 Skill 到 Agent

```bash
chmod +x scripts/*.sh
./scripts/install-skill.sh
```

或手动复制：

```bash
mkdir -p ~/.cursor/skills/tgkit ~/.claude/skills/tgkit
cp SKILL.md reference.md ~/.cursor/skills/tg-notify/
cp SKILL.md reference.md ~/.claude/skills/tg-notify/
```

### 4. 验证

```bash
tgkit send "tg_skill 测试"
./scripts/tg-notify.sh "wrapper 测试"
```

在 Cursor / Claude Code 中对 Agent 说：

> 用 tg-notify 给 Telegram 发消息：Skill 安装成功

## 与 tg-notify 的关系

| 仓库 | 内容 |
|------|------|
| **tgkit** | Python 包 + CLI（`pip install tgkit`） |
| **tg_skill**（本仓库） | LLM Skill 文档 + 便捷脚本 |
| **adb_skill** | Android ADB 远程操作 + 截图 AI 分析（见 [adb_skill](../adb_skill)） |

Skill 不包含 Bot Token，配置写在 `mobile-agent/.env`。

## 独立 Git 仓库

本目录设计为单独 `git init` / 推送到独立 remote：

```bash
cd tg_skill
git init
git add SKILL.md reference.md README.md .env.example scripts/ platforms/ .gitignore
git commit -m "feat: tg-notify lightweight LLM skill (plan A)"
```

## License

MIT（与 tg-notify 保持一致即可）
