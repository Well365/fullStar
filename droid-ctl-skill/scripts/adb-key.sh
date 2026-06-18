#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=adb-common.sh
source "$SCRIPT_DIR/adb-common.sh"
require_adbkit
[[ $# -ge 1 ]] || { echo "Usage: adb-key.sh KEY" >&2; exit 1; }
exec droid-ctl key "$1"
