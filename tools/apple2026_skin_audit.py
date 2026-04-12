#!/usr/bin/env python3
"""Static Apple2026 skin/theme audit for source, runtime trees, and zip artifacts."""

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
DEFAULT_PACKAGE_ROOT = ROOT / "build-sim" / "simdisk" / ".rockbox"
ASSET_DIR = ROOT / "wps" / "Apple2026"
WPSLIST = ROOT / "wps" / "WPSLIST"
APPLE2026_VERSION = "Update3"
APPLE2026_VERSION_FILE = ".apple2026_version"
SKINS = [
    ROOT / "wps" / "Apple2026.sbs",
    ROOT / "wps" / "Apple2026.wps",
]
VIEWPORT_RE = re.compile(r"%(V[li])\(([^)]*)\)")
PRELOAD_RE = re.compile(r"%xl\([^,]+,([^,]+\.bmp)")
LABEL_RE = re.compile(r"%V[li]\(([^,]+),")
ALBUMART_LOAD_RE = re.compile(r"%Cl\(")
THEME_BLOCK_RE = re.compile(r"<theme>(.*?)</theme>", re.S)
MAIN_BLOCK_RE = re.compile(r"<main>(.*?)</main>", re.S)

REQUIRED_THEME_SETTINGS = {
    "dynamic colors": "off",
    "backlight on button hold": "normal",
    "disable main menu scrolling": "on",
    "list separator height": "1",
    "qs top": "brightness",
    "qs left": "shuffle",
    "qs right": "repeat",
    "qs bottom": "sleeptimer duration",
}

REQUIRED_SOURCE_FILES = [
    "fonts/28-SFProDisplay-Bold.fnt",
    "fonts/16-SFProText-Semibold.fnt",
    "fonts/20-SFProText-Regular.fnt",
    "fonts/18-SFProText-Regular.fnt",
    "fonts/22-SFProText-Medium.fnt",
    "icons/Apple2026Icons.bmp",
    "wps/Apple2026.sbs",
    "wps/Apple2026.wps",
]

REQUIRED_RUNTIME_FILES = [
    APPLE2026_VERSION_FILE,
    "themes/Apple2026.cfg",
    "fonts/28-SFProDisplay-Bold.fnt",
    "fonts/16-SFProText-Semibold.fnt",
    "fonts/20-SFProText-Regular.fnt",
    "fonts/18-SFProText-Regular.fnt",
    "fonts/22-SFProText-Medium.fnt",
    "icons/Apple2026Icons.bmp",
    "wps/Apple2026.sbs",
    "wps/Apple2026.wps",
]

CLAIM_CONTRACTS = {
    "Apple2026.sbs": {
        "required": [
            ("%Vl(batterytext,-70,5,38,20,6)", "SBS battery text must use dense slot 6"),
            ("%Vl(batterytext_root,-70,5,38,20,6)", "root SBS battery text must use dense slot 6"),
            ("%?if(%bl, =, 100)<100%%|%bl%%>", "battery percentage must not contain a space before '%'"),
            ("%Vl(lock,-82,6,9,12,-)", "lock icon must live in the right-side battery cluster"),
            ("%Vl(sleeptimericon,-94,6,9,12,-)", "sleep icon must live in the right-side battery cluster"),
            ("%Vl(home_lock_notif_art,30,174,32,32,-)", "SBS lockscreen card must reuse the 32x32 album-art lane"),
            ("%?mp<%xd(Pa)|%xd(Pc)|%xd(Pb)|%xd(Pc)|%xd(Pc)>", "SBS mini-player must use the iPod-style play/pause mapping"),
            ("%?mp<|%xd(Oa)|%xd(Ob)|%xd(Oa)|%xd(Oa)>", "SBS lock notification must use the iPod-style play/pause mapping"),
        ],
        "forbidden": [
            ("%Vl(batterytext,-70,5,38,20,3)", "old SBS battery slot 3 layout must not ship"),
            ("%Vl(batterytext_root,-70,5,38,20,3)", "old root SBS battery slot 3 layout must not ship"),
            ("%bl %%", "old battery percentage formatting with a space must not ship"),
            ("%Vl(lock,24,6,9,12,-)", "old left-side lock icon layout must not ship"),
            ("%Vl(sleeptimericon,42,6,9,12,-)", "old left-side sleep icon layout must not ship"),
            ("%xl(Q,LockBatWarn.bmp,0,0)", "dead SBS low-battery preload must not ship"),
            ("%Vl(home_lock_notif_art,24,168,44,44,-)", "old SBS placeholder lockscreen art lane must not ship"),
            ("%?mp<%xd(Pa)|%xd(Pb)|%xd(Pc)|%xd(Pb)|%xd(Pb)>", "old Apple-style SBS mini-player mapping must not ship"),
            ("%?mp<|%xd(Ob)|%xd(Oa)|%xd(Ob)|%xd(Ob)>", "old Apple-style SBS lock notification mapping must not ship"),
        ],
    },
    "Apple2026.wps": {
        "required": [
            ("%?if(%bl, =, 100)<100%%|%bl%%>", "WPS battery percentage must not contain a space before '%'"),
            ("%?mm<|%xd(Ra)|%xd(X)|%xd(Y)|%xd(Z)>", "repeat display must show one clear icon per mode"),
            ("%x(M,speaker_mute.bmp,39,5)", "mute icon must align with the volume rail"),
            ("%Vl(lock_notif_art,0,0,0,0,-)", "WPS lockscreen card must stay text-only under the single-%Cl limit"),
            ("%Vl(lock_notif_title,30,168,238,20,9)", "WPS lockscreen title must reclaim the removed art lane"),
            ("%Vl(lock_notif_artist,30,190,238,18,3)", "WPS lockscreen artist must reclaim the removed art lane"),
            ("%?mh<|%?mp<|%xd(Pc)|%xd(Pb)|%xd(Pd)|%xd(Pd)|>>", "WPS status icon must use the iPod-style play/pause mapping"),
            ("%?mp<|%xd(Oa)|%xd(Ob)|%xd(Oa)|%xd(Oa)>", "WPS lock notification must use the iPod-style play/pause mapping"),
        ],
        "forbidden": [
            ("%bl %%", "old WPS battery percentage formatting with a space must not ship"),
            ("%?mm<|%xd(Ra)|%xd(Ra)%xd(X)|%xd(Ra)%xd(Y)|%xd(Ra)%xd(Z)>", "layered repeat icons must not ship"),
            ("%?if(%ps, =, s)<%xd(S)|>", "legacy extra shuffle overlay must not ship"),
            ("%xl(S,shuffle.bmp,42,0)", "dead WPS shuffle preload must not ship"),
            ("%xl(Q,LockBatWarn.bmp,0,0)", "dead WPS low-battery preload must not ship"),
            ("%Vl(lock_notif_art,24,168,44,44,-)", "old WPS placeholder lockscreen art lane must not ship"),
            ("%x(M,speaker_mute.bmp,39,8)", "old mute icon y=8 alignment must not ship"),
            ("%x(speaker_mute,speaker_mute.bmp,39,8)", "old named mute icon y=8 alignment must not ship"),
            ("%?mh<|%?mp<|%xd(Pb)|%xd(Pc)|%xd(Pd)|%xd(Pd)|>>", "old Apple-style WPS status mapping must not ship"),
            ("%?mp<|%xd(Ob)|%xd(Oa)|%xd(Ob)|%xd(Ob)>", "old Apple-style WPS lock notification mapping must not ship"),
        ],
    },
}


def sha1_bytes(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def sha1(path: Path) -> str:
    return sha1_bytes(path.read_bytes())


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


def parse_cfg_settings(text: str) -> dict[str, str]:
    settings: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        settings[key.strip()] = value.strip()
    return settings


def audit_theme_settings(label: str, settings: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for key, expected in REQUIRED_THEME_SETTINGS.items():
        actual = settings.get(key)
        if actual != expected:
            errors.append(
                f"{label}: expected '{key}: {expected}', found '{actual or '<missing>'}'"
            )
    return errors


def extract_apple2026_main_block(text: str) -> str | None:
    for block in THEME_BLOCK_RE.findall(text):
        if re.search(r"^\s*Name:\s*Apple2026\s*$", block, re.M):
            match = MAIN_BLOCK_RE.search(block)
            if match:
                return match.group(1)
    return None


def audit_source_contract() -> list[str]:
    errors: list[str] = []

    if not WPSLIST.exists():
        return [f"{WPSLIST}: missing Apple2026 theme source list"]

    wpslist_text = WPSLIST.read_text(encoding="utf-8", errors="replace")
    main_block = extract_apple2026_main_block(wpslist_text)
    if main_block is None:
        errors.append(f"{WPSLIST.name}: missing Apple2026 <main> block")
    else:
        errors.extend(
            audit_theme_settings("WPSLIST Apple2026 <main>", parse_cfg_settings(main_block))
        )

    for rel_path in REQUIRED_SOURCE_FILES:
        path = ROOT / rel_path
        if not path.exists():
            errors.append(f"{rel_path}: missing required Apple2026 source asset")

    return errors


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


def audit_runtime_root(package_root: Path) -> list[str]:
    errors: list[str] = []
    if not package_root.exists():
        return [f"{package_root}: package root missing"]

    for rel_path in REQUIRED_RUNTIME_FILES:
        path = package_root / rel_path
        if not path.exists():
            errors.append(f"{package_root}: missing required runtime file {rel_path}")

    for skin in SKINS:
        runtime = package_root / "wps" / skin.name
        if runtime.exists() and sha1(skin) != sha1(runtime):
            errors.append(f"{package_root}: runtime {skin.name} differs from repo source")

    theme_cfg = package_root / "themes" / "Apple2026.cfg"
    if theme_cfg.exists():
        errors.extend(
            audit_theme_settings(
                f"{package_root}/themes/Apple2026.cfg",
                parse_cfg_settings(theme_cfg.read_text(encoding="utf-8", errors="replace")),
            )
        )

    version_file = package_root / APPLE2026_VERSION_FILE
    if version_file.exists():
        version = version_file.read_text(encoding="utf-8", errors="replace").strip()
        if version != APPLE2026_VERSION:
            errors.append(
                f"{package_root}: expected {APPLE2026_VERSION_FILE}='{APPLE2026_VERSION}', found '{version}'"
            )

    return errors


def audit_zip(zip_path: Path) -> list[str]:
    errors: list[str] = []
    if not zip_path.exists():
        return [f"{zip_path}: zip artifact missing"]

    with zipfile.ZipFile(zip_path) as zf:
        members = set(zf.namelist())

        for skin in SKINS:
            member = f".rockbox/wps/{skin.name}"
            if member not in members:
                errors.append(f"{zip_path}: missing zip member {member}")
                continue
            if sha1_bytes(zf.read(member)) != sha1(skin):
                errors.append(f"{zip_path}: zip member {member} differs from repo source")

        for rel_path in REQUIRED_RUNTIME_FILES:
            member = f".rockbox/{rel_path}"
            if member not in members:
                errors.append(f"{zip_path}: missing zip member {member}")

        theme_member = ".rockbox/themes/Apple2026.cfg"
        if theme_member in members:
            errors.extend(
                audit_theme_settings(
                    f"{zip_path}:{theme_member}",
                    parse_cfg_settings(zf.read(theme_member).decode("utf-8", errors="replace")),
                )
            )

        version_member = f".rockbox/{APPLE2026_VERSION_FILE}"
        if version_member in members:
            version = zf.read(version_member).decode("utf-8", errors="replace").strip()
            if version != APPLE2026_VERSION:
                errors.append(
                    f"{zip_path}: expected {version_member}='{APPLE2026_VERSION}', found '{version}'"
                )

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
    parser.add_argument(
        "--source-only",
        action="store_true",
        help="Audit only source contracts; do not inspect a runtime tree",
    )
    args = parser.parse_args()

    package_roots = [Path(p) for p in args.package_root]
    zip_artifacts = [Path(p) for p in args.zip_artifact]

    if args.source_only and package_roots:
        parser.error("--source-only cannot be combined with --package-root")

    if not args.source_only and not package_roots:
        package_roots = [DEFAULT_PACKAGE_ROOT]

    errors: list[str] = []
    errors.extend(audit_source_contract())

    for skin in SKINS:
        errors.extend(audit_skin(skin))

    for package_root in package_roots:
        errors.extend(audit_runtime_root(package_root))

    for zip_artifact in zip_artifacts:
        errors.extend(audit_zip(zip_artifact))

    if errors:
        print("FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
