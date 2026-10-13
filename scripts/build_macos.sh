#!/usr/bin/env bash
# Build NotionPrettify.app for macOS.
#
# Usage:
#   bash scripts/build_macos.sh
#
# Output:
#   dist/NotionPrettify.app   — drag this into /Applications to install
#
# Prerequisites:
#   - uv (https://docs.astral.sh/uv/) installed and on PATH, or run via `mise run build:macos`

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

echo "==> Syncing dependencies (including build group)..."
uv sync --group build

echo "==> Cleaning previous build artefacts..."
rm -rf build dist

echo "==> Generating app icon from assets/icon.png..."
ICONSET="build/icon.iconset"
mkdir -p "$ICONSET"
for size in 16 32 128 256 512; do
    sips -z "$size" "$size" assets/icon.png --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
    sips -z "$((size * 2))" "$((size * 2))" assets/icon.png --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o build/icon.icns

echo "==> Building NotionPrettify.app..."
uv run pyinstaller NotionPrettify.spec --noconfirm

APP_PATH="dist/NotionPrettify.app"

if [ -d "$APP_PATH" ]; then
    # Ad-hoc sign the whole bundle so Gatekeeper and nested dylibs stay consistent
    # after copying to /Applications (PyInstaller signs the outer app; --deep catches Frameworks).
    echo "==> Ad-hoc signing app bundle (deep)..."
    codesign --force --deep --sign - "$APP_PATH"

    # Strip extended attributes from the build output (e.g. quarantine/provenance from tools).
    # End users who downloaded a zip may still need: xattr -cr /Applications/NotionPrettify.app
    xattr -cr "$APP_PATH" 2>/dev/null || true

    echo ""
    echo "Build succeeded!"
    echo "  App: $ROOT_DIR/$APP_PATH"
    echo "  CPU: $(uname -m) (use the same architecture on the Mac you install to; arm64 vs x86_64)"
    echo ""
    echo "To install:"
    echo "  cp -R \"$ROOT_DIR/$APP_PATH\" /Applications/"
    echo ""
    echo "If double-click does nothing or macOS says the app can't be opened:"
    echo "  • First launch: right-click the app → Open → Open (trusts this unsigned build)."
    echo "  • Or run:  xattr -cr /Applications/NotionPrettify.app"
    echo "  • If it still quits immediately, see:  ~/Library/Logs/NotionPrettify/crash.log"
else
    echo "Build failed — $APP_PATH not found." >&2
    exit 1
fi
