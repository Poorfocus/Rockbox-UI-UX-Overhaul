#!/usr/bin/env python3
"""Static Apple2026 skin audit for parser-fatal regressions and package drift."""

from __future__ import annotations

import argparse
import hashlib
import re
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path

LCD_W = 320
LCD_H = 240
WPS_MAX_TOKENS = 1150
ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "wps" / "Apple2026"
SKINS = [
    ROOT / "wps" / "Apple2026.sbs",
    ROOT / "wps" / "Apple2026.wps",
]
VIEWPORT_RE = re.compile(r"%(V[li])\(([^)]*)\)")
PRELOAD_RE = re.compile(r"%xl\([^,]+,([^,]+\.bmp)")
LABEL_RE = re.compile(r"%V[li]\(([^,]+),")
ALBUMART_LOAD_RE = re.compile(r"%Cl\(")
CLAIM_CONTRACTS = {
    "Apple2026.sbs": {
        "required": [
            ("%Vl(batterytext,-70,5,38,20,6)", "SBS battery text must use dense slot 6"),
            ("%Vl(batterytext_root,-70,5,38,20,6)", "root SBS battery text must use dense slot 6"),
            ("%?if(%bl, =, 100)<100%%|%bl%%>", "battery percentage must not contain a space before '%'"),
            ("%Vl(lock,-82,6,9,12,-)", "lock icon must live in the right-side battery cluster"),
            ("%Vl(sleeptimericon,-94,6,9,12,-)", "sleep icon must live in the right-side battery cluster"),
            ("%?mp<%xd(Pa)|%xd(Pc)|%xd(Pb)|%xd(Pc)|%xd(Pc)>", "SBS mini-player must use the iPod-style play/pause mapping"),
            ("%?mp<|%xd(Oa)|%xd(Ob)|%xd(Oa)|%xd(Oa)>", "SBS lock notification must use the iPod-style play/pause mapping"),
        ],
        "forbidden": [
            ("%Vl(batterytext,-70,5,38,20,3)", "old SBS battery slot 3 layout must not ship"),
            ("%Vl(batterytext_root,-70,5,38,20,3)", "old root SBS battery slot 3 layout must not ship"),
            ("%bl %%", "old battery percentage formatting with a space must not ship"),
            ("%Vl(lock,24,6,9,12,-)", "old left-side lock icon layout must not ship"),
            ("%Vl(sleeptimericon,42,6,9,12,-)", "old left-side sleep icon layout must not ship"),
            ("%?mp<%xd(Pa)|%xd(Pb)|%xd(Pc)|%xd(Pb)|%xd(Pb)>", "old Apple-style SBS mini-player mapping must not ship"),
            ("%?mp<|%xd(Ob)|%xd(Oa)|%xd(Ob)|%xd(Ob)>", "old Apple-style SBS lock notification mapping must not ship"),
        ],
    },
    "Apple2026.wps": {
        "required": [
            ("%?if(%bl, =, 100)<100%%|%bl%%>", "WPS battery percentage must not contain a space before '%'"),
            ("%?mm<|%xd(Ra)|%xd(X)|%xd(Y)|%xd(Z)>", "repeat display must show one clear icon per mode"),
            ("%x(M,speaker_mute.bmp,39,5)", "mute icon must align with the volume rail"),
            ("%?mh<|%?mp<|%xd(Pc)|%xd(Pb)|%xd(Pd)|%xd(Pd)|>>", "WPS status icon must use the iPod-style play/pause mapping"),
            ("%?mp<|%xd(Oa)|%xd(Ob)|%xd(Oa)|%xd(Oa)>", "WPS lock notification must use the iPod-style play/pause mapping"),
        ],
        "forbidden": [
            ("%bl %%", "old WPS battery percentage formatting with a space must not ship"),
            ("%?mm<|%xd(Ra)|%xd(Ra)%xd(X)|%xd(Ra)%xd(Y)|%xd(Ra)%xd(Z)>", "layered repeat icons must not ship"),
            ("%?if(%ps, =, s)<%xd(S)|>", "legacy extra shuffle overlay must not ship"),
            ("%x(M,speaker_mute.bmp,39,8)", "old mute icon y=8 alignment must not ship"),
            ("%x(speaker_mute,speaker_mute.bmp,39,8)", "old named mute icon y=8 alignment must not ship"),
            ("%?mh<|%?mp<|%xd(Pb)|%xd(Pc)|%xd(Pd)|%xd(Pd)|>>", "old Apple-style WPS status mapping must not ship"),
            ("%?mp<|%xd(Ob)|%xd(Oa)|%xd(Ob)|%xd(Ob)>", "old Apple-style WPS lock notification mapping must not ship"),
        ],
    },
}


def sha1(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def bmp_decoded_size(path: Path) -> tuple[int, int, int]:
    header = path.read_bytes()[:54]
    if header[:2] != b"BM":
        raise ValueError(f"{path} is not a BMP")
    width = struct.unpack_from("<i", header, 18)[0]
    height = abs(struct.unpack_from("<i", header, 22)[0])
    return width, height, width * height * 2


def percent_token_count(text: str) -> int:
    return len(re.findall(r"%(?:\?|[A-Za-z][A-Za-z]?|.)", text))


def resolved_rect(parts: list[str]) -> tuple[int, int, int, int]:
    x = 0 if parts[0] == "-" else int(parts[0])
    y = 0 if parts[1] == "-" else int(parts[1])
    if x < 0:
        x += LCD_W
    if y < 0:
        y += LCD_H

    if parts[2] == "-":
        width = LCD_W - x
    else:
        width = int(parts[2])
        if width < 0:
            width = (width + LCD_W) - x

    if parts[3] == "-":
        height = LCD_H - y
    else:
        height = int(parts[3])
        if height < 0:
            height = (height + LCD_H) - y

    return x, y, width, height


def audit_skin(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    contract = CLAIM_CONTRACTS.get(path.name, {})

    labels = [label for label in LABEL_RE.findall(text) if label != "-"]
    for label, count in Counter(labels).items():
        if count > 1:
            errors.append(f"{path.name}: duplicate viewport label '{label}' x{count}")

    albumart_loads = len(ALBUMART_LOAD_RE.findall(text))
    if albumart_loads > 1:
        errors.append(
            f"{path.name}: multiple %Cl album-art loads ({albumart_loads}) "
            "would override the active geometry"
        )

    token_count = percent_token_count(text)
    if token_count >= WPS_MAX_TOKENS:
        errors.append(
            f"{path.name}: token count {token_count} exceeds WPS_MAX_TOKENS {WPS_MAX_TOKENS}"
        )

    for needle, reason in contract.get("required", []):
        if needle not in text:
            errors.append(f"{path.name}: missing claim contract '{needle}' ({reason})")
    for needle, reason in contract.get("forbidden", []):
        if needle in text:
            errors.append(f"{path.name}: found forbidden legacy pattern '{needle}' ({reason})")

    for lineno, line in enumerate(text.splitlines(), 1):
        match = VIEWPORT_RE.search(line)
        if not match:
            continue
        kind = match.group(1)
        args = [part.strip() for part in match.group(2).split(",")]
        coords = args[1:5]
        if len(coords) < 4:
            continue
        x, y, width, height = resolved_rect(coords)
        if (
            x < 0
            or y < 0
            or x >= LCD_W
            or y >= LCD_H
            or width < 0
            or height < 0
            or x + width > LCD_W
            or y + height > LCD_H
        ):
            errors.append(
                f"{path.name}:{lineno}: {kind} out of bounds -> x={x} y={y} w={width} h={height}"
            )

    total = 0
    for asset_name in PRELOAD_RE.findall(text):
        asset_path = ASSET_DIR / asset_name
        if not asset_path.exists():
            errors.append(f"{path.name}: missing preload asset '{asset_name}'")
            continue
        _, _, decoded = bmp_decoded_size(asset_path)
        total += decoded

    print(f"{path.name}: percent-tokens={token_count} preload-decoded16={total}")
    return errors


def audit_package(source: Path, package_root: Path) -> list[str]:
    errors: list[str] = []
    if not package_root.exists():
        return errors

    runtime = package_root / "wps" / source.name
    if not runtime.exists():
        errors.append(f"{package_root}: missing runtime copy for {source.name}")
        return errors

    if sha1(source) != sha1(runtime):
        errors.append(f"{package_root}: runtime {source.name} differs from repo source")

    return errors


def audit_zip(source: Path, zip_path: Path) -> list[str]:
    errors: list[str] = []
    if not zip_path.exists():
        errors.append(f"{zip_path}: zip artifact missing")
        return errors

    member = f".rockbox/wps/{source.name}"
    with zipfile.ZipFile(zip_path) as zf:
        if member not in zf.namelist():
            errors.append(f"{zip_path}: missing zip member {member}")
            return errors
        if hashlib.sha1(zf.read(member)).hexdigest() != sha1(source):
            errors.append(f"{zip_path}: zip member {member} differs from repo source")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--package-root",
        action="append",
        default=[],
        help="Optional .rockbox root to compare against repo sources",
    )
    parser.add_argument(
        "--zip-artifact",
        action="append",
        default=[],
        help="Optional rockbox.zip artifact to compare against repo sources",
    )
    args = parser.parse_args()

    package_roots = [Path(p) for p in args.package_root]
    zip_artifacts = [Path(p) for p in args.zip_artifact]
    if not package_roots:
        package_roots = [ROOT / "build-sim" / "simdisk" / ".rockbox"]

    errors: list[str] = []
    for skin in SKINS:
        errors.extend(audit_skin(skin))
        for package_root in package_roots:
            errors.extend(audit_package(skin, package_root))
        for zip_artifact in zip_artifacts:
            errors.extend(audit_zip(skin, zip_artifact))

    if errors:
        print("FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
