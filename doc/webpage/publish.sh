#!/bin/bash
# Generates the FMICodeGenerator webpage from the AsciiDoc sources in this
# directory and copies the result to <repo>/docs (served by GitHub Pages).
#
# Usage: ./publish.sh            (can be called from any directory)
#
# Requirements: asciidoctor (with the rouge gem for syntax highlighting)
#
# Note: the content of <repo>/docs is replaced completely on every run - do not
#       edit files there by hand.

set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SRC_DIR/../.." && pwd)"
TARGET_DIR="$REPO_DIR/docs"

# static asset directories copied as-is
ASSET_DIRS="css fonts images data"

command -v asciidoctor >/dev/null || { echo "ERROR: asciidoctor not found in PATH" >&2; exit 1; }

BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT

echo "*** Generating html ***"
cd "$SRC_DIR"
# all top-level .adoc files are pages, except partials starting with '_'
PAGES=$(ls *.adoc | grep -v '^_')
for page in $PAGES; do
	echo "  $page"
done
# --failure-level WARN: abort on broken includes, unknown attributes etc.
asciidoctor --failure-level WARN -D "$BUILD_DIR" $PAGES

echo "*** Copying assets ***"
for d in $ASSET_DIRS; do
	cp -r "$d" "$BUILD_DIR/"
done
# tell GitHub Pages to serve the files as they are (no Jekyll processing)
touch "$BUILD_DIR/.nojekyll"

echo "*** Updating $TARGET_DIR ***"
rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"
cp -r "$BUILD_DIR/." "$TARGET_DIR/"

echo "*** Finished successfully ***"
echo "Open $TARGET_DIR/index.html to preview the webpage."
