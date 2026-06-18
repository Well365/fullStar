# Skill 组合指南

`mobile-agent` 内各 Skill **彼此独立**，可按需单独安装或自由组合。  
每个 Skill 对应一套 CLI + Agent 文档，组合时 Agent 按任务选用。

## 可用 Skill

| Skill 名 | 安装名 | CLI | 依赖 |
|----------|--------|-----|------|
| **tg** / tg-notify | `tg_skill` | `tg-notify` | `.env` + Bot Token |
| **adb** | `adb_skill` | `droid-ctl` | USB Android |
| **ios** | `ios_skill` | `iphone-ctl` | USB iPhone + WDA |
| **mobile-agent** | mob-remote-skill/SKILL.md | `mobagent` | 上述任意子集 |

## 安装方式

```bash
cd mobile-agent

# 全部
./mob install-skill

# 只装需要的
./mob install-skill --only tg
./mob install-skill --only adb,ios
./mob install-skill tg adb          # 等价于 --only tg,adb

# 查看列表
./mob install-skill --list
```

对应 Python 包（可单独 pip）：

```bash
pip install -e tg-notify/      # 仅 Telegram
pip install -e droid-ctl/     # 仅 Android
pip install -e iphone-ctl/     # 仅 iOS
```

`setup` 同样支持组合：

```bash
./mob setup --only tg,adb
./mob setup --only ios --with-ios-wda
```

---

## 常见组合

### 1. 仅 Telegram 通知

**Skill:** `tg`  
**场景:** CI 构建通知、发截图、发日志，不操作手机。

```bash
./mob install-skill --only tg
./mob setup --only tg --test
```

Agent 话术：「用 tg-notify 发 Telegram：构建完成」

---

### 2. 仅 Android 本地自动化

**Skill:** `adb`  
**场景:** USB 连测试机，截图分析、点击滑动，不发 TG。

```bash
./mob install-skill --only adb
./mob setup --only adb
adbkit shot --json && droid-ctl tap 540 1200
```

---

### 3. 仅 iOS 本地自动化

**Skill:** `ios`  
**场景:** iPhone 真机 + WDA，坐标操作。

```bash
./mob install-skill --only ios
./mob setup --only ios
./mob ios-start
ioskit shot --json && iphone-ctl tap 540 1200
```

---

### 4. Android + Telegram（远程验收）

**Skill:** `tg` + `adb`  
**场景:** 手机发 TG 指令 → Mac Agent 操作 Android → 截图回 TG。

```bash
./mob install-skill --only tg,adb
./mob setup --only tg,adb --test
```

| 你说 | Agent 用 |
|------|----------|
| 把手机画面发到 Telegram | `adb-tg-shot.sh` |
| 点登录按钮 | `adb-analyze` → `adb-tap` → `adb-tg-shot` |

---

### 5. iOS + Telegram（远程验收）

**Skill:** `tg` + `ios`

```bash
./mob install-skill --only tg,ios
./mob ios-start
./mob shot-ios -c "验收"
```

---

### 6. Android + iOS（双端本地）

**Skill:** `adb` + `ios`  
**场景:** 同一台 Mac 连两台设备，分别操作，无需 TG。

```bash
./mob install-skill --only adb,ios
```

Agent 按平台切换 `droid-ctl` / `iphone-ctl`。

---

### 7. 全栈（TG 收令 + 双端 + Agent）

**Skill:** `tg` + `adb` + `ios` + `mobile-agent`

```bash
./mob install-skill          # 或 --all
./mob setup --test
./mob tg-start               # Bot 收 /shot /tap 等
```

`mobile-agent` Skill 是**编排层**，告诉 Agent 如何组合上述三个子 Skill。

---

## 组合矩阵

| 需求 | 安装 Skill | setup |
|------|-----------|-------|
| 发 TG 消息 | tg | `--only tg` |
| 控 Android | adb | `--only adb` |
| 控 iPhone | ios | `--only ios` |
| Android 远程验收 | tg + adb | `--only tg,adb` |
| iOS 远程验收 | tg + ios | `--only tg,ios` |
| 双端本地 | adb + ios | `--only adb,ios` |
| 完整远程 Agent | all | 默认 |

---

## Agent 如何选 Skill

- 用户提到 **Telegram / tg / 通知** → 加载 **tg**
- 用户提到 **adb / Android / 安卓** → 加载 **adb**
- 用户提到 **iOS / iPhone / WDA** → 加载 **ios**
- 用户提到 **远程验收 / mobile-agent / 双端** → 加载 **mobile-agent**（内含组合指引）

各 Skill 的 `disable-model-invocation: true`，需用户点名或显式引用时加载，避免无关场景误触发。

---

## 脚本层组合（无需全量 Skill）

即使只装了部分 Skill，shell 脚本仍可组合：

```bash
# tg + adb（需 tg-notify + adbkit）
droid-ctl-skill/scripts/adb-tg-shot.sh -c "结果"

# tg + ios
iphone-ctl-skill/scripts/ios-tg-shot.sh -c "结果"

# devkit 封装（内部调上述脚本）
./mob shot-android
./mob shot-ios
```

---

## 独立部署

mobile-agent 是**自包含包**，所有配置在包内完成：

```bash
cp .env.example .env    # Telegram Token
./mob setup --test
```

- 验收机可只装 **tg + adb** 或 **tg + ios**
- 各 Skill **不强制**安装其他 Skill；缺依赖时 `check` 会提示
- 通过 `TGKIT_ENV_FILE` 可指向外部 `.env`（可选，非默认）
