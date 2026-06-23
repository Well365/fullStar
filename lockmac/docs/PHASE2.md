# lockmac 第二阶段 — 中央服务器 + 超级管理员舰队（设计）

> 状态：📐 设计，待实施。基于第一阶段（单机 agent，见 [PHASE1.md](PHASE1.md)）。
> 本阶段只做「协调与管控通道」，破坏性销毁/crypto-erase 留第三阶段。

---

## 1. 目标

把已实现的单机 lockmac 升级为**一对多舰队**：
- 一个**超级管理员**通过 Telegram 管理多台 Mac。
- 超管：查看全部、远程锁/解任意机、配置各机 dead-man、暂停（防误触）。
- **超管锁定 → 普通用户/本地密码不能解，必须超管解。**
- 每条消息带**机器可识别名称**，超管一眼知道是哪台。
- **不改变第一阶段的本地自治**：销毁/锁定仍本地执行，服务器只「续期 + 下发指令」。

---

## 2. 与第一阶段的关系

```
第一阶段（已实现）            第二阶段（新增，叠加在上）
──────────────────          ──────────────────────────
每台 agent：                 + 注册到中央服务器
 本地 dead-man 倒计时   ──►   + 倒计时由"服务器续期"重置（替代/补充本地）
 本地执行锁/purge            + 收超管指令（锁/解/暂停/配置）
 自带 TG（单机）        ──►   + 心跳改发往服务器（而非各自 bot），解决
                              getUpdates 单消费者冲突
                            + 上报机器名/状态
超管：无                     + 超管面板（经超管 bot ↔ 服务器 API）
```

第一阶段的执行层（overlay / system_lock / purge_dirs_now）**原样复用**，第二阶段只在外面套一层「注册 + 续期 + 指令」。

---

## 3. 架构图

```
                ┌──────────────────────┐
                │   超级管理员 (Telegram) │
                │  /fleet  /lock <机>    │
                │  /unlock <机> /pause   │
                └───────────┬──────────┘
                            │ 超管 bot（单一消费者 = 服务器）
                            ▼
        ┌───────────────────────────────────────────┐
        │            中央服务器（常驻在线）             │
        │  • 设备注册表：id / 机器名 / 状态 / 最后心跳   │
        │  • 角色权限：super-admin / operator          │
        │  • 续期签名：给在线 agent 发"renew"           │
        │  • 指令队列：lock/unlock/pause/config         │
        │  • 审计日志                                  │
        └───┬──────────────┬──────────────┬───────────┘
            │ HTTPS+token   │              │   agent 周期心跳 ↑（带机器名/状态）
            ▼               ▼              ▼   服务器回复 ↓（renew + 指令）
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ Mac-A       │  │ "设计部-02" │  │ "财务-Mac"  │
     │ lockmac     │  │ lockmac    │  │ lockmac    │
     │ agent       │  │ agent      │  │ agent      │
     │ ┌────────┐  │  │            │  │            │
     │ │本地倒计时│  │  │  本地自治   │  │  本地自治   │
     │ │收renew  │  │  │  离线照锁   │  │            │
     │ │重置;否则 │  │  │            │  │            │
     │ │到点本地锁│  │  │            │  │            │
     │ └────────┘  │  │            │  │            │
     └────────────┘  └────────────┘  └────────────┘
```

---

## 4. 组件

### 4.1 中央服务器（新建）
- **设备注册表**：`device_id, name, pubkey, status, last_seen, owner_lock`。
- **续期签名**：在线 agent 心跳 → 返回签名 `renew`（重置其本地倒计时）。**签名防伪造续期**绕过 dead-man。
- **指令队列**：超管下发的 `lock/unlock/pause/config`，agent 心跳时取走。
- **超管 bot ↔ API**：超管 bot 是服务器对 Telegram 的唯一消费者（避免多机 409）。

### 4.2 agent（在第一阶段上扩展）
- `register`：首次上报机器名（`scutil --get ComputerName`）、生成密钥。
- `heartbeat`：周期上报状态，接收 `renew` + 指令。
- **续期即重置本地倒计时**；收不到 renew（服务器够不到 或 机器离线）→ 本地到点自锁（沿用第一阶段）。
- 执行超管指令：`lock`（owner=admin，本地密码失效）/`unlock`（需服务器令牌）/`pause`。

---

## 5. 数据流

### 5.1 注册
```
agent ──register{name, pubkey}──► server ──► 返回 device_id + token
```

### 5.2 心跳 / 续期（核心循环）
```
每 interval：
  agent ──heartbeat{device_id, status}──► server
  server ──{renew(签名), commands[]}──► agent
        renew → 重置本地倒计时
        commands → 执行（lock/unlock/pause/config）
  若心跳失败（服务器够不到 / 离线）：
        本地倒计时继续 → 到 T1 本地锁 → 到 T2 本地销毁（第一阶段逻辑）
```

### 5.3 超管锁 / 解
```
超管 /lock 设计部-02 ──► server 入队 lock ──► 该机下次心跳取走 ──► owner=admin 本地锁
超管 /unlock 设计部-02 ──► server 发签名解锁令牌 ──► agent 验证 → 解除
                          （本地密码/TOTP 对 admin 锁无效）
```

### 5.4 防误触
```
超管 /pause 设计部-02 2h ──► server 标记 ──► 持续给该机 renew（即使它"看似失联"）
   用于：长途飞行 / 已知网络故障，避免 dead-man 误触发
```

---

## 6. 服务器 API（草案）

```
POST /register     {name, pubkey}                 → {device_id, token}
POST /heartbeat    {device_id, status, ts}        → {renew_sig, commands[]}
GET  /admin/devices                               → 列出全部（名/状态/last_seen）
POST /admin/lock   {device_id}                     → 入队 admin-lock
POST /admin/unlock {device_id}                     → 下发签名解锁令牌
POST /admin/pause  {device_id, until}              → 暂停 dead-man（防误触）
POST /admin/config {device_id, deadman/purge…}     → 远程改各机配置
```
超管 bot 命令 ↔ 上述 API：`/fleet`→devices，`/lock <名>`→lock，等。

---

## 7. 关键设计点（承接第一阶段 ADR）

- **本地自治不变**（ADR-1）：服务器只「续期」，销毁/锁定本地执行；服务器/网络缺席不影响 dead-man 必然触发。
- **续期需签名**：防止伪造 renew 绕过 dead-man。
- **超管 bot 单消费者**：服务器是该 bot 唯一 getUpdates 消费者，多机不冲突（解决早期 409 问题）。
- **机器名标识**：每条上报/通知带 `ComputerName`。
- **失联即触发，超管可暂停**（ADR-4）：T1/T2 够长 + `/pause` 防误触。

---

## 8. 实施里程碑

| # | 里程碑 | 产出 |
|---|---|---|
| 2.1 | 服务器骨架 + 注册/心跳 | agent 能注册、周期心跳、收 renew |
| 2.2 | 续期驱动本地倒计时 | renew 重置；失联→本地自锁（接第一阶段） |
| 2.3 | 超管 bot 面板 | `/fleet` `/lock` `/unlock` `/pause` + 机器名 |
| 2.4 | 超管锁优先级 | owner=admin，本地密码/TOTP 失效，仅超管解 |
| 2.5 | 远程配置 + 暂停 | `/admin/config` `/pause` 防误触 |
| 2.6 | 审计 + 加固 | 签名、令牌、HTTPS、日志 |

部署形态待定（自建小服务 / 云函数 / VPS），评审时确定。

---

## 9. 不在第二阶段

- ❌ recovery key 托管、crypto-erase、MDM `EraseDevice`、两段销毁 → **第三阶段**
- 第二阶段交付的是「可靠的管控通道 + 超管 + 防误触」，为第三阶段的破坏性操作打地基。
