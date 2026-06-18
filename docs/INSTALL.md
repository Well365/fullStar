# 安装指南 / Install Guide / インストール

> 依赖说明：[DEPENDENCIES.md](DEPENDENCIES.md) | 根脚本：[../scripts/README.md](../scripts/README.md) | TG 配置：[TELEGRAM_SETUP.md](TELEGRAM_SETUP.md)

| 语言 | 章节 |
|------|------|
| 简体中文 | [zh](#zh) |
| English | [en](#en) |
| 日本語 | [ja](#ja) |

---

<a id="zh"></a>

## 简体中文

### 我该用哪个脚本？

```
只想配 Telegram？          → ./mob tg-setup --test
要装全套（推荐首次）        → ./mob setup --test
只要 Agent Skill？         → ./mob install-skill [--only tg,adb,ios]
只要某一个 Python 包？      → 见下方「分模块安装」
```

### 总装（推荐）

```bash
cd mobile-agent
chmod +x mobagent mob-compose/compose mob-compose/scripts/*.sh scripts/*.sh tg-relay/setup-telegram.sh

# 1. Telegram（若尚未配置）
./mob tg-setup --test

# 2. Python 包 + Skills + 环境检查（可组合）
./mob setup --test                    # 全部
./mob setup --only tg,adb --test      # 仅 TG + Android
./mob setup --only ios --with-ios-wda # iOS + 编译 WDA

# 3. Agent Skills（setup 已包含，也可单独执行）
./mob install-skill
./mob check
```

**`mobagent setup` 实际调用：** `mob-compose/scripts/setup-all.sh`

| 选项 | 说明 |
|------|------|
| `--only tg,adb,ios` | 逗号分隔，只装指定模块 |
| `--with-ios-wda` | clone/编译 WebDriverAgent |
| `--test` | 发 TG 测试 + 设备冒烟 |
| `--token` / `--chat-id` | 写入 `.env` |
| `--project-dir` | `.env` 目录（默认包根） |

### 根目录 `scripts/`

| 脚本 | mobagent 别名 | 作用 |
|------|---------------|------|
| `setup-telegram.sh` | `tg-setup` | TG Token/ChatID + pip 依赖 |
| `install-skill.sh` | `install-skill` | 安装 Cursor/Claude Skills |
| `tg-relay.py` | `tg-start` | Bot 收令 |

详见 [../scripts/README.md](../scripts/README.md)。

### 分模块安装

#### tg-notify — `tg-notify/scripts/setup.sh`

```bash
./tg-notify/scripts/setup.sh
# pip install -e ./tgkit[dotenv]
```

#### tg_skill — `tg-notify-skill/scripts/setup-all.sh`

```bash
./tg-notify-skill/scripts/setup-all.sh --test
# tg-notify + .env + install-skill + check-env + 可选测试消息
```

| 选项 | 说明 |
|------|------|
| `--project-dir` | `.env` 目录（默认 cwd） |
| `--token` / `--chat-id` | 非交互写入 |
| `--test` | 发测试消息 |
| `--non-interactive` | 无 token 则失败 |

#### droid-ctl — `droid-ctl/scripts/setup.sh`

```bash
./droid-ctl/scripts/setup.sh
adbkit install-tools   # 下载 platform-tools 到 ~/.adbkit
```

#### adb_skill — `droid-ctl-skill/scripts/setup-all.sh`

```bash
./droid-ctl-skill/scripts/setup-all.sh
./droid-ctl-skill/scripts/setup-all.sh --with-tg --test
```

| 选项 | 说明 |
|------|------|
| `--with-tg` | 同时跑 tg_skill setup |
| `--test` | `adbkit shot --json` |

#### iphone-ctl — `iphone-ctl/scripts/setup.sh`

```bash
brew install libimobiledevice
./iphone-ctl/scripts/setup.sh
```

#### ios_skill — `iphone-ctl-skill/scripts/setup-all.sh`

```bash
./iphone-ctl-skill/scripts/setup-all.sh
# pip install iphone-ctl + install-skill + check-env
```

WDA 辅助：

```bash
./iphone-ctl-skill/scripts/setup-wda.sh          # clone WDA + 打开 Xcode
./mob-compose/scripts/build-wda.sh             # xcodebuild（需 IOS_DEVELOPMENT_TEAM）
./mob ios-start                      # iproxy 后台
```

#### devkit 日常脚本 — `mob-compose/scripts/`

| 脚本 | mobagent | 作用 |
|------|----------|------|
| `setup-all.sh` | `setup` | 总装 |
| `check-env.sh` | `check` | 环境检查 |
| `shot-android.sh` | `shot-android` | Android 截图→TG |
| `shot-ios.sh` | `shot-ios` | iOS 截图→TG |
| `start-ios-proxy.sh` | `ios-start` | 启动 iproxy |
| `stop-ios-proxy.sh` | `ios-stop` | 停止 iproxy |
| `build-wda.sh` | `build-wda` | 编译 WDA 到真机 |

### 常见组合速查

| 场景 | 命令 |
|------|------|
| 仅 TG 通知 | `./mob setup --only tg --test` |
| Android 远程验收 | `./mob setup --only tg,adb --test` |
| iOS 远程验收 | `./mob setup --only tg,ios --test` + `./mob ios-start` |
| 双端本地 | `./mob setup --only adb,ios` |
| 全栈 | `./mob setup --test` + `./mob tg-start` |

更多组合：[SKILL_COMPOSE.md](SKILL_COMPOSE.md)

---

<a id="en"></a>

## English

### Which script?

| Goal | Command |
|------|---------|
| Telegram only | `./mob tg-setup --test` |
| Full first-time setup | `./mob setup --test` |
| Skills only | `./mob install-skill [--only tg,adb,ios]` |

### Full setup

```bash
cd mobile-agent
chmod +x mobagent mob-compose/compose mob-compose/scripts/*.sh scripts/*.sh tg-relay/setup-telegram.sh
./mob tg-setup --test
./mob setup --test
./mob check
```

`mobagent setup` → `mob-compose/scripts/setup-all.sh` with `--only`, `--with-ios-wda`, `--test`.

### Per-module scripts

| Path | Installs |
|------|----------|
| `tg-notify/scripts/setup.sh` | pip tg-notify |
| `tg-notify-skill/scripts/setup-all.sh` | tg-notify + .env + skills |
| `droid-ctl/scripts/setup.sh` | pip droid-ctl + adb tools |
| `droid-ctl-skill/scripts/setup-all.sh` | droid-ctl + skill (`--with-tg`) |
| `iphone-ctl/scripts/setup.sh` | pip iphone-ctl |
| `iphone-ctl-skill/scripts/setup-all.sh` | iphone-ctl + skill |
| `iphone-ctl-skill/scripts/setup-wda.sh` | clone/open WDA |
| `mob-compose/scripts/setup-all.sh` | orchestrates above |
| `tg-relay/setup-telegram.sh` | TG config only |

### devkit daily commands

`check` · `shot-android` · `shot-ios` · `ios-start` · `build-wda`

See [../scripts/README.md](../scripts/README.md).

---

<a id="ja"></a>

## 日本語

### どのスクリプトを使う？

| 目的 | コマンド |
|------|----------|
| Telegram のみ | `./mob tg-setup --test` |
| 初回フルセットアップ | `./mob setup --test` |
| Skill のみ | `./mob install-skill [--only tg,adb,ios]` |

### フルセットアップ

```bash
cd mobile-agent
chmod +x mobagent mob-compose/compose mob-compose/scripts/*.sh scripts/*.sh tg-relay/setup-telegram.sh
./mob tg-setup --test
./mob setup --test
./mob check
```

### モジュール別スクリプト

| パス | 内容 |
|------|------|
| `tg-notify/scripts/setup.sh` | pip tg-notify |
| `tg-notify-skill/scripts/setup-all.sh` | tg-notify + .env + skills |
| `droid-ctl/scripts/setup.sh` | pip droid-ctl + adb |
| `droid-ctl-skill/scripts/setup-all.sh` | droid-ctl + skill |
| `iphone-ctl/scripts/setup.sh` | pip iphone-ctl |
| `iphone-ctl-skill/scripts/setup-all.sh` | iphone-ctl + skill |
| `mob-compose/scripts/setup-all.sh` | 全体オーケストレーション |
| `tg-relay/setup-telegram.sh` | TG 設定のみ |

詳細：[DEPENDENCIES.md](DEPENDENCIES.md) · [SKILL_COMPOSE.md](SKILL_COMPOSE.md)
