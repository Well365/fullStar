# adb_skill — Android ADB 操作 Skill

通过 **adbkit** 控制 Android 真机/模拟器（**自带 platform-tools 下载**，新电脑无需预装 adb）。

可与 **tg_skill + tgkit** 组合实现 Telegram 远程发令 → 本机 AI 操作手机 → 截图回传。

> **adbkit（能力层）→ [../adbkit](../adbkit)**  
> **使用指南 → [docs/GUIDE.md](docs/GUIDE.md)**

## 架构

```
Telegram（远程指令）  →  本机 AI Agent（Cursor / Claude）
                              ↓
                    droid-ctl-skill/scripts/*
                              ↓
                         Android 设备
                              ↓
                    tg-notify 回传截图（可选）
```

| 仓库 | 职责 |
|------|------|
| **adbkit** | Python 包 + CLI + platform-tools 自动安装 |
| **adb_skill** | LLM Skill + shell 包装（调 adbkit） |
| **tg_skill** / **tgkit** | Telegram 远程 |

## 一键安装

```bash
cd adb_skill
./scripts/setup-all.sh --with-tg   # 安装 droid-ctl + Skill + 可选 tgkit
```

## 快速验证

```bash
./scripts/adb-devices.sh
./scripts/adb-shot.sh --json
./scripts/adb-analyze.sh --ui
```

## 目录结构

```
droid-ctl-skill/
├── SKILL.md              # Agent 主 Skill
├── reference.md          # 命令参考
├── examples.md           # 场景示例
├── docs/
│   ├── GUIDE.md          # 使用指南
│   └── REMOTE_WORKFLOW.md
├── scripts/
│   ├── adb-shot.sh       # 截图
│   ├── adb-analyze.sh    # 截图 + UI dump（AI 分析）
│   ├── adb-tg-shot.sh    # 截图发 Telegram
│   ├── adb-tap.sh        # 点击
│   ├── adb-swipe.sh      # 滑动
│   ├── adb-input.sh      # 输入文字
│   ├── adb-key.sh        # 按键
│   ├── adb-ui-dump.sh    # UI 层次结构
│   ├── adb-install.sh    # 安装 APK
│   ├── adb-start.sh      # 启动 Activity
│   ├── setup-all.sh
│   ├── check-env.sh
│   └── install-skill.sh
└── platforms/
    └── cursor.md
```

## Agent 示例指令

- 「adb 截图分析一下现在是什么界面」
- 「在手机上点击登录按钮」（Agent 会先截图 → 分析坐标 → tap）
- 「把当前手机画面发到 Telegram」
- 「安装这个 apk 并启动」

## License

MIT
