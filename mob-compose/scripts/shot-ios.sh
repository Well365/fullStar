#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
exec "$MONOREPO_ROOT/iphone-ctl-skill/scripts/ios-tg-shot.sh" "$@"
