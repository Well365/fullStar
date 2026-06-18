#!/usr/bin/env bash
# Install mob-remote skills — all or selected modules (composable)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

declare -A SKILL_DIR=(
  [tg]=tg-notify-skill
  [tg-notify]=tg-notify-skill
  [tgkit]=tg-notify-skill
  [adb]=droid-ctl-skill
  [droid-ctl]=droid-ctl-skill
  [ios]=iphone-ctl-skill
  [iphone-ctl]=iphone-ctl-skill
  [mob-remote]=mob-remote-skill
  [mobile-agent]=mob-remote-skill
)

declare -A SKILL_CURSOR_NAME=(
  [tg]=tg-notify
  [tg-notify]=tg-notify
  [tgkit]=tg-notify
  [adb]=droid-ctl
  [droid-ctl]=droid-ctl
  [ios]=iphone-ctl
  [iphone-ctl]=iphone-ctl
  [mob-remote]=mob-remote
  [mobile-agent]=mob-remote
)

usage() {
  cat <<'EOF'
Usage: install-skill.sh [options] [SKILL ...]

Install Agent skills to ~/.cursor/skills and ~/.claude/skills.

Available skills:
  tg-notify, tg     Telegram outbound notify
  droid-ctl, adb    Android device control
  iphone-ctl, ios   iPhone device control + WDA
  mob-remote        Umbrella skill (full workflow)

Options:
  --only LIST     Comma-separated skills
  --all           Install all skills (default)
  --list          List available skills
  -h, --help

Examples:
  ./mob install-skill
  ./mob install-skill --only tg-notify,droid-ctl
  ./mob install-skill --only mob-remote
EOF
}

list_skills() {
  echo "Available: tg-notify | droid-ctl | iphone-ctl | mob-remote"
  echo "Legacy IDs: tg, adb, ios, mobile-agent"
}

install_mob_remote() {
  local target_base="$1" label="$2"
  if [[ ! -d "$(dirname "$target_base")" ]]; then
    echo "skip $label: parent dir missing"
    return 0
  fi
  mkdir -p "$target_base/mob-remote"
  cp "$ROOT/mob-remote-skill/SKILL.md" "$target_base/mob-remote/SKILL.md"
  cp "$ROOT/docs/SKILL_COMPOSE.md" "$target_base/mob-remote/SKILL_COMPOSE.md" 2>/dev/null || true
  cp "$ROOT/README.md" "$target_base/mob-remote/README.md"
  echo "installed → $target_base/mob-remote/"
}

install_sub_skill() {
  local id="$1"
  local dir="${SKILL_DIR[$id]:-}"
  if [[ -z "$dir" ]]; then
    echo "unknown skill: $id" >&2
    return 1
  fi
  local setup="$ROOT/$dir/scripts/install-skill.sh"
  if [[ -x "$setup" ]]; then
    echo "→ $id ($dir)"
    "$setup" | sed 's/^/  /'
  else
    echo "skip $id: $setup not found" >&2
    return 1
  fi
}

normalize_id() {
  local raw="${1,,}"
  raw="${raw/_skill/}"
  raw="${raw/-skill/}"
  case "$raw" in
    tg|tgkit|tg-notify|telegram|notify) echo "tg-notify" ;;
    adb|android|droid|droid-ctl) echo "droid-ctl" ;;
    ios|iphone|iphone-ctl|wda) echo "iphone-ctl" ;;
    mob-remote|mobile-agent|mobileagent|all|umbrella) echo "mob-remote" ;;
    *) echo "$raw" ;;
  esac
}

SELECTED=()
ONLY_MODE=0
INSTALL_ALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --only)
      ONLY_MODE=1
      IFS=',' read -ra parts <<< "${2:-}"
      for p in "${parts[@]}"; do
        SELECTED+=("$(normalize_id "$p")")
      done
      shift 2
      ;;
    --all) INSTALL_ALL=1; shift ;;
    --list) list_skills; exit 0 ;;
    -h|--help) usage; exit 0 ;;
    --*) echo "unknown option: $1" >&2; usage; exit 1 ;;
    *)
      SELECTED+=("$(normalize_id "$1")")
      shift
      ;;
  esac
done

if [[ "$INSTALL_ALL" -eq 1 ]] || [[ ${#SELECTED[@]} -eq 0 ]]; then
  SELECTED=(tg-notify droid-ctl iphone-ctl mob-remote)
fi

declare -A _seen=()
UNIQUE=()
for s in "${SELECTED[@]}"; do
  [[ -n "$s" ]] || continue
  [[ -n "${_seen[$s]:-}" ]] && continue
  _seen[$s]=1
  UNIQUE+=("$s")
done
SELECTED=("${UNIQUE[@]}")

echo "Installing skills: ${SELECTED[*]}"
echo ""

FAIL=0
for id in "${SELECTED[@]}"; do
  if [[ "$id" == "mob-remote" ]]; then
    install_mob_remote "$HOME/.cursor/skills" "Cursor"
    install_mob_remote "$HOME/.claude/skills" "Claude Code"
  else
    install_sub_skill "$id" || FAIL=$((FAIL + 1))
  fi
done

echo ""
if [[ "$FAIL" -eq 0 ]]; then
  echo "Done. Installed: ${SELECTED[*]}"
  echo "Check: ./mob check"
else
  echo "Completed with $FAIL error(s)" >&2
  exit 1
fi
