#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=ios-common.sh
source "$SCRIPT_DIR/ios-common.sh"

OK=0; WARN=0; FAIL=0
pass() { echo "  ✓ $1"; OK=$((OK+1)); }
warn() { echo "  ! $1"; WARN=$((WARN+1)); }
fail() { echo "  ✗ $1"; FAIL=$((FAIL+1)); }

echo "== ios_skill environment check =="

if command -v iphone-ctl >/dev/null 2>&1; then pass "ioskit: $(command -v iphone-ctl)"; else fail "ioskit missing"; fi

for bin in idevice_id idevicescreenshot iproxy; do
  if command -v "$bin" >/dev/null 2>&1; then pass "$bin"; else warn "$bin missing (brew install libimobiledevice)"; fi
done

if command -v iphone-ctl >/dev/null 2>&1; then
  if iphone-ctl devices 2>/dev/null | grep -q .; then pass "iOS device connected"; else warn "no device"; fi
  if iphone-ctl wda status --json 2>/dev/null | grep -q '"ready": true'; then
    pass "WDA ready"
  else
    warn "WDA not ready — start Runner on device + iproxy 8100 8100"
  fi
fi

for d in "$HOME/.cursor/skills/ios" "$HOME/.claude/skills/ios"; do
  [[ -f "$d/SKILL.md" ]] && pass "skill: $d" || warn "skill missing: $d"
done

echo ""; echo "summary: ${OK} ok, ${WARN} warn, ${FAIL} fail"
[[ "$FAIL" -eq 0 ]]
