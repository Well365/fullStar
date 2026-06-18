#!/usr/bin/env bash
# Screenshot iOS device and send to Telegram via tgkit
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=ios-common.sh
source "$SCRIPT_DIR/ios-common.sh"
require_ioskit

CAPTION=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    -c|--caption) CAPTION="${2:-}"; shift 2 ;;
    -h|--help)
      echo "Usage: ios-tg-shot.sh [-c CAPTION]"
      exit 0
      ;;
    *) echo "unknown: $1" >&2; exit 1 ;;
  esac
done

SHOT_JSON="$(ioskit shot --json)"
SHOT_PATH="$(python3 -c "import json,sys; print(json.load(sys.stdin)['path'])" <<< "$SHOT_JSON")"
udid="$(python3 -c "import json,sys; print(json.load(sys.stdin)['udid'])" <<< "$SHOT_JSON")"
CAPTION="${CAPTION:-iOS screenshot · $udid}"

command -v tg-notify >/dev/null 2>&1 || { echo "tgkit required" >&2; exit 1; }
TG_SKILL="$(cd "$SCRIPT_DIR/../../tg-notify-skill/scripts" 2>/dev/null && pwd || true)"
if [[ -n "$TG_SKILL" && -f "$TG_SKILL/load-env.sh" ]]; then
  # shellcheck source=/dev/null
  source "$TG_SKILL/load-env.sh" || true
fi
tgkit send --photo "$SHOT_PATH" --caption "$CAPTION"

python3 -c "
import json
d = json.loads('''$SHOT_JSON''')
d['telegram_sent'] = True
d['caption'] = '''$CAPTION'''
print(json.dumps(d, ensure_ascii=False))
"
