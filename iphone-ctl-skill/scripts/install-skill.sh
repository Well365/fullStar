#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_NAME="ios"

install_one() {
  local base="$1" label="$2"
  [[ -d "$(dirname "$base")" ]] || return 0
  mkdir -p "$base/$SKILL_NAME"
  cp "$SKILL_ROOT/SKILL.md" "$base/$SKILL_NAME/"
  cp "$SKILL_ROOT/reference.md" "$base/$SKILL_NAME/" 2>/dev/null || true
  echo "installed → $base/$SKILL_NAME/"
}

install_one "$HOME/.cursor/skills" "Cursor"
install_one "$HOME/.claude/skills" "Claude"
