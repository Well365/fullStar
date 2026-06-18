#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "→ pip install droid-ctl from $ROOT"
python3 -m pip install -e "$ROOT" -q

echo "→ ensure platform-tools (downloads to ~/.adbkit if no system adb)"
python3 -c "from droid_ctl.core.adb_path import resolve_adb_path; print('adb:', resolve_adb_path())"

python3 -c "import droid_ctl; print('adbkit', droid_ctl.__version__, 'ok')"
command -v droid-ctl
adbkit --help | head -3

echo ""
echo "Done. Run: droid-ctl devices"
