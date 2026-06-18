# WebDriverAgent 真机安装指南

与 Appium 使用的是**同一套 WDA**。装好后 `ioskit tap/swipe` 通过 `http://127.0.0.1:8100` 控制真机。

---

## 你需要准备

| 项目 | 说明 |
|------|------|
| Mac + Xcode | 建议 Xcode 15+ |
| Apple ID | 免费账号即可（证书约 7 天需重装） |
| iPhone | USB 连接，**开发者模式**打开（iOS 16+） |
| libimobiledevice | `brew install libimobiledevice` |

---

## 第一步：下载 WebDriverAgent

mobile-agent 已内置 `WebDriverAgent/`。若需单独 clone：

```bash
cd /path/to/mobile-agent
# 或: git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent
./Scripts/bootstrap.sh -d
```

若 `bootstrap.sh` 失败，可跳过，直接用 Xcode 打开工程。

```bash
open WebDriverAgent.xcodeproj
```

或使用本仓库脚本（仅 clone + 打开 Xcode）：

```bash
./iphone-ctl-skill/scripts/setup-wda.sh
```

---

## 第二步：Xcode 签名配置（两个 Target 都要改）

在 Xcode 左侧选中工程 **WebDriverAgent**，对下面 **两个** Target 重复操作：

1. **WebDriverAgentLib**
2. **WebDriverAgentRunner** ← 真正装到手机上的 Runner

对每个 Target：

1. 打开 **Signing & Capabilities**
2. 勾选 **Automatically manage signing**
3. **Team** 选你的 Apple 开发者账号（个人免费账号即可）
4. 若 **Bundle Identifier** 冲突，改成唯一值，例如：
   - `com.yourname.WebDriverAgentLib`
   - `com.yourname.WebDriverAgentRunner.xctrunner`

> Runner 的 Bundle ID 末尾通常是 `.xctrunner`，保持即可。

---

## 第三步：编译并装到真机

1. 顶部设备选择器选你的 **iPhone 真机**（不要选 Simulator）
2. Scheme 选 **WebDriverAgentRunner**
3. 菜单 **Product → Run**（或 `⌘R`）

首次可能失败，常见处理：

| 报错 | 处理 |
|------|------|
| Signing / provisioning | 换唯一 Bundle ID，重登 Apple ID |
| untrusted developer | 手机：设置 → 通用 → VPN与设备管理 → 信任 |
| Developer Mode | 设置 → 隐私与安全性 → 开发者模式 → 开 |
| Could not launch | 拔掉重插 USB，手机上点「信任」 |

成功后：

- Xcode 控制台出现 `ServerURLHere->http://xxx.xxx.xxx.xxx:8100<-ServerURLHere`
- 手机上出现 **WebDriverAgentRunner** 应用（或自动化图标）

**保持 Xcode Run 状态**，或手机上手动点开 Runner，WDA 服务才会监听 8100 端口。

---

## 第四步：Mac 端口转发（每次必做）

WDA 在手机的 **8100** 端口，Mac 需用 `iproxy` 转发：

```bash
export IOS_UDID=$(ioskit devices | head -1)
iproxy 8100 8100 -u "$IOS_UDID"
```

**此终端要保持运行**，不要关。

另开终端验证：

```bash
ioskit wda status
# 应看到 "ready": true 或 session 信息

curl -s http://127.0.0.1:8100/status | python3 -m json.tool
```

---

## 第五步：配合 iphone-ctl 使用

```bash
# 测你们游戏时建议设置 Bundle ID
export IOS_WDA_BUNDLE_ID=com.your.poker.bundle

ioskit shot --json          # 截图（走 idevicescreenshot，不需 WDA）
ioskit tap 540 1200         # 坐标点击（走 WDA）
ioskit swipe 540 800 540 300
./iphone-ctl-skill/scripts/ios-tg-shot.sh -c "验收"
```

---

## 架构示意

```
┌─────────────┐     USB      ┌──────────────────┐
│    Mac      │◄────────────►│  iPhone 真机      │
│             │              │  WDA Runner :8100 │
│  iproxy     │              └──────────────────┘
│  8100→8100  │
│      ↓      │
│  iphone-ctl tap │──── HTTP ────► /session/.../wda/tap
│  idevicescreenshot ─ USB ──► 截图文件
└─────────────┘
```

---

## 免费证书 7 天过期

个人免费 Apple ID 签名的 WDA **约 7 天失效**，到期后：

1. Xcode 重新 **Run** WebDriverAgentRunner 到手机  
2. 或：Xcode → Window → Devices and Simulators → 选中设备 → **+** 重新安装

付费开发者账号（$99/年）可大幅延长。

---

## 与 Appium 的关系

| | Appium | iphone-ctl |
|--|--------|--------|
| WDA 安装 | 同一套 Xcode 编译 | **相同** |
| 控制方式 | Appium Server + 驱动 | 直接 HTTP 调 WDA |
| 截图 | 可用 WDA 或 idevice | 默认 **idevicescreenshot**（更稳） |
| tap/swipe | WDA | WDA 坐标 API |

你已装好 WDA 后，**不必再装 Appium**，`iphone-ctl` 直接连 `127.0.0.1:8100`。

---

## 故障排查

| 现象 | 检查 |
|------|------|
| `connection refused` | Runner 是否在跑？iproxy 是否开着？ |
| `ready: false` | Xcode 重新 Run；看手机是否锁屏 |
| tap 无反应 | 设 `IOS_WDA_BUNDLE_ID`，确保目标 App 在前台 |
| idevicescreenshot 失败 | USB、信任、`ioskit devices` 能否看到 UDID |
| 8100 被占用 | `lsof -i :8100`，换端口：`iproxy 8200 8100` + `IOS_WDA_URL=http://127.0.0.1:8200` |

---

## 一键检查

```bash
./iphone-ctl-skill/scripts/check-env.sh
```

期望：`iOS device connected` ✓，`WDA ready` ✓（需 Runner + iproxy 都就绪）。
