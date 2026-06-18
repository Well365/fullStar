#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILL_NAME="adb"

install_one() {
  local target_base="$1"
  local label="$2"
  if [[ ! -d "$(dirname "$target_base")" ]]; then
    echo "skip $label: parent dir missing"
    return 0
  fi
  mkdir -p "$target_base/$SKILL_NAME"
  cp "$SKILL_ROOT/SKILL.md" "$target_base/$SKILL_NAME/SKILL.md"
  cp "$SKILL_ROOT/reference.md" "$target_base/$SKILL_NAME/reference.md"
  cp "$SKILL_ROOT/examples.md" "$target_base/$SKILL_NAME/examples.md"
  echo "installed → $target_base/$SKILL_NAME/"
}

install_one "$HOME/.cursor/skills" "Cursor"
install_one "$HOME/.claude/skills" "Claude Code"

cat <<EOF

Done. Requires **adbkit** (pip install -e ../adbkit).

  ./scripts/setup-all.sh

Ask the agent:
  "adb 截图并分析当前界面"
  "通过 adb 点击坐标 540 1200"

Remote + Telegram: install tg_skill + tgkit, see docs/REMOTE_WORKFLOW.md

EOF
