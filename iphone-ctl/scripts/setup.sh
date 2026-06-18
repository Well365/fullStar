#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -m pip install -e "$ROOT[dev]" -q
python3 -c "import iphone_ctl; print('ioskit', iphone_ctl.__version__)"
command -v iphone-ctl
ioskit which
