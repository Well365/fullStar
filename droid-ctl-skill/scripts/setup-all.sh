#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ADBKIT_PATH="${ADBKIT_PATH:-$(cd "$SKILL_ROOT/../adbkit" 2>/dev/null && pwd || true)}"
INSTALL_TG=0
RUN_TEST=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-tg) INSTALL_TG=1; shift ;;
    --test) RUN_TEST=1; shift ;;
    --adbkit-path) ADBKIT_PATH="${2:-}"; shift 2 ;;
    -h|--help) exit 0 ;;
    *) echo "unknown: $1" >&2; exit 1 ;;
  esac
done

echo "== adb_skill setup =="

# 1. Install droid-ctl (includes platform-tools bootstrap)
if [[ -n "$ADBKIT_PATH" && -f "$ADBKIT_PATH/pyproject.toml" ]]; then
  echo "→ pip install droid-ctl from $ADBKIT_PATH"
  python3 -m pip install -e "$ADBKIT_PATH" -q
elif python3 -m pip show droid-ctl >/dev/null 2>&1; then
  echo "→ droid-ctl already installed"
else
  echo "error: droid-ctl not found. Clone ../adbkit or set --adbkit-path" >&2
  exit 1
fi

echo "→ platform-tools"
adbkit which
adbkit install-tools 2>/dev/null || droid-ctl which

chmod +x "$SCRIPT_DIR"/*.sh
"$SCRIPT_DIR/install-skill.sh" | sed 's/^/  /'
"$SCRIPT_DIR/check-env.sh" ${INSTALL_TG:+--with-tg} || true

if [[ "$INSTALL_TG" -eq 1 ]]; then
  TG="$SKILL_ROOT/../tg-notify-skill/scripts/setup-all.sh"
  TG_PROJECT="$(cd "$SKILL_ROOT/.." && pwd)"
  [[ -x "$TG" ]] && "$TG" --project-dir "$TG_PROJECT" || true
fi

if [[ "$RUN_TEST" -eq 1 ]]; then
  droid-ctl shot --json || echo "  (no device?)"
fi

cat <<EOF

== done ==
  droid-ctl devices
  droid-ctl shot --json
  droid-ctl analyze --ui

EOF
