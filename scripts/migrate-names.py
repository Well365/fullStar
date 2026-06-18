#!/usr/bin/env python3
"""One-shot migration: apply first naming scheme across the repo."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "vendor", "WebDriverAgent"}
SKIP_SUFFIXES = {".pyc", ".png", ".jpg", ".jar", ".dylib", ".so", ".zip", ".aar"}

# Order matters: longer / more specific first
REPLACEMENTS: list[tuple[str, str]] = [
    # Path segments
    ("tg-notify-skill", "tg-notify-skill"),  # noop anchor
    ("tg_skill/", "tg-notify-skill/"),
    ("adb_skill/", "droid-ctl-skill/"),
    ("ios_skill/", "iphone-ctl-skill/"),
    ("scripts/tg-relay", "tg-relay"),
    ("scripts/run_tg_relay", "tg-relay/run_tg_relay"),
    ("scripts/tg_relay_patches", "tg-relay/tg_relay_patches"),
    ("scripts/tg-relay-daemon", "tg-relay/tg-relay-daemon"),
    ("scripts/tg-stack-daemon", "tg-relay/tg-stack-daemon"),
    ("scripts/setup-telegram", "tg-relay/setup-telegram"),
    ("scripts/relay_iterm_routing", "tg-relay/relay_iterm_routing"),
    ("scripts/iterm-", "term-bridge/iterm-"),
    ("scripts/iterm_", "term-bridge/iterm_"),
    ("autoqa-loop/", "game-qa-autopilot/"),
    ("devkit/", "mob-compose/"),
    ("tgkit/", "tg-notify/"),
    ("adbkit/", "droid-ctl/"),
    ("ioskit/", "iphone-ctl/"),
    # Python imports / modules
    ("from tgkit", "from tg_notify"),
    ("import tgkit", "import tg_notify"),
    ("tgkit.", "tg_notify."),
    ("from adbkit", "from droid_ctl"),
    ("import adbkit", "import droid_ctl"),
    ("adbkit.", "droid_ctl."),
    ("from ioskit", "from iphone_ctl"),
    ("import ioskit", "import iphone_ctl"),
    ("ioskit.", "iphone_ctl."),
    # pyproject package find
    ('include = ["tgkit*"]', 'include = ["tg_notify*"]'),
    ('include = ["adbkit*"]', 'include = ["droid_ctl*"]'),
    ('include = ["ioskit*"]', 'include = ["iphone_ctl*"]'),
    # CLI binary names in docs/scripts (command invocation)
    ("command -v tgkit", "command -v tg-notify"),
    ('["tgkit"', '["tg-notify"'),
    (" tgkit ", " tg-notify "),
    ("`tgkit`", "`tg-notify`"),
    ("command -v adbkit", "command -v droid-ctl"),
    (" adbkit ", " droid-ctl "),
    ("`adbkit`", "`droid-ctl`"),
    ("command -v ioskit", "command -v iphone-ctl"),
    (" ioskit ", " iphone-ctl "),
    ("`ioskit`", "`iphone-ctl`"),
    # devkit binary
    ("mob-compose/devkit", "mob-compose/compose"),
    ("$DEVKIT", "$COMPOSE"),
    ("devkit/devkit", "mob-compose/compose"),
    ("./devkit ", "./mob-compose/"),
    # Skill IDs / names
    ("mobile-agent-skill", "mob-remote-skill"),
    ("SKILL.zh-CN.md", "mob-remote-skill/SKILL.zh-CN.md"),
    ("SKILL.ja.md", "mob-remote-skill/SKILL.ja.md"),
    ("根目录 `SKILL.md`", "mob-remote-skill/SKILL.md"),
    ("根目录 SKILL.md", "mob-remote-skill/SKILL.md"),
    # mobagent -> mob (selective)
    ("./mobagent ", "./mob "),
    ("./mobagent\n", "./mob\n"),
    ("`./mobagent`", "`./mob`"),
    ("# ./mobagent", "# ./mob"),
    # Package names in pyproject
    ('name = "tgkit"', 'name = "tg-notify"'),
    ('name = "droid-ctl"', 'name = "droid-ctl"'),
    ('name = "iphone-ctl"', 'name = "iphone-ctl"'),
    ('tgkit = "tgkit.cli:main"', 'tg-notify = "tg_notify.cli:main"\ntgkit = "tg_notify.cli:main"'),
    ('adbkit = "adbkit.cli:main"', 'droid-ctl = "droid_ctl.cli:main"\nadbkit = "droid_ctl.cli:main"'),
    ('ioskit = "ioskit.cli:main"', 'iphone-ctl = "iphone_ctl.cli:main"\nioskit = "iphone_ctl.cli:main"'),
    # autoqa
    ("autoqa-loop", "game-qa-autopilot"),
    ("AutoQA-Loop", "Game-QA-Autopilot"),
    # ROOT paths in moved scripts
    ('ROOT / "scripts" / "iterm-', 'ROOT / "term-bridge" / "iterm-'),
    ('ROOT / "scripts" / "iterm_', 'ROOT / "term-bridge" / "iterm_'),
    ('ROOT / "scripts" / "tg-relay', 'ROOT / "tg-relay" / "tg-relay'),
    ('ROOT / "scripts" / "run_tg_relay', 'ROOT / "tg-relay" / "run_tg_relay'),
    ('parent.parent', 'parent.parent'),  # noop
]

# Fix ROOT for tg-relay and term-bridge - they are one level deeper now... 
# Actually tg-relay is at ROOT/tg-relay, so parent.parent from tg-relay/tg-relay.py is still ROOT. Good.

TEXT_EXTENSIONS = {
    ".md", ".py", ".sh", ".toml", ".txt", ".json", ".ts", ".mjs", ".yaml", ".yml",
    ".example", ".env", ".gitignore", "mobagent", "compose", "devkit",
}


def should_process(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    if path.suffix in SKIP_SUFFIXES:
        return False
    if path.name in ("migrate-names.py",):
        return False
    if path.suffix in TEXT_EXTENSIONS:
        return True
    if path.name in ("mobagent", "compose", "mob", ".env.example"):
        return True
    return False


def migrate_file(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False
    orig = text
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and should_process(path):
            if migrate_file(path):
                changed += 1
                print(f"  updated: {path.relative_to(ROOT)}")
    print(f"\n{changed} files updated")


if __name__ == "__main__":
    main()
