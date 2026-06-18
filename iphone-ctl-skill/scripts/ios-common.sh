#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
IOSKIT_DEFAULT="$(cd "$SKILL_ROOT/../ioskit" 2>/dev/null && pwd || true)"

require_ioskit() {
  if ! command -v iphone-ctl >/dev/null 2>&1; then
    if [[ -n "$IOSKIT_DEFAULT" && -f "$IOSKIT_DEFAULT/pyproject.toml" ]]; then
      python3 -m pip install -e "$IOSKIT_DEFAULT" -q
    fi
  fi
  command -v iphone-ctl >/dev/null 2>&1 || {
    echo "ios_skill: iphone-ctl not found. pip install -e ../ioskit" >&2
    exit 1
  }
}
