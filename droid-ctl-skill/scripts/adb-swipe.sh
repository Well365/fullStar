#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=adb-common.sh
source "$SCRIPT_DIR/adb-common.sh"
require_adbkit
[[ $# -ge 4 ]] || { echo "Usage: adb-swipe.sh X1 Y1 X2 Y2 [DURATION_MS]" >&2; exit 1; }
exec droid-ctl swipe "$@"
