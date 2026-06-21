# Telegram Setup / Telegram 配置 / Telegram 設定

> All config lives in `fullStar/.env`

| Language | Section |
|----------|---------|
| 简体中文 | [below](#zh) |
| English | [below](#en) |
| 日本語 | [below](#ja) |

**One-click:**

```bash
cd fullStar
chmod +x mob tg-relay/setup-telegram.sh
./tg-relay/setup-telegram.sh --test
# or: ./mob tg-setup --test
```

---

<a id="zh"></a>

## 简体中文

### 一键配置

```bash
./tg-relay/setup-telegram.sh --test                    # 交互式
./tg-relay/setup-telegram.sh --fetch-chat-id --test    # 自动获取 Chat ID
./tg-relay/setup-telegram.sh --token "TOKEN" --chat-id "ID" --non-interactive --test
```

### 手动配置 `.env`

```bash
cp .env.example .env
```

```bash
TELEGRAM_BOT_TOKEN=从@BotFather获取
TELEGRAM_CHAT_ID=你的chat_id
```

| 变量 | 必填 | 说明 |
|------|:----:|------|
| `TELEGRAM_BOT_TOKEN` | ✓ | @BotFather 创建 Bot 获得 |
| `TELEGRAM_CHAT_ID` | 推荐 | 截图/通知的默认接收者 |

### 获取 Token

1. Telegram → **@BotFather** → `/newbot`
2. 复制 Token 写入 `.env`

### 获取 Chat ID

1. 给 Bot 发 `/start`
2. 访问 `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. 找 `"chat":{"id":...}`

或：`./tg-relay/setup-telegram.sh --fetch-chat-id`

### 验证

```bash
./mob check
tgkit send "测试"
./mob tg-start
```

### 常见问题

| 问题 | 处理 |
|------|------|
| `TELEGRAM_BOT_TOKEN not set` | 运行 `./tg-relay/setup-telegram.sh` |
| `chat_id is not set` | `--fetch-chat-id` 或手动填写 |
| Bot 无响应 | `./mob tg-start` 需在 Mac 上运行 |
| Token 泄露 | @BotFather `/revoke` 后更新 `.env` |

---

<a id="en"></a>

## English

### One-click setup

```bash
./tg-relay/setup-telegram.sh --test
./tg-relay/setup-telegram.sh --fetch-chat-id --test
./tg-relay/setup-telegram.sh --token "TOKEN" --chat-id "ID" --non-interactive --test
```

### Manual `.env`

```bash
cp .env.example .env
```

```bash
TELEGRAM_BOT_TOKEN=from @BotFather
TELEGRAM_CHAT_ID=your_chat_id
```

| Variable | Required | Purpose |
|----------|:--------:|---------|
| `TELEGRAM_BOT_TOKEN` | yes | Bot credential |
| `TELEGRAM_CHAT_ID` | recommended | Default message recipient |

### Get Token

Telegram → **@BotFather** → `/newbot` → copy token to `.env`

### Get Chat ID

Message bot `/start`, then open `https://api.telegram.org/bot<TOKEN>/getUpdates`

Or: `./tg-relay/setup-telegram.sh --fetch-chat-id`

### Verify

```bash
./mob check
tgkit send "test"
./mob tg-start
```

### Troubleshooting

| Issue | Fix |
|-------|-----|
| `TELEGRAM_BOT_TOKEN not set` | Run `./tg-relay/setup-telegram.sh` |
| `chat_id is not set` | Use `--fetch-chat-id` or set manually |
| Bot not responding | `./mob tg-start` must run on your Mac |
| Token leaked | @BotFather `/revoke`, update `.env` |

---

<a id="ja"></a>

## 日本語

### ワンクリック設定

```bash
./tg-relay/setup-telegram.sh --test
./tg-relay/setup-telegram.sh --fetch-chat-id --test
./tg-relay/setup-telegram.sh --token "TOKEN" --chat-id "ID" --non-interactive --test
```

### 手動 `.env`

```bash
cp .env.example .env
```

```bash
TELEGRAM_BOT_TOKEN=@BotFatherで取得
TELEGRAM_CHAT_ID=あなたのchat_id
```

| 変数 | 必須 | 説明 |
|------|:----:|------|
| `TELEGRAM_BOT_TOKEN` | ✓ | Bot 認証情報 |
| `TELEGRAM_CHAT_ID` | 推奨 | デフォルト送信先 |

### Token 取得

Telegram → **@BotFather** → `/newbot` → Token を `.env` に設定

### Chat ID 取得

Bot に `/start` を送信後、`https://api.telegram.org/bot<TOKEN>/getUpdates` を開く

または：`./tg-relay/setup-telegram.sh --fetch-chat-id`

### 検証

```bash
./mob check
tgkit send "テスト"
./mob tg-start
```

### トラブルシューティング

| 現象 | 対処 |
|------|------|
| `TELEGRAM_BOT_TOKEN not set` | `./tg-relay/setup-telegram.sh` を実行 |
| `chat_id is not set` | `--fetch-chat-id` または手動設定 |
| Bot が応答しない | `./mob tg-start` を Mac で実行 |
| Token 漏洩 | @BotFather `/revoke`、`.env` を更新 |
