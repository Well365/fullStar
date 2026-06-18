#!/usr/bin/env bash
# tg-notify package-only setup (no LLM skill). Called standalone or from tg-notify-skill/setup-all.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "→ pip install tg-notify from $ROOT"
python3 -m pip install -e "$ROOT[dotenv]" -q
python3 -c "import tg_notify; print('tgkit', tg_notify.__version__, 'ok')"
command -v tg-notify

echo "Next: configure .env and run tg-notify-skill/scripts/setup-all.sh for full setup"
