# lockmac 第一阶段 — 单机 dead-man（已实现）

> 状态：✅ 已实现并测试（49 passed）。完全单机、自包含、**不依赖任何服务器**。
> 所有 dead-man 触发本地自治，离线必然生效。

---

## 1. 概述

单台 Mac 上的隐私遮罩 + 锁定 + dead-man 自毁工具：
- **三种锁定级别**：app 遮罩(可解) / 系统真锁(单向) / 删目录。
- **三种触发**：失联超时 / 心跳无响应 / 手动。
- **双配置通道**：CLI 与 Telegram，共享同一配置，TG 改动即时生效。
- **二步验证**：本地密码 + TOTP（本地解除 与 TG 远程都支持）。

---

## 2. 架构图（单机）

```
┌───────────────────────────── 一台 Mac ─────────────────────────────┐
│                                                                     │
│   配置入口（共享同一份 config）                                       │
│   ┌──────────────┐        ┌─────────────────────────┐              │
│   │  CLI: lockmac │        │  Telegram (绑定的 bot)   │              │
│   │  deadman/...  │        │  /deadman /purge /veil…  │              │
│   └──────┬───────┘        └────────────┬────────────┘              │
│          │  读写                         │  tg-listen 收命令 + 每轮重读 │
│          ▼                              ▼                            │
│   ┌─────────────────────────────────────────────────┐              │
│   │  config.json  (~/.config/lockmac/)               │              │
│   │  密码哈希 · TOTP密钥 · 心跳/失联时间 · 动作 · 删除清单 │              │
│   └───────────────────────┬─────────────────────────┘              │
│                           │ 读                                       │
│   ┌───────────────────────▼─────────────────────────┐              │
│   │  lockmac.core  (执行层)                           │              │
│   │   start/stop(遮罩) · system_lock · purge_dirs_now │              │
│   │   verify_password · verify TOTP · heartbeat_cfg   │              │
│   └───┬───────────────┬───────────────┬──────────────┘              │
│       │               │               │                            │
│       ▼               ▼               ▼                            │
│  ┌─────────┐    ┌──────────┐    ┌──────────────┐                   │
│  │ overlay  │    │ osascript │    │ rm -rf       │                   │
│  │ (Swift)  │    │ Ctrl-Cmd-Q│    │ (purge dirs) │                   │
│  │ 遮罩+密码 │    │ 系统锁屏  │    │ 白名单护栏    │                   │
│  │ +TOTP框  │    └──────────┘    └──────────────┘                   │
│  └─────────┘                                                        │
│                                                                     │
│   守护：tg-listen（前台/LaunchAgent）跑 dead-man 倒计时              │
│         开机自启：install-agent(遮罩) · tg-install(监听)            │
└─────────────────────────────────────────────────────────────────┘
```

**模块**
| 文件 | 职责 |
|---|---|
| `core.py` | 配置读写、遮罩启停、系统锁、purge、密码/TOTP 校验、心跳配置 |
| `cli.py` | `lockmac` 命令入口 |
| `tg.py` | 绑定 TG：命令分发、心跳/失联 dead-man 调度、配置命令 |
| `totp.py` | RFC 6238 TOTP（与 Swift 端算法一致） |
| `overlay.swift` | 全屏遮罩 + 密码框 + TOTP 码框 |

---

## 3. 流程图 A：dead-man 触发（核心）

```
            tg-listen 循环（每轮重读配置）
                      │
        ┌─────────────┼──────────────┐
        ▼             ▼              ▼
  getUpdates      心跳到期?         失联检查
   成功→记       发签到(✅按钮)    now - 上次成功联系
   last_online        │                │
        │        点按钮→重置        ≥ offline?
        │             │                │
        │        宽限内没点 ≥grace?    是 → 触发(本地)
        │             │ 是              │
        └─────────────┴────────────────┘
                      ▼
              执行动作 _do_action(action)
                ├ lock   → 系统真锁
                ├ veil   → app 遮罩
                └ purge  → 删配置目录(白名单护栏)
                      │
              通知 TG（best-effort，离线则跳过）
```

**关键**：失联触发完全本地（`now - last_online`），断网/拔网照样到点执行——这是真正的 dead-man。

---

## 4. 流程图 B：解除遮罩（二步验证）

```
遮罩升起（veil）
   │
   ├─ 本地：overlay 显示
   │    ┌ 密码框 ──► sha256(salt+pw) == 存储? ─┐
   │    └ TOTP框 ──► verifyTOTP(secret, code)? ─┤ 两者都 ✅ → 解除
   │                                            └ 否 → 提示错误，清空
   │
   ├─ Telegram：/unveil <6位码>
   │    └ chat 白名单(因素1) + TOTP(因素2) ✅ → 解除
   │
   └─ 超时兜底：veil N → N 秒自动解除
```
> 系统锁(lock)不同：单向，只能在机器前输系统密码解，无远程解除。

---

## 5. 命令清单

```
锁定/解除   veil · unveil · lock · status
dead-man    deadman <签到秒> <宽限秒> <lock|veil|purge> [失联秒]
删除清单    purge-add <路径> · purge-list · purge-clear · purge-now --yes
密码/2FA    setup · passwd · set-password · setup-2fa · 2fa-off
开机自启    install-agent · uninstall-agent(遮罩) · tg-install · tg-uninstall(监听)
Telegram    tg-setup · tg-test · tg-listen
TG 内命令   /veil /unveil /lock /status /deadman /purge /unveil <码>
```

---

## 6. 配置项（`~/.config/lockmac/config.json`）

| 键 | 含义 |
|---|---|
| `pwd_hash` / `salt` | 本地解除密码（salted SHA-256） |
| `totp_secret` | 二步验证密钥（RFC 6238） |
| `hb_interval` / `hb_grace` | 主动签到间隔 / 宽限 |
| `hb_offline` | 失联超时（连不上 TG 多久触发） |
| `hb_action` | `lock` / `veil` / `purge` |
| `purge_dirs` | 删除清单（白名单护栏） |
| `tg_token` / `tg_chat` | 绑定的 bot |
| `enable_on_boot` | 开机是否自动遮罩 |

---

## 7. 安全护栏

- **purge 白名单**：路径必须绝对，拒绝 `/`、`$HOME`、`/System` `/Library` `/usr` 等系统树；仅删显式加入的目录。
- **purge-now 需 `--yes`**。
- **chat 白名单**：TG 只响应绑定的 chat（fail-closed）。
- 密码/TOTP 密钥/token 不进 argv。
- TOTP 第二因素（本地 + TG 都可要求）。

---

## 8. 测试 / 分发

- 测试：`cd lockmac && pytest` → **49 passed**（密码、TOTP RFC 向量、失联/心跳触发边界、purge 路径护栏、TG 配置）。
- 分发：`install.sh` 一键 / Homebrew formula / 双击 `.pkg`（见 `packaging/`）。

---

## 9. 边界（第一阶段不含）

- ❌ 多机舰队、超级管理员、批量管控 → 第二阶段（`PHASE2.md`）
- ❌ recovery key 托管、crypto-erase / MDM → 第三阶段
- ⚠️ 单机的 purge 是真删除；crypto-erase（销毁芯片密钥）需 MDM，不在本阶段
