#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=ios-common.sh
source "$SCRIPT_DIR/ios-common.sh"
require_ioskit
exec iphone-ctl analyze "$@"
