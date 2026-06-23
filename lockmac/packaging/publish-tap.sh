#!/usr/bin/env bash
# publish-tap.sh — one-shot: publish lockmac as a Homebrew tap.
#
# Creates (if missing) the tap repo `homebrew-lockmac`, builds the release
# tarball of the lockmac/ subtree, makes a GitHub Release on the main repo,
# fills the formula sha256, and pushes the formula to the tap. After this:
#     brew tap <owner>/lockmac && brew install lockmac
#
# Requires: gh (logged in: `gh auth login`), git. Idempotent-ish; re-run to bump.
set -euo pipefail

OWNER="${LOCKMAC_OWNER:-wwk5c5gh3}"          # GitHub owner for the tap + release
MAIN_REPO="${LOCKMAC_MAIN_REPO:-$OWNER/fullStar}"   # repo holding the release asset
VERSION="${LOCKMAC_VERSION:-0.1.0}"
TAG="lockmac-v${VERSION}"
TAP_REPO="$OWNER/homebrew-lockmac"

PKG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # lockmac/packaging
LOCKMAC_DIR="$(cd "$PKG_DIR/.." && pwd)"                  # lockmac/
REPO_ROOT="$(cd "$LOCKMAC_DIR/.." && pwd)"                # fullStar/
FORMULA="$LOCKMAC_DIR/Formula/lockmac.rb"
TARBALL="/tmp/lockmac-${VERSION}.tar.gz"

say() { echo "▸ $*"; }
die() { echo "✗ $*" >&2; exit 1; }

command -v gh >/dev/null || die "需要 gh CLI（brew install gh && gh auth login）"
gh auth status >/dev/null 2>&1 || die "gh 未登录：先运行 gh auth login"

# 1. release tarball of the lockmac/ subtree + sha256
say "生成 release tarball"
( cd "$REPO_ROOT" && git archive --format=tar.gz --prefix="lockmac-${VERSION}/" HEAD:lockmac > "$TARBALL" )
SHA="$(shasum -a 256 "$TARBALL" | awk '{print $1}')"
say "sha256 = $SHA"

# 2. patch the formula's sha256 to match this tarball
say "更新 formula sha256"
sed -i '' "s|sha256 \"[0-9a-f]*\"|sha256 \"$SHA\"|" "$FORMULA"

# 3. GitHub Release on the main repo (asset = tarball)
say "创建/更新 GitHub Release $TAG @ $MAIN_REPO"
if gh release view "$TAG" -R "$MAIN_REPO" >/dev/null 2>&1; then
  gh release upload "$TAG" "$TARBALL" -R "$MAIN_REPO" --clobber
else
  gh release create "$TAG" "$TARBALL" -R "$MAIN_REPO" \
    --title "lockmac $VERSION" --notes "lockmac $VERSION (Homebrew release asset)"
fi

# 4. tap repo: create if missing, then push the formula
say "准备 tap repo $TAP_REPO"
TAP_TMP="$(mktemp -d)"
if gh repo view "$TAP_REPO" >/dev/null 2>&1; then
  gh repo clone "$TAP_REPO" "$TAP_TMP/tap" -- -q
else
  gh repo create "$TAP_REPO" --public -d "Homebrew tap for lockmac" >/dev/null
  git -C "$TAP_TMP" clone "https://github.com/$TAP_REPO.git" tap -q 2>/dev/null || \
    gh repo clone "$TAP_REPO" "$TAP_TMP/tap" -- -q
fi
mkdir -p "$TAP_TMP/tap/Formula"
cp "$FORMULA" "$TAP_TMP/tap/Formula/lockmac.rb"
(
  cd "$TAP_TMP/tap"
  git add Formula/lockmac.rb
  git commit -q -m "lockmac $VERSION" || { echo "  (formula 无变化)"; exit 0; }
  git push -q origin HEAD
)
rm -rf "$TAP_TMP" "$TARBALL"

cat <<EOF

✓ 发布完成。用户安装：
    brew tap ${OWNER}/lockmac
    brew install lockmac
  或免 release 直接装：
    brew install --HEAD ${OWNER}/lockmac/lockmac

记得把更新后的 formula（sha256=$SHA）也提交回主仓库。
EOF
