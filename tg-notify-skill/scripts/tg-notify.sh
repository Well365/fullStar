#!/usr/bin/env bash
# Send Telegram notification via tg-notify CLI
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=load-env.sh
source "$SCRIPT_DIR/load-env.sh"

if ! command -v tg-notify >/dev/null 2>&1; then
  echo "tg-notify: tg-notify not installed. Run: pip install \"tgkit[dotenv]\"" >&2
  exit 1
fi

if [[ $# -eq 0 ]]; then
  cat <<'EOF' >&2
Usage:
  tg-notify.sh "message text"
  tg-notify.sh --photo path.png [--caption TEXT]
  tg-notify.sh --file path.log
  tg-notify.sh --chat-id ID "message"

Delegates to: tg-notify send ...
EOF
  exit 1
fi

exec tg-notify send "$@"
