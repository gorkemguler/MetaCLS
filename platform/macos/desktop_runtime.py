"""Shared runtime for the source launcher and the self-contained macOS app."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def configure_runtime() -> None:
    if getattr(sys, "frozen", False):
        vendor = Path(sys._MEIPASS) / "vendor" / "exiftool"
        os.environ["PATH"] = str(vendor) + os.pathsep + "/usr/bin:/bin:/usr/sbin:/sbin"
        # Finder's working directory is not a user's project configuration.
        # Keep CLI configuration discovery away from the app and source checkout.
        os.chdir(Path.home())


def cli_command() -> list[str] | None:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--cli"]
    override = os.environ.get("METACLS")
    for candidate in (
        override, shutil.which("metacls"),
        str(Path.home() / ".local/bin/metacls"),
        "/opt/homebrew/bin/metacls", "/usr/local/bin/metacls",
    ):
        if candidate and shutil.which(candidate):
            return [candidate]
    return None


def scrub_paths(paths: list[str]) -> list[str]:
    from metacls.config import DEFAULT_FILETYPES

    command = cli_command()
    if command is None:
        return ["! MetaCLS is missing. Install metacls or use the packaged Mac app."]
    lines = []
    ok = fail = skipped = 0
    for item in paths:
        path = Path(item).absolute()
        if not path.is_file() or path.suffix.lower().lstrip(".") not in DEFAULT_FILETYPES:
            skipped += 1
            lines.append(f"SKIP  {path.name}  (not a supported document or image)")
            continue
        try:
            result = subprocess.run(
                [*command, "clean", "--in-place", "--yes", "--no-json-report", "--no-html-report", "--", str(path)],
                capture_output=True, text=True, errors="replace", timeout=300,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            fail += 1
            lines.append(f"FAIL  {path.name}  ({exc})")
            continue
        if result.returncode == 0:
            ok += 1
            lines.append(f"ok    {path.name}")
        else:
            fail += 1
            detail = "metadata remains; review the file" if result.returncode == 2 else f"exit {result.returncode}"
            lines.append(f"FAIL  {path.name}  ({detail})")
            output = (result.stderr or result.stdout).strip()
            if output:
                lines.append(output[-2000:])
    lines.append(f"-- scrubbed {ok}, failed {fail}, skipped {skipped} --")
    return lines
