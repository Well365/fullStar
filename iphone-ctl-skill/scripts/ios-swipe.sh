#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=ios-common.sh
source "$SCRIPT_DIR/ios-common.sh"
require_ioskit
[[ $# -ge 4 ]] || { echo "Usage: ios-swipe.sh X1 Y1 X2 Y2 [--duration SEC]" >&2; exit 1; }
exec iphone-ctl swipe "$@"
