#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ADBKIT_DEFAULT="$(cd "$SKILL_ROOT/../adbkit" 2>/dev/null && pwd || true)"
# shellcheck source=adb-common.sh
source "$SCRIPT_DIR/adb-common.sh"

OK=0
WARN=0
FAIL=0
CHECK_TG=0

pass() { echo "  ✓ $1"; OK=$((OK + 1)); }
warn() { echo "  ! $1"; WARN=$((WARN + 1)); }
fail() { echo "  ✗ $1"; FAIL=$((FAIL + 1)); }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-tg) CHECK_TG=1; shift ;;
    -h|--help) exit 0 ;;
    *) echo "unknown: $1" >&2; exit 1 ;;
  esac
done

echo "== adb_skill environment check =="

if command -v droid-ctl >/dev/null 2>&1; then
  pass "adbkit CLI: $(command -v droid-ctl)"
else
  if [[ -n "$ADBKIT_DEFAULT" ]]; then
    warn "adbkit not on PATH — run: pip install -e $ADBKIT_DEFAULT"
  else
    fail "adbkit not found"
  fi
fi

if command -v droid-ctl >/dev/null 2>&1; then
  adb_path="$(adbkit which 2>/dev/null || true)"
  if [[ -n "$adb_path" ]]; then
    pass "adb binary: $adb_path"
  fi
  if droid-ctl devices 2>/dev/null | awk 'NR>1 && $2=="device" {c++} END{exit c<1}'; then
    pass "device connected"
  else
    warn "no device in 'device' state"
  fi
fi

for skill_home in "$HOME/.cursor/skills/adb" "$HOME/.claude/skills/adb"; do
  if [[ -f "$skill_home/SKILL.md" ]]; then
    pass "skill: $skill_home"
  else
    warn "skill missing: $skill_home"
  fi
done

if [[ "$CHECK_TG" -eq 1 ]] && command -v tg-notify >/dev/null 2>&1; then
  pass "tgkit available (adb-tg-shot)"
fi

echo ""
echo "summary: ${OK} ok, ${WARN} warn, ${FAIL} fail"
[[ "$FAIL" -eq 0 ]] || exit 1
