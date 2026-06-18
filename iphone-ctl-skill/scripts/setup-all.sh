#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
IOSKIT="${IOSKIT_PATH:-$SKILL_ROOT/../ioskit}"

echo "== ios_skill setup =="
[[ -f "$IOSKIT/pyproject.toml" ]] && python3 -m pip install -e "$IOSKIT" -q
chmod +x "$SCRIPT_DIR"/*.sh
"$SCRIPT_DIR/install-skill.sh"
"$SCRIPT_DIR/check-env.sh" || true
echo ""
echo "WDA quick start:"
ioskit wda proxy 2>/dev/null || true
