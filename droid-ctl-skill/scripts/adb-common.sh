#!/usr/bin/env bash
# Delegate to droid-ctl CLI (bundled platform-tools when system adb missing)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ADBKIT_DEFAULT="$(cd "$SKILL_ROOT/../adbkit" 2>/dev/null && pwd || true)"

require_adbkit() {
  if ! command -v droid-ctl >/dev/null 2>&1; then
    if [[ -n "$ADBKIT_DEFAULT" && -f "$ADBKIT_DEFAULT/pyproject.toml" ]]; then
      echo "adb_skill: installing droid-ctl from $ADBKIT_DEFAULT" >&2
      python3 -m pip install -e "$ADBKIT_DEFAULT" -q
    fi
  fi
  if ! command -v droid-ctl >/dev/null 2>&1; then
    echo "adb_skill: droid-ctl not found. Run: pip install -e ../adbkit" >&2
    exit 1
  fi
}
