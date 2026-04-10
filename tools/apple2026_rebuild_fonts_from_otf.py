#!/usr/bin/env python3
"""
Rebuild `fonts/*.fnt` from Apple-vendored OTF under `Apple Fonts/` using
`tools/otf_to_rb12_fnt.py` (FreeType). Skips missing sources with a clear message.

Run from repo root:
  python tools/apple2026_rebuild_fonts_from_otf.py
  python tools/apple2026_rebuild_fonts_from_otf.py --dry-run

After rebuild, run:
  python tools/analyze_rb12_fonts.py
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
OTF_TOOL = ROOT / "tools" / "otf_to_rb12_fnt.py"
FONTS_OUT = ROOT / "fonts"
SF_PRO = ROOT / "Apple Fonts" / "SF Pro"
SF_COMPACT = ROOT / "Apple Fonts" / "SF Compact"

# (output_name, source_otf, pixel_size, track_px, space_extra)
# track: slight openness for menu/list (Apple-like); Display Bold slightly less.
JOBS: List[Tuple[str, Path, int, float, int]] = [
    ("35-SFProDisplay-Bold.fnt", SF_PRO / "SF-Pro-Display-Bold.otf", 35, 0.22, 1),
    ("28-SFProDisplay-Bold.fnt", SF_PRO / "SF-Pro-Display-Bold.otf", 28, 0.20, 0),
    ("25-SFProDisplay-Bold.fnt", SF_PRO / "SF-Pro-Display-Bold.otf", 25, 0.20, 0),
    # Figma 1:4008 list labels: SF Pro Text Regular 22px, tracking ~0.5px
    ("22-SFProText-Regular.fnt", SF_PRO / "SF-Pro-Text-Regular.otf", 22, 0.50, 1),
    # Same face at 20px: slightly more open for list readability
    ("20-SFProText-Regular.fnt", SF_PRO / "SF-Pro-Text-Regular.otf", 20, 0.50, 1),
    # Picture Flow tracklist: readable without shell 22px list size
    ("18-SFProText-Regular.fnt", SF_PRO / "SF-Pro-Text-Regular.otf", 18, 0.40, 1),
    # Dense track/song list font: Music subfolders, Cover Flow tracklist, playlist viewer
    ("16-SFProText-Regular.fnt", SF_PRO / "SF-Pro-Text-Regular.otf", 16, 0.35, 0),
    ("22-SFProText-Medium.fnt", SF_PRO / "SF-Pro-Text-Medium.otf", 22, 0.30, 1),
    ("22-SFCompactDisplay-Semibold.fnt", SF_COMPACT / "SF-Compact-Display-Semibold.otf", 22, 0.28, 1),
    ("20-SFProText-Medium.fnt", SF_PRO / "SF-Pro-Text-Medium.otf", 20, 0.28, 1),
    ("19-SFProText-Medium.fnt", SF_PRO / "SF-Pro-Text-Medium.otf", 19, 0.28, 1),
    ("19-SFProText-Semibold.fnt", SF_PRO / "SF-Pro-Text-Semibold.otf", 19, 0.26, 1),
    ("17-SFProText-Bold.fnt", SF_PRO / "SF-Pro-Text-Bold.otf", 17, 0.24, 0),
    ("16-SFProText-Medium.fnt", SF_PRO / "SF-Pro-Text-Medium.otf", 16, 0.26, 1),
    ("16-SFProText-Semibold.fnt", SF_PRO / "SF-Pro-Text-Semibold.otf", 16, 0.24, 1),
    ("15-SFProText-Medium.fnt", SF_PRO / "SF-Pro-Text-Medium.otf", 15, 0.26, 0),
    ("15-SFProText-Semibold.fnt", SF_PRO / "SF-Pro-Text-Semibold.otf", 15, 0.24, 0),
    ("14-SFProText-Regular.fnt", SF_PRO / "SF-Pro-Text-Regular.otf", 14, 0.35, 1),
    ("13-SFCompactText-Regular.fnt", SF_COMPACT / "SF-Compact-Text-Regular.otf", 13, 0.28, 0),
]


def run_one(otf: Path, out: Path, px: int, track: float, space: int, dry: bool) -> bool:
    cmd = [
        sys.executable,
        str(OTF_TOOL),
        str(otf),
        str(out),
        "-p",
        str(px),
        "--track",
        str(track),
        "--space-extra",
        str(space),
    ]
    if dry:
        print(" ".join(cmd))
        return otf.is_file()
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
    return proc.returncode == 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not OTF_TOOL.is_file():
        sys.exit(f"Missing {OTF_TOOL}")

    ok = 0
    skipped = 0
    for name, src, px, track, space in JOBS:
        out = FONTS_OUT / name
        if not src.is_file():
            print(f"[skip] {name} — no source: {src}")
            skipped += 1
            continue
        print(f"[build] {name} <= {src.name} px={px} track={track}")
        if run_one(src, out, px, track, space, args.dry_run):
            ok += 1

    print(f"\nDone: built {ok}, skipped {skipped} (install OTFs under Apple Fonts/ to rebuild all).")


if __name__ == "__main__":
    main()
