#!/usr/bin/env bash
# Pre-commit / CI: fail if tracked files look like they contain secrets
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

FAIL=0

echo "== verify-no-secrets =="

# 1. Must-ignore files must not be tracked
FORBIDDEN_PATHS=(
  .env
  mob-compose/compose.env
  game-qa-autopilot/.env
  game-qa-autopilot/autoqa.config.local.ts
  game-qa-autopilot/storage-state.json
)

if git rev-parse --git-dir >/dev/null 2>&1; then
  for p in "${FORBIDDEN_PATHS[@]}"; do
    if [[ -f "$p" ]] && git ls-files --error-unmatch "$p" >/dev/null 2>&1; then
      echo "✗ tracked secret file: $p (must be gitignored)"
      FAIL=1
    fi
  done
else
  echo "! not a git repo — skip tracked-file check"
fi

# 2. Scan staged/tracked text for Telegram token pattern
scan_grep() {
  local label="$1"
  shift
  if "$@" 2>/dev/null | grep -qE '[0-9]{8,12}:[A-Za-z0-9_-]{30,}'; then
    echo "✗ possible TELEGRAM_BOT_TOKEN in $label"
    FAIL=1
  fi
}

if git rev-parse --git-dir >/dev/null 2>&1; then
  scan_grep "tracked files" git grep -l 'TELEGRAM_BOT_TOKEN=[^$]' -- ':!*.example' ':!.env.example' ':!verify-no-secrets.sh' 2>/dev/null || true
fi

# 3. Local .env must exist only locally
for f in .env mob-compose/compose.env; do
  if [[ -f "$f" ]]; then
    echo "  (local only) $f — gitignored ✓"
  fi
done

if [[ "$FAIL" -eq 0 ]]; then
  echo "✓ no obvious secrets in git index"
else
  echo "fix issues before pushing"
  exit 1
fi
