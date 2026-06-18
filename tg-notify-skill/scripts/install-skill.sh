#!/usr/bin/env bash
# Install tg-notify skill to Cursor and Claude Code user skill directories
set -euo pipefail

SKILL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="tg-notify"

install_one() {
  local target_base="$1"
  local label="$2"
  if [[ ! -d "$(dirname "$target_base")" ]]; then
    echo "skip $label: $(dirname "$target_base") does not exist"
    return 0
  fi
  mkdir -p "$target_base/$SKILL_NAME"
  cp "$SKILL_ROOT/SKILL.md" "$target_base/$SKILL_NAME/SKILL.md"
  cp "$SKILL_ROOT/reference.md" "$target_base/$SKILL_NAME/reference.md"
  echo "installed → $target_base/$SKILL_NAME/"
}

install_one "$HOME/.cursor/skills" "Cursor"
install_one "$HOME/.claude/skills" "Claude Code"

cat <<EOF

Done. Skill files copied; tg-notify Python package is separate:

  pip install "tg-notify[dotenv]"

Configure .env in your project, then ask the agent:
  "用 tg-notify 发 Telegram：构建完成"

EOF
