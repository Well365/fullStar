#!/usr/bin/env bash
# Resolve path to .env (mobile-agent root, cwd, or parents)
find_tgkit_env_file() {
  local start_dir="${1:-$(pwd)}"
  local skill_root="${2:-}"

  if [[ -n "${TGKIT_ENV_FILE:-}" && -f "$TGKIT_ENV_FILE" ]]; then
    echo "$TGKIT_ENV_FILE"
    return 0
  fi

  local _dir
  _dir="$(cd "$start_dir" 2>/dev/null && pwd || echo "$start_dir")"
  while [[ "$_dir" != "/" ]]; do
    if [[ -f "$_dir/.env" ]]; then
      echo "$_dir/.env"
      return 0
    fi
    _dir="$(dirname "$_dir")"
  done

  if [[ -n "$skill_root" ]]; then
    local parent
    parent="$(cd "$skill_root/.." 2>/dev/null && pwd || true)"
    for candidate in \
      "$parent/.env" \
      "$skill_root/.env"; do
      if [[ -f "$candidate" ]]; then
        echo "$candidate"
        return 0
      fi
    done
  fi

  return 1
}
