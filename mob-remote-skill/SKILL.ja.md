---
name: mobile-agent
description: >-
  Telegram リモート制御で Android / iOS 実機を自動化。サブスキル tg・adb・ios と自由に組み合わせ、必要なものだけインストール。
  リモート端末操作、TG デバイス運用、モバイル受入、WDA タップ、Telegram 経由の adb スクリーンショット、
  mobile-agent / mobagent ワークフローに使用。iOS は macOS のみ。
disable-model-invocation: true
---

# mobile-agent — Telegram + Android + iOS

**Telegram** 経由の**リモートモバイル端末自動化**用統合スキル。

パッケージルート：`mobile-agent/` — 自己完結、外部プロジェクト不要。

## 組み合わせ可能なスキル

各サブスキルは**単体で利用可能**。任意の組み合わせでインストール：

| スキル | 単体利用の場面 | よく一緒に使う |
|--------|----------------|----------------|
| **tg** | TG 通知のみ送信 | adb、ios |
| **adb** | Android USB 自動化 | tg（リモート受入） |
| **ios** | iPhone + WDA 自動化 | tg（リモート受入） |
| **mobile-agent** | 全体オーケストレーション文書 | 上記すべて |

```bash
./mob install-skill --only tg          # Telegram のみ
./mob install-skill --only adb,ios     # デュアルプラットフォーム、TG スキルなし
./mob install-skill --only tg,adb      # Android リモート受入
./mob install-skill                    # すべて

./mob setup --only tg,adb
```

レシピは [docs/SKILL_COMPOSE.md](docs/SKILL_COMPOSE.md) を参照。

Agent ルール：タスクに関連するスキルのみ読み込む（tg / adb / ios）。  
サブスキル詳細：`tg-notify-skill/SKILL.md`、`droid-ctl-skill/SKILL.md`、`iphone-ctl-skill/SKILL.md`。

## コンポーネント

| 部分 | パス | 役割 |
|------|------|------|
| **mobagent** | `./mob` | 統合 CLI エントリ |
| **devkit** | `mob-compose/` | setup / check / shot-android / shot-ios |
| **adbkit + adb_skill** | `droid-ctl/`、`droid-ctl-skill/` | Android 制御 |
| **ioskit + ios_skill** | `iphone-ctl/`、`iphone-ctl-skill/` | iOS 制御（WDA） |
| **tgkit + tg_skill** | `tg-notify/`、`tg-notify-skill/` | Telegram 送信 |
| **tg-relay** | `tg-relay.py` | TG コマンド受信 |
| **WebDriverAgent** | `WebDriverAgent/` | iOS タップ/スワイプ |
| **game-qa-autopilot** | `game-qa-autopilot/` | ブラウザゲーム QA（任意） |

## 初回セットアップ

```bash
cd mobile-agent
chmod +x mobagent mob-compose/compose mob-compose/scripts/*.sh scripts/*.sh

cp .env.example .env
./mob setup --test
./mob install-skill
./mob check
```

iOS の日常運用：`./mob ios-start` のあと、端末で WDA Runner が動作していることを確認。

## 3 つの運用モード

### A. Agent + TG 送信（デフォルト）

ユーザーが Cursor に TG 指示を貼る → Agent がデバイススクリプトを実行 → `tg-notify` で結果送信。

```
TG 指示 → Agent → droid-ctl/ioskit → tg-notify send --photo
```

### B. TG Bot コマンド（半自動）

```bash
./mob tg-start
```

Bot コマンド：`/shot android`、`/shot ios`、`/tap 540 1200`、`/swipe ...`、`/check`、`/devices`  
自然言語 → `inbox/pending.txt` に書き込み → Agent が `./mob tg-inbox` で読み取り。

### C. ビジョンループ（フル自動）

```
1. shot --json          → PNG を読む
2. 画面を分析           → x,y を決定
3. tap / swipe          → 操作実行
4. shot --json          → 検証
5. tg-notify send --photo   → ユーザーへ報告
```

## Agent ワークフロー

1. `./mob check` を実行 — 不足ツール/端末を先に修正。
2. プラットフォーム選択：**android**（`droid-ctl`）または **ios**（`iphone-ctl` + WDA + iproxy）。
3. タップ後は**必ず再スクリーンショット**して検証。
4. 結果送信：`./mob shot-android -c "..."` または `tgkit send --photo`。
5. `TELEGRAM_BOT_TOKEN` を出力しない。

## クイックコマンド

```bash
# 環境
./mob check
./mob ios-start

# スクリーンショット → Telegram
./mob shot-android -c "Android 受入"
./mob shot-ios -c "iOS 受入"

# 直接 CLI
adbkit shot --json && droid-ctl tap 540 1200
ioskit shot --json && iphone-ctl tap 540 1200

# TG リスナー
./mob tg-start
./mob tg-inbox
```

## 座標のヒント

- 原点 (0,0) は左上；サイズは `shot --json` の `screen` フィールドから取得
- Cocos ゲーム：**画像座標**を使い、要素 id は使わない
- iOS ゲーム：`mob-compose/compose.env` に `IOS_WDA_BUNDLE_ID` を設定

## 安全

- 破壊的操作はユーザーに確認
- リモート tap/swipe はテスト端末を使用
- `.env` やトークンをコミットしない

## トラブルシューティング

| 問題 | 対処 |
|------|------|
| Android 端末なし | USB デバッグ有効；`adbkit devices` |
| WDA 未準備 | Xcode で WDA Runner を Run；`./mob ios-start` |
| TG トークンなし | `mobile-agent/.env`（`.env.example` からコピー） |
| タップ無効（iOS） | `IOS_WDA_BUNDLE_ID` を設定；アプリをフォアグラウンドに |

## サブスキル（個別）

| スキル | インストール | ドキュメント |
|--------|--------------|--------------|
| tg | `./mob install-skill --only tg` | `tg-notify-skill/SKILL.md` |
| adb | `./mob install-skill --only adb` | `droid-ctl-skill/SKILL.md` |
| ios | `./mob install-skill --only ios` | `iphone-ctl-skill/SKILL.md` |

## 詳細資料

- [docs/SKILL_COMPOSE.md](docs/SKILL_COMPOSE.md) — **組み合わせインストールとシナリオ**
- [README.ja.md](README.ja.md) — パッケージ全体ガイド
- `droid-ctl-skill/docs/REMOTE_WORKFLOW.md` — TG リモートアーキテクチャ
- `iphone-ctl-skill/docs/WDA_SETUP.md` — iOS WDA セットアップ

## 他の言語

- [English](SKILL.md)
- [简体中文](mob-remote-skill/SKILL.zh-CN.md)
