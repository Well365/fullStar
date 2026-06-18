#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=ios-common.sh
source "$SCRIPT_DIR/ios-common.sh"
require_ioskit
[[ $# -ge 2 ]] || { echo "Usage: ios-tap.sh X Y" >&2; exit 1; }
exec iphone-ctl tap "$1" "$2" "${@:3}"
