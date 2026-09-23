# Platform integration

Right-click, drop-target and drop-folder integration for MetaCLS.
Except for the downloadable macOS windowed app, `metacls` must be installed and on `PATH` (`pip install metacls`,
`pipx install metacls`, or a venv you add to `PATH`). Everything here
scrubs **in place**: the originals are overwritten with the cleaned
version.

## macOS

### Drop app: `MetaCLS.app`

```bash
platform/macos/build-app.sh            # -> /Applications/MetaCLS.app
```

Builds a self-contained droplet with `osacompile` (no Xcode). Drag files
onto its Finder icon or its Dock icon; double-click it to pick files with
a dialog. A notification reports the result. Delete the `.app` to remove
it. Source: `MetaCLS-droplet.applescript`.

### Drop window: `MetaCLS Drop.app`

Download the ready-to-run **DMG** from [GitHub Releases](https://github.com/gorkemguler/MetaCLS/releases).
Choose `arm64` for Apple Silicon (M-series) or `x86_64` for Intel, open the
DMG, and drag **MetaCLS Drop.app** to **Applications**. Requires macOS 14+.
No Python, pip, Homebrew or separate MetaCLS/ExifTool installation is needed.
Double-click the app for the persistent window; drop files or use **Choose files…**.
The app also accepts files dropped onto its Finder/Dock icon. Files are cleaned
in place, and results appear in the log without freezing the window.

Community builds are ad-hoc signed, without Apple Developer ID/notarization.
If macOS blocks the first launch, use **System Settings → Privacy & Security →
Open Anyway** after attempting to open the downloaded app. See
[Apple's instructions](https://support.apple.com/102445).

Python, Cocoa bindings, the cleaning engine and ExifTool are bundled. ExifTool
uses macOS's built-in `/usr/bin/perl`. LibreOffice is not included; some legacy
Office files may still need conversion. The window supports the existing
PDF / Office / SVG / image formats, not recursive archives or media mode.
Delete the app to uninstall it. Old `drop-venv` installations are no longer used.

#### Building and publishing

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install . -r platform/macos/requirements-build.txt
PYTHON="$PWD/.venv/bin/python" platform/macos/build-drop-app.sh
```

Outputs go to `dist/macos/` (or an explicit output directory): `.app`, `.dmg`,
`.zip` and SHA-256 checksums. Build separately on each architecture. The build
verifies the downloaded ExifTool checksum, validates the app signature, and
smoke-tests PDF, JPEG and Office cleaning with a system-only PATH. Dependency
licenses are included under `Contents/Resources/licenses`.

`.github/workflows/macos.yml` builds and tests both architectures for relevant
pull requests. A `v*` tag attaches Mac downloads to the regular release; a
`macos-v*` tag creates a desktop prerelease without triggering PyPI publishing.
Manual workflow runs produce downloadable Actions artifacts.

For Apple-signed distribution, install a Developer ID Application identity in
the build machine's keychain, set `MACOS_CODESIGN_IDENTITY`, and set
`MACOS_NOTARY_PROFILE` to an existing `xcrun notarytool store-credentials`
keychain profile. The script signs, submits and staples the app and DMG before
calculating checksums. GitHub's default builds remain ad-hoc signed until an
Apple signing identity and notarization credentials are provisioned there.

### Finder Quick Action

```bash
platform/macos/install-quick-action.sh
```

Adds a **Scrub metadata** Quick Action in `~/Library/Services/`.
Right-click one or more files in Finder → *Quick Actions* → *Scrub
metadata*. Remove it by deleting `~/Library/Services/Scrub metadata.workflow`.
`scrub-selected.sh` is the script it calls.

## Windows

### Drop window: `MetaCLS-drop.ps1`

```powershell
powershell -ExecutionPolicy Bypass -File platform\windows\MetaCLS-drop.ps1
```

A WinForms window styled to match the project's dark/green branding
(the "meta**cls**" wordmark, a dashed drop zone, a colour-coded result
list): drop files onto it (or pass them as arguments) and they're
scrubbed. On Windows 10 1809+/11 the title bar follows in dark mode too.

### Send-to menu

```powershell
powershell -ExecutionPolicy Bypass -File platform\windows\install-sendto.ps1
powershell -ExecutionPolicy Bypass -File platform\windows\install-sendto.ps1 -Uninstall
```

Adds **MetaCLS** to the right-click *Send to* menu, opening the drop
window pre-loaded with the selected files.

### Explorer right-click

```powershell
powershell -ExecutionPolicy Bypass -File platform\windows\install-context-menu.ps1
powershell -ExecutionPolicy Bypass -File platform\windows\install-context-menu.ps1 -Uninstall
```

Adds *Scrub metadata with MetaCLS* to the right-click menu for PDF /
Office / image / SVG files (current user, no admin).

### winget

`platform/windows/winget/` holds a manifest for `GorkemGuler.MetaCLS`,
ready to submit to `winget-pkgs` once a release ships a Windows artifact.
See the README there.

## Linux

### Drop window: `metacls_drop_gtk.py`

```bash
python3 platform/linux/metacls_drop_gtk.py
```

The GTK3 counterpart to the macOS/Windows drop windows, styled the same
way: a real window you leave open, drop files onto, and watch a
colour-coded results log. Needs PyGObject (`python3-gi` on
Debian/Ubuntu, `python3-gobject` on Fedora, `python-gobject` on Arch;
usually already installed on GNOME/GTK desktops).

### Desktop launcher + "Open With" handler

```bash
platform/linux/install-desktop.sh              # install
platform/linux/install-desktop.sh --uninstall
```

Installs `metacls.desktop` (+ `metacls-drop.sh` into `~/.local/bin`).
Drag files onto **MetaCLS** in your applications menu, or right-click a
file → *Open With* → *MetaCLS*. With no files it opens a `zenity` file
picker. Results go to `zenity` / `notify-send` / stdout.

### File-manager script (Nautilus / Nemo / Caja)

```bash
mkdir -p ~/.local/share/nautilus/scripts
install -m755 platform/linux/nautilus-scrub-metadata.sh \
  ~/.local/share/nautilus/scripts/"Scrub metadata"
```

Right-click → *Scripts* → *Scrub metadata* (see the script header for
Nemo/Caja paths).

### Drop-folder daemon

`platform/linux/metacls-watch@.service` is a systemd template unit for
`metacls watch`: see the
[README](https://github.com/gorkemguler/MetaCLS/blob/main/README.md#watch-keep-a-drop-folder-scrubbed).
