#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=adb-common.sh
source "$SCRIPT_DIR/adb-common.sh"
require_adbkit
LINES=50
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -n) LINES="${2:-50}"; shift 2 ;;
    -f|--follow) echo "adb-logcat: use droid-ctl logcat (no follow yet)" >&2; shift ;;
    *) ARGS+=("$1"); shift ;;
  esac
done
exec droid-ctl logcat -n "$LINES" "${ARGS[@]}"
