#!/usr/bin/env bash
# ABOUTME: Automated release script — bumps VERSION, tags, creates GH release, updates Homebrew formula.
# ABOUTME: Usage: ./scripts/release.sh [version]  (if no version, increments minor by 0.1)
set -euo pipefail
IFS=$'\n\t'

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TAP_REPO="$HOME/code/tigoss/homebrew-tap"
TAP_FORMULA="$TAP_REPO/Formula/real-esrgan-pro.rb"
GH_REPO="tigger04/Real-ESRGAN"

cd "$REPO_ROOT"

# --- Determine version ---
CURRENT_VERSION=$(cat VERSION)

if [[ $# -ge 1 ]]; then
    NEW_VERSION="$1"
else
    # Increment minor version by 0.1
    IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"
    minor=$((minor + 1))
    NEW_VERSION="${major}.${minor}.0"
fi

echo "Releasing: $CURRENT_VERSION -> $NEW_VERSION"

# --- Update VERSION file ---
echo "$NEW_VERSION" > VERSION

# --- Commit and tag ---
git add VERSION
git commit -m "release: v${NEW_VERSION}"
git tag "v${NEW_VERSION}"

# --- Push to origin ---
git push origin master
git push origin "v${NEW_VERSION}"

# --- Create GitHub release ---
gh release create "v${NEW_VERSION}" \
    --repo "$GH_REPO" \
    --title "v${NEW_VERSION}" \
    --generate-notes

# --- Compute SHA256 of the release archive ---
ARCHIVE_URL="https://github.com/${GH_REPO}/archive/refs/tags/v${NEW_VERSION}.tar.gz"
echo "Downloading archive to compute SHA256..."
TMPFILE=$(mktemp)
cleanup() {
    rm -f -- "$TMPFILE"
}
trap cleanup EXIT

curl -sL "$ARCHIVE_URL" -o "$TMPFILE"
SHA256=$(shasum -a 256 "$TMPFILE" | cut -d ' ' -f 1)
echo "SHA256: $SHA256"

# --- Update Homebrew formula ---
if [[ -f "$TAP_FORMULA" ]]; then
    # Update version, url, and sha256 in the formula
    # These are config file edits (Ruby formula), not source code — acceptable per CODING.md
    python3 -c "
import re, sys

with open('$TAP_FORMULA', 'r') as f:
    content = f.read()

content = re.sub(
    r'url \"https://github.com/${GH_REPO}/archive/refs/tags/v[^\"]+\.tar\.gz\"',
    'url \"${ARCHIVE_URL}\"',
    content)
content = re.sub(
    r'sha256 \"[a-f0-9]+\"',
    'sha256 \"${SHA256}\"',
    content)
content = re.sub(
    r'version \"[^\"]+\"',
    'version \"${NEW_VERSION}\"',
    content)

with open('$TAP_FORMULA', 'w') as f:
    f.write(content)
"
    echo "Updated Homebrew formula."

    # Commit and push tap
    cd "$TAP_REPO"
    git add Formula/real-esrgan-pro.rb
    git commit -m "real-esrgan-pro: update to v${NEW_VERSION}"
    git push origin main
    echo "Homebrew tap updated and pushed."
else
    echo "Homebrew formula not found at $TAP_FORMULA — skipping tap update."
    echo "Create the formula first, then re-run or update manually."
fi

echo ""
echo "Release v${NEW_VERSION} complete."
