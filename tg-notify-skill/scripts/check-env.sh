#!/usr/bin/env bash
# Verify tg-notify installation and .env configuration
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=find-env.sh
source "$SCRIPT_DIR/find-env.sh"

PROJECT_DIR=""
OK=0
WARN=0
FAIL=0

pass() { echo "  ✓ $1"; OK=$((OK + 1)); }
warn() { echo "  ! $1"; WARN=$((WARN + 1)); }
fail() { echo "  ✗ $1"; FAIL=$((FAIL + 1)); }

usage() {
  cat <<'EOF'
Usage: check-env.sh [--project-dir PATH]

Checks tg-notify install, .env, and LLM skill registration.

.env search order:
  1. TGKIT_ENV_FILE
  2. --project-dir/.env
  3. current directory and parents
  4. mobile-agent/.env (package root)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-dir) PROJECT_DIR="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

SEARCH_DIR="${PROJECT_DIR:-$(pwd)}"
echo "== tg-notify environment check =="
echo "  cwd: $(pwd)"

if command -v python3 >/dev/null 2>&1; then
  pass "python3: $(python3 --version 2>&1)"
else
  fail "python3 not found"
fi

if command -v tg-notify >/dev/null 2>&1; then
  pass "tgkit CLI: $(command -v tg-notify)"
else
  fail "tgkit CLI not found (run: ./mob setup)"
fi

if python3 -c "import tg_notify" 2>/dev/null; then
  pass "tgkit Python module importable"
else
  fail "cannot import tg_notify"
fi

ENV_FILE=""
if ENV_FILE="$(find_tgkit_env_file "$SEARCH_DIR" "$SKILL_ROOT")"; then
  :
else
  ENV_FILE=""
fi

if [[ -n "$ENV_FILE" && -f "$ENV_FILE" ]]; then
  pass ".env found: $ENV_FILE"
  # shellcheck disable=SC1090
  set -a && source "$ENV_FILE" && set +a
else
  fail ".env not found (try: cp .env.example .env && ./mob setup)"
fi

if [[ -n "${TELEGRAM_BOT_TOKEN:-}" ]]; then
  pass "TELEGRAM_BOT_TOKEN is set"
else
  fail "TELEGRAM_BOT_TOKEN is empty"
fi

if [[ -n "${TELEGRAM_CHAT_ID:-}" ]]; then
  pass "TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}"
elif [[ -n "$ENV_FILE" ]]; then
  CONFIG_PATH="${TGKIT_CONFIG_PATH:-}"
  if [[ -z "$CONFIG_PATH" ]]; then
    env_dir="$(dirname "$ENV_FILE")"
    for cfg in "$env_dir/config.json"; do
      if [[ -f "$cfg" ]]; then
        CONFIG_PATH="$cfg"
        break
      fi
    done
  fi
  if [[ -n "$CONFIG_PATH" && -f "$CONFIG_PATH" ]]; then
    CHAT_FROM_CFG="$(python3 -c "import json; print(json.load(open('$CONFIG_PATH')).get('chat_id',''))" 2>/dev/null || true)"
    if [[ -n "$CHAT_FROM_CFG" ]]; then
      pass "chat_id from config: $CONFIG_PATH → $CHAT_FROM_CFG"
    else
      warn "TELEGRAM_CHAT_ID not set (set in .env or config.json chat_id)"
    fi
  else
    warn "TELEGRAM_CHAT_ID not set (set in .env or pass --chat-id when sending)"
  fi
else
  warn "TELEGRAM_CHAT_ID not set"
fi

for skill_home in "$HOME/.cursor/skills/tg-notify" "$HOME/.claude/skills/tg-notify"; do
  if [[ -f "$skill_home/SKILL.md" ]]; then
    pass "skill installed: $skill_home"
  else
    warn "skill missing: $skill_home (run install-skill.sh)"
  fi
done

if [[ "$(uname -s)" == "Darwin" ]]; then
  warn "macOS: grant Accessibility + Screen Recording to your terminal for app screenshots"
fi

echo ""
echo "summary: ${OK} ok, ${WARN} warn, ${FAIL} fail"
if [[ "$FAIL" -gt 0 ]]; then
  exit 1
fi
