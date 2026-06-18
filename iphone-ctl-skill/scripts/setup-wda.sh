#!/usr/bin/env bash
# Clone WebDriverAgent and open Xcode (one-time WDA setup helper)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PARENT="$(cd "$SKILL_ROOT/.." && pwd)"
WDA_DIR="${WDA_DIR:-$PARENT/WebDriverAgent}"
REPO="https://github.com/appium/WebDriverAgent.git"

usage() {
  cat <<EOF
Usage: setup-wda.sh [options]

Clone WebDriverAgent next to ios_skill and open Xcode.

Options:
  --dir PATH    Clone destination (default: ../WebDriverAgent)
  --no-open     Clone only, do not open Xcode
  -h, --help

After Xcode opens, see: iphone-ctl-skill/docs/WDA_SETUP.md
EOF
}

OPEN=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dir) WDA_DIR="${2:-}"; shift 2 ;;
    --no-open) OPEN=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown: $1" >&2; exit 1 ;;
  esac
done

if [[ -d "$WDA_DIR/.git" ]]; then
  echo "→ WebDriverAgent exists: $WDA_DIR"
  git -C "$WDA_DIR" pull --ff-only 2>/dev/null || true
else
  echo "→ cloning $REPO"
  git clone "$REPO" "$WDA_DIR"
fi

if [[ -f "$WDA_DIR/Scripts/bootstrap.sh" ]]; then
  echo "→ running bootstrap.sh -d (may take a minute)"
  (cd "$WDA_DIR" && ./Scripts/bootstrap.sh -d) || echo "  bootstrap failed — continue in Xcode"
fi

cat <<EOF

== Next steps (see docs/WDA_SETUP.md) ==

1. Xcode → open WebDriverAgent.xcodeproj
2. Targets WebDriverAgentLib + WebDriverAgentRunner → Signing → your Team
3. Scheme: WebDriverAgentRunner → select iPhone → Run (⌘R)
4. Terminal: iproxy 8100 8100 -u \$(ioskit devices | head -1)
5. iphone-ctl wda status

EOF

if [[ "$OPEN" -eq 1 ]]; then
  if [[ -f "$WDA_DIR/WebDriverAgent.xcodeproj/project.pbxproj" ]]; then
    open "$WDA_DIR/WebDriverAgent.xcodeproj"
  else
    echo "error: project not found under $WDA_DIR" >&2
    exit 1
  fi
fi
