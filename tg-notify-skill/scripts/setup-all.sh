#!/usr/bin/env bash
# One-click setup: tg-notify pip package + .env + Cursor/Claude skills + verify
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TGKIT_DEFAULT="$(cd "$SKILL_ROOT/../tg-notify" 2>/dev/null && pwd || true)"

PROJECT_DIR=""
TGKIT_PATH="${TGKIT_PATH:-$TGKIT_DEFAULT}"
TOKEN=""
CHAT_ID=""
RUN_TEST=0
INTERACTIVE=1

usage() {
  cat <<'EOF'
Usage: setup-all.sh [options]

One-click configure tg-notify + tg_skill for local development.

Options:
  --project-dir PATH   Directory to create/use .env (default: current directory)
  --tgkit-path PATH    Path to tg-notify repo (default: ../tg-notify next to tg_skill)
  --token TOKEN        TELEGRAM_BOT_TOKEN (skip prompt)
  --chat-id ID         TELEGRAM_CHAT_ID (skip prompt)
  --test               Send a test message after setup
  --non-interactive    Fail if token missing instead of prompting
  -h, --help           Show help

Examples:
  ./scripts/setup-all.sh
  ./scripts/setup-all.sh --test
  ./scripts/setup-all.sh --token "123:ABC" --chat-id 123456789 --non-interactive
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-dir) PROJECT_DIR="${2:-}"; shift 2 ;;
    --tgkit-path) TGKIT_PATH="${2:-}"; shift 2 ;;
    --token) TOKEN="${2:-}"; shift 2 ;;
    --chat-id) CHAT_ID="${2:-}"; shift 2 ;;
    --test) RUN_TEST=1; shift ;;
    --non-interactive) INTERACTIVE=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

PROJECT_DIR="${PROJECT_DIR:-$(pwd)}"
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"

echo "== tg-notify one-click setup =="
echo "project dir : $PROJECT_DIR"
echo "tg_skill    : $SKILL_ROOT"

# --- 1. Python / pip ---
if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 required" >&2
  exit 1
fi
echo "→ python3 $(python3 --version 2>&1)"

# --- 2. Install tg-notify ---
if [[ -n "$TGKIT_PATH" && -f "$TGKIT_PATH/pyproject.toml" ]]; then
  echo "→ pip install tg-notify from $TGKIT_PATH"
  python3 -m pip install -e "$TGKIT_PATH[dotenv]" -q
elif python3 -m pip show tg-notify >/dev/null 2>&1; then
  echo "→ tg-notify already installed via pip"
else
  echo "→ pip install tg-notify from PyPI"
  python3 -m pip install "tg-notify[dotenv]" -q
fi

if ! command -v tg-notify >/dev/null 2>&1; then
  echo "error: tg-notify CLI not on PATH after install" >&2
  echo "  try: python3 -m pip install --user -e \"$TGKIT_PATH[dotenv]\"" >&2
  exit 1
fi
echo "  tgkit: $(command -v tg-notify)"

# --- 3. .env ---
ENV_FILE="$PROJECT_DIR/.env"
if [[ -f "$ENV_FILE" ]]; then
  echo "→ .env exists: $ENV_FILE"
else
  cp "$SKILL_ROOT/.env.example" "$ENV_FILE"
  echo "→ created .env from template: $ENV_FILE"
fi

# Read existing values if not passed on CLI
# shellcheck disable=SC1090
set -a && source "$ENV_FILE" && set +a
TOKEN="${TOKEN:-${TELEGRAM_BOT_TOKEN:-}}"
CHAT_ID="${CHAT_ID:-${TELEGRAM_CHAT_ID:-}}"

if [[ -z "$TOKEN" && "$INTERACTIVE" -eq 1 ]]; then
  echo ""
  read -r -p "Enter TELEGRAM_BOT_TOKEN (from @BotFather): " TOKEN
fi

if [[ -z "$CHAT_ID" && "$INTERACTIVE" -eq 1 ]]; then
  read -r -p "Enter TELEGRAM_CHAT_ID (optional, Enter to skip): " CHAT_ID
fi

if [[ -z "$TOKEN" ]]; then
  echo "error: TELEGRAM_BOT_TOKEN is required" >&2
  echo "  edit $ENV_FILE or re-run with --token" >&2
  exit 1
fi

write_env() {
  local key="$1" val="$2" file="$3"
  if grep -q "^${key}=" "$file" 2>/dev/null; then
    if [[ "$(uname -s)" == "Darwin" ]]; then
      sed -i '' "s|^${key}=.*|${key}=${val}|" "$file"
    else
      sed -i "s|^${key}=.*|${key}=${val}|" "$file"
    fi
  else
    echo "${key}=${val}" >> "$file"
  fi
}

write_env "TELEGRAM_BOT_TOKEN" "$TOKEN" "$ENV_FILE"
if [[ -n "$CHAT_ID" ]]; then
  write_env "TELEGRAM_CHAT_ID" "$CHAT_ID" "$ENV_FILE"
fi
echo "→ updated $ENV_FILE"

# --- 4. Install LLM skills ---
echo "→ installing skills to Cursor / Claude Code"
"$SCRIPT_DIR/install-skill.sh" | sed 's/^/  /'

# --- 5. Verify ---
echo "→ running check-env"
(
  cd "$PROJECT_DIR"
  export TGKIT_ENV_FILE="$ENV_FILE"
  "$SCRIPT_DIR/check-env.sh"
) || true

# --- 6. Optional test send ---
if [[ "$RUN_TEST" -eq 1 ]]; then
  echo "→ sending test message"
  (
    cd "$PROJECT_DIR"
    export TGKIT_ENV_FILE="$ENV_FILE"
    tg-notify send "tgkit setup-all 测试 OK ✓"
  )
  echo "  check your Telegram chat for the test message"
fi

cat <<EOF

== setup complete ==

Project .env : $ENV_FILE
Try:
  cd "$PROJECT_DIR"
  tg-notify send "hello"
  $SKILL_ROOT/scripts/tg-notify.sh "hello"

In Cursor / Claude Code:
  "用 tg-notify 发 Telegram：构建完成"

EOF
