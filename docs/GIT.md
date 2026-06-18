# 独立 Git 仓库说明 / Standalone Git Repository

`mobile-agent` 为**自包含 Git 仓库**，与 `cc-shells` 等业务项目无关。

## 初始化（维护者）

```bash
cd mobile-agent
git init
git add .
git status   # 确认 .env / devkit.env 未出现

# 提交前检查敏感信息
chmod +x scripts/verify-no-secrets.sh
./scripts/verify-no-secrets.sh

git commit -m "chore: initial mobile-agent standalone repository"
```

## 绝不提交的文件

| 文件 | 内容 |
|------|------|
| `.env` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| `mob-compose/compose.env` | `IOS_UDID`, `IOS_DEVELOPMENT_TEAM`, 内网 IP |
| `inbox/` | Telegram 自然语言待办 |
| `iphone-ctl/.venv-pymd/` | 本地 Python 虚拟环境 |

模板文件 **可以** 提交：`.env.example`、`devkit.env.example`

## 克隆后配置

```bash
git clone <your-remote> mobile-agent
cd mobile-agent
./mob tg-setup --test
cp mob-compose/compose.env.example mob-compose/compose.env   # iOS 需要时编辑
./mob setup --test
```

## 嵌套仓库处理

原 `tg-notify/`、`tg-notify-skill/`、`WebDriverAgent/` 曾各有独立 `.git`，  
已合并为单一仓库（删除子目录 `.git`）。历史 remote 若需保留请自行备份。

## 推送前检查

```bash
./scripts/verify-no-secrets.sh
git diff --cached --name-only | grep -E '\.env$|devkit\.env$' && echo 'STOP' || echo 'OK'
```

MIT
