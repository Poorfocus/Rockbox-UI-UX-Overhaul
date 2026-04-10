#!/usr/bin/env python3
"""Static anti-regression audit for wps/Apple2026.wps.
Checks: non-ASCII, duplicate image IDs, undefined %xd refs (multi-frame aware),
        font file existence, BMP asset existence, %VB art viewport placement.

Known safe patterns (not bugs):
  - %?if(%mp,<,4) and %?if(%pv, >,0): the < / > inside tag params are comparison
    operators, not conditional brackets. Naive bracket counting produces false positives.
  - %xl(P,...,4) defines 4 frames Pa/Pb/Pc/Pd -- %xd(Pa) etc. are valid.
"""

from __future__ import annotations

import re
import sys
import collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WPS = ROOT / "wps" / "Apple2026.wps"
BMP_DIR = ROOT / "wps" / "Apple2026"
FONTS_DIR = ROOT / "fonts"


def expand_frames(tag_id: str, frame_count: int) -> list[str]:
    """Expand %xl(ID,...,N) into frame IDs: IDa, IDb, IDc, ..."""
    frames = []
    for i in range(frame_count):
        suffix = chr(ord('a') + i)
        frames.append(f"{tag_id}{suffix}")
    return frames


def main() -> int:
    text = WPS.read_text(encoding="utf-8")
    lines = text.splitlines()
    issues: list[str] = []

    # A. Non-ASCII (critical -- Rockbox skin parser may choke on non-ASCII bytes)
    print("=== A. NON-ASCII CHECK ===")
    bad = [(i, ord(ch)) for i, ch in enumerate(text) if ord(ch) > 127]
    print(f"Non-ASCII chars: {len(bad)}")
    for idx, code in bad[:10]:
        issues.append(f"Non-ASCII char U+{code:04X} at byte {idx}")
        print(f"  U+{code:04X} at byte {idx}")
    if not bad:
        print("PASS")

    # B. Image ID audit (multi-frame aware)
    print("\n=== B. IMAGE ID AUDIT ===")
    # %xl(ID,file.bmp,x,y[,frames])  -- multi-frame preload
    xl_matches = re.findall(r'%xl\(([^,\)]+),([^,\)]+),[^,\)]+,[^,\)]+(?:,(\d+))?\)', text)
    # %x(ID,file.bmp,...) -- inline define
    x_ids = re.findall(r'%x\(([^,\)]+),', text)
    # %xd(ID) -- draw reference
    xd_ids = re.findall(r'%xd\(([^,\)]+)\)', text)

    all_defs: dict[str, int] = {}  # id -> count
    for tag_id, _, frames_str in xl_matches:
        tag_id = tag_id.strip()
        all_defs[tag_id] = all_defs.get(tag_id, 0) + 1
        if frames_str:
            n = int(frames_str)
            for fid in expand_frames(tag_id, n):
                all_defs[fid] = all_defs.get(fid, 0) + 1
        else:
            # Single frame: IDa is the only frame
            fid = f"{tag_id}a"
            all_defs[fid] = all_defs.get(fid, 0) + 1
    for tag_id in x_ids:
        tag_id = tag_id.strip()
        all_defs[tag_id] = all_defs.get(tag_id, 0) + 1

    dups = [k for k, v in all_defs.items() if v > 1]
    if dups:
        print(f"DUPLICATE defs: {dups}")
        issues.append(f"Duplicate image IDs: {dups}")
    else:
        print("No duplicate image IDs. PASS")

    undefined = sorted(set(i.strip() for i in xd_ids if i.strip() not in all_defs))
    if undefined:
        print(f"UNDEFINED %xd refs: {undefined}")
        issues.append(f"Undefined %xd refs: {undefined}")
    else:
        print("All %xd refs resolve. PASS")

    # C. Font files
    print("\n=== C. FONT AUDIT ===")
    fl_refs = re.findall(r'%Fl\(\d+,([^)]+)\)', text)
    all_ok = True
    for fnt in fl_refs:
        fnt = fnt.strip()
        exists = (FONTS_DIR / fnt).exists()
        status = "OK" if exists else "MISSING"
        print(f"  {fnt}: {status}")
        if not exists:
            issues.append(f"Font missing: {fnt}")
            all_ok = False
    if all_ok:
        print("All fonts present. PASS")

    # D. BMP assets
    print("\n=== D. BMP ASSET AUDIT ===")
    bmp_pattern = re.compile(
        r'(?:%xl\([^,]+,|%x\([^,]+,|image,|backdrop,)([^,\)\s]+\.bmp)'
    )
    bmp_refs = list(dict.fromkeys(bmp_pattern.findall(text)))
    all_ok = True
    for b in bmp_refs:
        exists = (BMP_DIR / b).exists()
        status = "OK" if exists else "MISSING"
        print(f"  {b}: {status}")
        if not exists:
            issues.append(f"BMP missing: {b}")
            all_ok = False
    if all_ok:
        print("All BMP assets present. PASS")

    # E. %VB album art structure
    print("\n=== E. %VB ALBUM ART CHECK ===")
    # Verify: a %VB viewport exists that ALSO contains %Cl
    # We track viewport blocks: a %VB viewport starts on a line with %VB and a %V tag,
    # and ends when the next top-level %V starts.
    in_vb_block = False
    art_in_vb = False
    for ln, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        # New viewport line
        if s.startswith("%V(") or s.startswith("%Vl(") or s.startswith("%Vd("):
            in_vb_block = "%VB" in s
        if in_vb_block and "%Cl(" in s:
            art_in_vb = True
    if art_in_vb:
        print("PASS: %Cl is inside a %VB viewport (correct Rockbox album art pattern).")
    else:
        print("FAIL: %Cl not found inside a %VB viewport.")
        issues.append("%Cl not inside %VB viewport")

    # Summary
    print("\n=== SUMMARY ===")
    if issues:
        print(f"ISSUES FOUND ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print("ALL CHECKS PASSED. WPS is structurally sound and should load correctly.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
