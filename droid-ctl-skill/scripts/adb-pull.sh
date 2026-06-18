#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=adb-common.sh
source "$SCRIPT_DIR/adb-common.sh"
require_adbkit
[[ $# -ge 2 ]] || { echo "Usage: adb-pull.sh REMOTE [LOCAL]" >&2; exit 1; }
LOCAL="${2:-$(basename "$1")}"
exec droid-ctl pull "$1" "$LOCAL"
