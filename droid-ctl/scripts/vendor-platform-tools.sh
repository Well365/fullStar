#!/usr/bin/env bash
# Refresh vendor/platform-tools* from local SDK or Google download (maintainers)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FROM_SDK=0
DOWNLOAD=0

usage() {
  cat <<'EOF'
Usage: vendor-platform-tools.sh [--from-sdk | --download]

  --from-sdk   Copy from ANDROID_HOME or ~/Library/Android/sdk/platform-tools
  --download   Download latest from Google into vendor/ (maintainer release)

Default: --from-sdk if SDK found, else error.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --from-sdk) FROM_SDK=1; shift ;;
    --download) DOWNLOAD=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown: $1" >&2; exit 1 ;;
  esac
done

if [[ "$DOWNLOAD" -eq 1 ]]; then
  exec python3 -c "
from droid_ctl.core.tools import download_platform_tools
p = download_platform_tools(into_vendor=True)
print('vendor updated:', p)
"
fi

SRC=""
for d in \
  "${ANDROID_HOME:-}/platform-tools" \
  "${ANDROID_SDK_ROOT:-}/platform-tools" \
  "$HOME/Library/Android/sdk/platform-tools" \
  "$HOME/Android/Sdk/platform-tools"; do
  if [[ -x "$d/adb" || -f "$d/adb.exe" ]]; then
    SRC="$d"
    break
  fi
done

if [[ -z "$SRC" ]]; then
  echo "error: no local SDK platform-tools found. Use --download or set ANDROID_HOME." >&2
  exit 1
fi

DEST="$ROOT/vendor/platform-tools"
echo "→ rsync $SRC → $DEST"
mkdir -p "$DEST"
rsync -a --delete "$SRC/" "$DEST/"
echo "done: $DEST"
ls -la "$DEST/adb" 2>/dev/null || ls -la "$DEST/adb.exe"
