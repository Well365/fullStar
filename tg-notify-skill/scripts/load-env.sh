#!/usr/bin/env bash
# Find and load .env (mobile-agent root, cwd, or parents)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=find-env.sh
source "$SCRIPT_DIR/find-env.sh"

ENV_FILE=""
if ENV_FILE="$(find_tgkit_env_file "$(pwd)" "$SKILL_ROOT")"; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
  return 0 2>/dev/null || exit 0
fi

echo "tg_skill: .env not found (set TGKIT_ENV_FILE or run: ./mob setup)" >&2
return 1 2>/dev/null || exit 1
