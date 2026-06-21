# docs/ — 文档索引 / Documentation Index

| 文档 | 语言 | 内容 |
|------|------|------|
| [FEATURES.md](FEATURES.md) | 中文 | **新增功能清单** — /new、命令菜单、会话控制、自动兜底、白名单 |
| [GIT.md](GIT.md) | 中文 | **独立 Git 仓库**与敏感信息排除 |
| [INSTALL.md](INSTALL.md) | 中 / En / 日 | **一键安装脚本**总览与各模块 setup |
| [DEPENDENCIES.md](DEPENDENCIES.md) | 中 / En / 日 | **各目录依赖**（pip / 系统 / 硬件） |
| [TELEGRAM_SETUP.md](TELEGRAM_SETUP.md) | 中 / En / 日 | Telegram Token / Chat ID 配置 |
| [ITERM_MULTI_TAB.md](ITERM_MULTI_TAB.md) | 中文 | **iTerm 多标签页路由** — Telegram 指定 tab、前缀用法 |
| [TG_ITERM_AI_FLOW.html](TG_ITERM_AI_FLOW.html) · [En](TG_ITERM_AI_FLOW.en.html) · [日](TG_ITERM_AI_FLOW.ja.html) | 中 / En / 日 | **可视化流程说明页** — 架构图 + 消息生命周期 + 完成判定 |
| [SKILL_COMPOSE.md](SKILL_COMPOSE.md) | 中文 | Skill 组合安装场景 |
| [TASKS.md](TASKS.md) | 中文 | 任务清单 / 路线图 |
| [NAMING.md](NAMING.md) | 中文 | 命名约定 |

## 快速链接

```bash
# 一键（推荐）
./oneClickSetup.sh         # 自动 chmod + 准备 .env + ./mob setup + ./mob check
./oneClickStart.sh         # 一键开启全部服务（relay + monitor），--stop 关闭

# 首次安装（手动分步）
./mob tg-setup --test      # Telegram
./mob setup --test         # 全套
./mob install-skill        # Agent Skills
./mob check                # 验证

# 文档
cat docs/INSTALL.md
cat docs/DEPENDENCIES.md
```

## 子模块文档

| 模块 | 路径 |
|------|------|
| tg-notify | `tg-notify/README.md`, `tg-notify-skill/docs/GUIDE.md` |
| adb | `droid-ctl/README.md`, `droid-ctl-skill/docs/GUIDE.md` |
| iOS / WDA | `iphone-ctl/README.md`, `iphone-ctl-skill/docs/WDA_SETUP.md` |
| 远程工作流 | `droid-ctl-skill/docs/REMOTE_WORKFLOW.md` |
| devkit | `mob-compose/README.md` |
| 根脚本 | `scripts/README.md` |
