# adb_skill — Examples

## 1. AI 分析当前界面

```bash
./scripts/adb-analyze.sh --ui
# Agent reads JSON → opens path PNG + ui_dump XML → describes screen
```

## 2. 点击登录按钮（视觉循环）

```bash
# Step 1: see
./scripts/adb-shot.sh --json
# Agent finds button at ~(540, 1800) from image

# Step 2: act
./scripts/adb-tap.sh 540 1800

# Step 3: verify
./scripts/adb-shot.sh --json
```

## 3. 用 UI dump 精确定位

```bash
./scripts/adb-ui-dump.sh -o /tmp/ui.xml
# Find: bounds="[100,200][300,280]" → center (200, 240)
./scripts/adb-tap.sh 200 240
```

## 4. 安装并启动 APK

```bash
./scripts/adb-install.sh /path/to/app-release.apk
./scripts/adb-start.sh com.your.pkg/com.cocos.game.AppActivity
./scripts/adb-tg-shot.sh -c "安装完成，当前界面"
```

## 5. 远程 Telegram 验收

用户在 Telegram 说：「截个图看看登录页」

Agent 在本机执行：

```bash
./scripts/adb-tg-shot.sh -c "登录页验收"
```

用户手机上收到 Bot 发来的截图。

## 6. 滑动列表

```bash
# Swipe up (1080x2400 screen)
./scripts/adb-swipe.sh 540 1800 540 600 400
```

## 7. 输入搜索词

```bash
./scripts/adb-tap.sh 540 200      # focus search box
./scripts/adb-input.sh "poker"
./scripts/adb-key.sh ENTER
```

## 8. 唤醒黑屏后截图

```bash
./scripts/adb-key.sh POWER
sleep 1
./scripts/adb-shot.sh --json
```

## 9. 多设备指定序列号

```bash
export ADB_SERIAL=emulator-5554
./scripts/adb-devices.sh
./scripts/adb-shot.sh --json
```

## 10. Agent 自然语言

用户对 Cursor 说：

> 连着的 Android 手机截个图，看看是不是在主界面；如果不是就按返回键再截一张，发到 Telegram。

Agent 应依次调用：`adb-analyze.sh` → 读图 → 可能 `adb-key.sh BACK` → `adb-tg-shot.sh`。
