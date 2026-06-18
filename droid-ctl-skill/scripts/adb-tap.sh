#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=adb-common.sh
source "$SCRIPT_DIR/adb-common.sh"
require_adbkit
[[ $# -ge 2 ]] || { echo "Usage: adb-tap.sh X Y" >&2; exit 1; }
exec droid-ctl tap "$1" "$2"
