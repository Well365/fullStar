# devkit — 一键移动设备运维

统一入口：**Telegram + Android (adbkit) + iOS (iphone-ctl/WDA)**。

## 能一键做什么

| 操作 | 命令 | 全自动？ |
|------|------|----------|
| **全部安装** | `./mob-compose/setup` | ✅ pip + skills + .env |
| **环境检查** | `./mob-compose/check` | ✅ |
| **Android 截图发 TG** | `./mob-compose/shot-android` | ✅ 需连手机 |
| **iOS 截图发 TG** | `./mob-compose/shot-ios` | ✅ 需 USB |
| **iOS 端口转发** | `./mob-compose/ios-start` | ✅ 后台 iproxy |
| **WDA 编译装真机** | `./mob-compose/build-wda` | ⚠️ 需 `IOS_DEVELOPMENT_TEAM` |
| **WDA 首次签名** | Xcode Run 一次 | ⚠️ 免费账号需手动点 Team |

> **唯一不能 100% 跳过的一步**：iOS WDA 首次要在 Xcode 里选 **Team** 并信任证书（或配置 `IOS_DEVELOPMENT_TEAM` 后 `build-wda`）。

## 一键开始

```bash
cd mobile-agent

chmod +x mobagent mob-compose/compose mob-compose/scripts/*.sh

cp .env.example .env
# 编辑 TELEGRAM_BOT_TOKEN、TELEGRAM_CHAT_ID

# 安装一切（Telegram + adb + ios + Skills）
./mob setup --test

# 检查
./mob check
```

## 日常一键

```bash
# Android 验收截图 → Telegram
./mob-compose/shot-android -c "Android 构建完成"

# iOS：先确保 WDA Runner 在手机上运行
./mob-compose/ios-start
./mob-compose/shot-ios -c "iOS 验收"

# iOS 坐标点击（Agent 或手动）
ioskit tap 540 1200
```

## iOS WDA 尽量一键

```bash
cp mob-compose/compose.env.example mob-compose/compose.env
# 编辑 IOS_DEVELOPMENT_TEAM=你的TeamID（Xcode → Accounts）

./mob-compose/setup --with-ios-wda    # 含 clone WDA + xcodebuild
./mob-compose/ios-start
./mob-compose/check                   # 应看到 WDA ready
```

首次若 `build-wda` 失败，按 `iphone-ctl-skill/docs/WDA_SETUP.md` 在 Xcode 里 **Run 一次** WebDriverAgentRunner，之后只需：

```bash
./mob-compose/ios-start    # 每天一条
```

## 包结构

```
mobile-agent/
├── .env              ← Telegram 等配置
├── mobagent          ← CLI 入口
├── mob-compose/
├── tg-notify/ + tg-notify-skill/
├── droid-ctl/ + droid-ctl-skill/
└── iphone-ctl/ + iphone-ctl-skill/
```

## Agent

`setup` 后 Cursor 可用 skills：**tg** / **adb** / **ios**。

对 Agent 说：「devkit check 一下，然后 Android 和 iOS 都截图发 Telegram」

MIT
