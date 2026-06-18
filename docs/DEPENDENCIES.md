# Dependencies / 依赖 / 依存関係

> Install scripts: [INSTALL.md](INSTALL.md) | Scripts index: [../scripts/README.md](../scripts/README.md)

| Lang | Section |
|------|---------|
| 中文 | [zh](#zh) |
| EN | [en](#en) |
| 日本語 | [ja](#ja) |

<a id="zh"></a>
## 中文 — 系统依赖

| 功能 | 依赖 | 安装 |
|------|------|------|
| Python CLI | Python ≥3.9 | `brew install python` |
| TG 发送 | tgkit, python-telegram-bot | `./mob tg-setup` |
| TG 收令 | python-telegram-bot ≥20 | `./tg-relay/setup-telegram.sh` |
| Android | adb (platform-tools) | `./mob setup --only adb` |
| iOS USB | libimobiledevice | `brew install libimobiledevice` |
| iOS 自动化 | WDA + iproxy | Xcode, `./mob ios-start` |

### 目录依赖

| 目录 | pip 依赖 | 系统/硬件 | 一键安装 |
|------|----------|-----------|----------|
| `tg-notify/` | python-telegram-bot, python-dotenv | macOS 截图权限 | `tg-notify/scripts/setup.sh` |
| `tg-notify-skill/` | 依赖 tg-notify | `.env` | `tg-notify-skill/scripts/setup-all.sh` |
| `droid-ctl/` | 无 | adb, USB Android | `droid-ctl/scripts/setup.sh` |
| `droid-ctl-skill/` | droid-ctl (+tgkit 可选) | bash | `droid-ctl-skill/scripts/setup-all.sh` |
| `iphone-ctl/` | 无 | libimobiledevice, WDA:8100 | `iphone-ctl/scripts/setup.sh` |
| `iphone-ctl-skill/` | iphone-ctl | WDA, tg-notify 可选 | `iphone-ctl-skill/scripts/setup-all.sh` |
| `mob-compose/` | 编排上述 | `.env`, devkit.env | `mob-compose/scripts/setup-all.sh` → `./mob setup` |
| `WebDriverAgent/` | — | Xcode, iPhone | `iphone-ctl-skill/scripts/setup-wda.sh` |
| `scripts/` | python-telegram-bot | — | `tg-relay/setup-telegram.sh` → `./mob tg-setup` |

### 配置与检查脚本

| 模块 | check 脚本 |
|------|------------|
| 全局 | `mob-compose/scripts/check-env.sh` → `./mob check` |
| tg | `tg-notify-skill/scripts/check-env.sh` |
| adb | `droid-ctl-skill/scripts/check-env.sh` |
| ios | `iphone-ctl-skill/scripts/check-env.sh` |

<a id="en"></a>
## English

| Feature | Deps | Install |
|---------|------|---------|
| Python CLIs | Python ≥3.9 | system python |
| TG send | tg-notify | `./mob tg-setup` |
| TG bot | python-telegram-bot | `./tg-relay/setup-telegram.sh` |
| Android | adb | `./mob setup --only adb` |
| iOS | libimobiledevice, WDA | brew + Xcode |

Per-dir install scripts: see [INSTALL.md](INSTALL.md).

| Directory | pip | system | one-click |
|-----------|-----|--------|-----------|
| tg-notify | python-telegram-bot | macOS perms | `tg-notify/scripts/setup.sh` |
| droid-ctl | none | adb | `droid-ctl/scripts/setup.sh` |
| iphone-ctl | none | libimobiledevice | `iphone-ctl/scripts/setup.sh` |
| devkit | orchestrates | .env | `./mob setup` |

<a id="ja"></a>
## 日本語

| 機能 | 依存 | インストール |
|------|------|--------------|
| Python CLI | Python ≥3.9 | システム Python |
| TG 送信 | tg-notify | `./mob tg-setup` |
| Android | adb | `./mob setup --only adb` |
| iOS | libimobiledevice, WDA | brew + Xcode |

詳細は [INSTALL.md](INSTALL.md)。`./mob setup` が総合インストール入口。
