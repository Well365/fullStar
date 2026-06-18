#!/usr/bin/env bash
# Capture screenshot and send to Telegram via tg-notify CLI (macOS)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=load-env.sh
source "$SCRIPT_DIR/load-env.sh"

if ! command -v tg-notify >/dev/null 2>&1; then
  echo "tg-screenshot: tg-notify not installed. Run: pip install \"tgkit[dotenv]\"" >&2
  exit 1
fi

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "tg-screenshot: screenshot features require macOS" >&2
  exit 1
fi

exec tg-notify screenshot "$@"
