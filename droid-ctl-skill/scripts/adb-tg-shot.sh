#!/usr/bin/env bash
# Screenshot via droid-ctl and send to Telegram via tgkit
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=adb-common.sh
source "$SCRIPT_DIR/adb-common.sh"
require_adbkit

CAPTION=""
TO_TG=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    -c|--caption) CAPTION="${2:-}"; shift 2 ;;
    --no-tg) TO_TG=0; shift ;;
    -h|--help)
      echo "Usage: adb-tg-shot.sh [-c CAPTION] [--no-tg]"
      exit 0
      ;;
    *) echo "unknown: $1" >&2; exit 1 ;;
  esac
done

SHOT_JSON="$(adbkit shot --json)"
SHOT_PATH="$(python3 -c "import json,sys; print(json.load(sys.stdin)['path'])" <<< "$SHOT_JSON")"
serial="$(python3 -c "import json,sys; print(json.load(sys.stdin)['device'])" <<< "$SHOT_JSON")"
CAPTION="${CAPTION:-ADB screenshot · $serial}"

if [[ "$TO_TG" -eq 1 ]]; then
  command -v tg-notify >/dev/null 2>&1 || { echo "tgkit required: pip install tgkit[dotenv]" >&2; exit 1; }
  TG_SKILL="$(cd "$SCRIPT_DIR/../../tg-notify-skill/scripts" 2>/dev/null && pwd || true)"
  if [[ -n "$TG_SKILL" && -f "$TG_SKILL/load-env.sh" ]]; then
    # shellcheck source=/dev/null
    source "$TG_SKILL/load-env.sh" || true
  fi
  tg-notify send --photo "$SHOT_PATH" --caption "$CAPTION"
fi

python3 -c "
import json
d = json.loads('''$SHOT_JSON''')
d['telegram_sent'] = $TO_TG == 1
d['caption'] = '''$CAPTION'''
print(json.dumps(d, ensure_ascii=False))
"
