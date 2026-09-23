#!/bin/bash
# Build a portable windowed app, ZIP and drag-to-Applications DMG.
# Requires a build environment only; the resulting app needs no Python/pip.
# Usage: PYTHON=/path/to/python3 platform/macos/build-drop-app.sh [OUTPUT_DIR]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"
cd "$root"
python="${PYTHON:-python3}"
dest="${1:-$root/dist/macos}"
mkdir -p "$dest" build/vendor build/macos
# Resolve before changing directories, including output paths with spaces.
dest="$(cd "$dest" && pwd)"
export PYINSTALLER_CONFIG_DIR="$root/build/pyinstaller-cache"
version="$("$python" -c 'from importlib.metadata import version; print(version("metacls"))')"
arch="$("$python" -c 'import platform; print(platform.machine())')"
archive="$root/build/vendor/exiftool-13.59.tar.gz"
if [ ! -f "$archive" ]; then
    curl --fail --location --retry 3 \
        https://github.com/exiftool/exiftool/archive/refs/tags/13.59.tar.gz -o "$archive"
fi
printf '%s  %s\n' 87d3317882fdae9cb4dcfe57a96a378d0132ffc02c731315bf128b19ddcf7aac "$archive" | shasum -a 256 -c -
tar -xzf "$archive" -C build/vendor
# Avoid a dependency on a Homebrew Perl interpreter.
"$python" -c 'from pathlib import Path; p=Path("build/vendor/exiftool-13.59/exiftool"); s=p.read_text(); p.write_text("#!/usr/bin/perl\n" + s.split("\n", 1)[1])'
chmod +x build/vendor/exiftool-13.59/exiftool
"$python" "$here/make-icon.py"
"$python" "$here/collect-licenses.py" > build/macos/THIRD-PARTY-LICENSES.txt
"$python" -m PyInstaller --noconfirm --clean --distpath "$dest" \
    --workpath "$root/build/pyinstaller" "$here/MetaCLS.spec"
app="$dest/MetaCLS Drop.app"
codesign --verify --deep --strict "$app"
"$python" "$here/smoke-test.py" "$app"
base="MetaCLS-Drop-$version-macos-$arch"
# A Developer ID signature is optional for local/community builds.
# Set MACOS_NOTARY_PROFILE to a notarytool keychain profile to notarize.
if [ -n "${MACOS_NOTARY_PROFILE:-}" ]; then
    : "${MACOS_CODESIGN_IDENTITY:?Notarization requires a Developer ID Application identity}"
    ditto -c -k --sequesterRsrc --keepParent "$app" "$dest/notarize.zip"
    xcrun notarytool submit "$dest/notarize.zip" --keychain-profile "$MACOS_NOTARY_PROFILE" --wait
    xcrun stapler staple "$app"
    rm "$dest/notarize.zip"
fi
ditto -c -k --sequesterRsrc --keepParent "$app" "$dest/$base.zip"
stage="$(mktemp -d "$root/build/macos/dmg.XXXXXX")"
trap 'rm -rf "$stage"' EXIT
ditto "$app" "$stage/MetaCLS Drop.app"
ln -s /Applications "$stage/Applications"
cp "$here/INSTALL.txt" "$stage/READ ME.txt"
hdiutil create -volname "MetaCLS Drop" -srcfolder "$stage" -ov -format UDZO "$dest/$base.dmg"
if [ -n "${MACOS_CODESIGN_IDENTITY:-}" ]; then
    codesign --sign "$MACOS_CODESIGN_IDENTITY" --timestamp "$dest/$base.dmg"
fi
if [ -n "${MACOS_NOTARY_PROFILE:-}" ]; then
    xcrun notarytool submit "$dest/$base.dmg" --keychain-profile "$MACOS_NOTARY_PROFILE" --wait
    xcrun stapler staple "$dest/$base.dmg"
fi
(cd "$dest" && shasum -a 256 "$base.dmg" "$base.zip" > "$base.sha256")
echo "Built $dest/$base.dmg"
