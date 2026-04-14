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

from apple2026_palette import GROUPED_FILL, PROGRESS_TRACK, SHELL_BG, SHELL_BG_HEX_LOWER, TEXT_SECONDARY, TEXT_TERTIARY

LCD_W = 320
LCD_H = 240
WPS_MAX_TOKENS = 1150
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_ROOT = ROOT / "build-sim" / "simdisk" / ".rockbox"
ASSET_DIR = ROOT / "wps" / "Apple2026"
WPSLIST = ROOT / "wps" / "WPSLIST"
STATUSBAR_SKINNED = ROOT / "apps" / "gui" / "statusbar-skinned.c"
ART_FRAME_TOOL = ROOT / "tools" / "apple2026_wps_art_frame.py"
APPLE2026_VERSION = "Update3"
APPLE2026_VERSION_FILE = ".apple2026_version"
TRANS_KEY = (255, 0, 255)
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
    "foreground color": "000000",
    "background color": SHELL_BG_HEX_LOWER,
    "dynamic colors": "off",
    "backlight on button hold": "normal",
    "disable main menu scrolling": "on",
    "list separator height": "1",
    "qs top": "brightness",
    "qs left": "shuffle",
    "qs right": "repeat",
    "qs bottom": "brightness",
}

REQUIRED_SOURCE_FILES = [
    "fonts/28-SFProDisplay-Bold.fnt",
    "fonts/13-SFCompactText-Regular.fnt",
    "fonts/16-SFProText-Semibold.fnt",
    "fonts/20-SFProText-Regular.fnt",
    "fonts/18-SFProText-Regular.fnt",
    "fonts/22-SFProText-Medium.fnt",
    "icons/Apple2026Icons.bmp",
    "wps/Apple2026.sbs",
    "wps/Apple2026.wps",
    "wps/Apple2026/albumPlaceholder.bmp",
    "wps/Apple2026/art_mask.bmp",
    "wps/Apple2026/miniplayer_bg.bmp",
    "wps/Apple2026/playerStatusLarge.bmp",
    "wps/Apple2026/repeatLarge.bmp",
    "wps/Apple2026/wpsBackdrop.bmp",
    "wps/Apple2026/wpsArtCorners.bmp",
    "wps/Apple2026/qs_wheel.bmp",
    "wps/Apple2026/qs_slider_fill.bmp",
    "wps/Apple2026/qs_slider_track.bmp",
    "wps/Apple2026/qs_bar_fill.bmp",
    "wps/Apple2026/qs_bar_track.bmp",
    "wps/Apple2026/qs_sun_max.bmp",
    "wps/Apple2026/qs_sun_min.bmp",
    "wps/Apple2026/shuffle.bmp",
    "wps/Apple2026/shuffleLarge.bmp",
]

REQUIRED_RUNTIME_FILES = [
    APPLE2026_VERSION_FILE,
    "themes/Apple2026.cfg",
    "fonts/28-SFProDisplay-Bold.fnt",
    "fonts/13-SFCompactText-Regular.fnt",
    "fonts/16-SFProText-Semibold.fnt",
    "fonts/20-SFProText-Regular.fnt",
    "fonts/18-SFProText-Regular.fnt",
    "fonts/22-SFProText-Medium.fnt",
    "icons/Apple2026Icons.bmp",
    "wps/Apple2026.sbs",
    "wps/Apple2026.wps",
    "wps/Apple2026/albumPlaceholder.bmp",
    "wps/Apple2026/art_mask.bmp",
    "wps/Apple2026/miniplayer_bg.bmp",
    "wps/Apple2026/playerStatusLarge.bmp",
    "wps/Apple2026/repeatLarge.bmp",
    "wps/Apple2026/wpsBackdrop.bmp",
    "wps/Apple2026/wpsArtCorners.bmp",
    "wps/Apple2026/qs_wheel.bmp",
    "wps/Apple2026/qs_slider_fill.bmp",
    "wps/Apple2026/qs_slider_track.bmp",
    "wps/Apple2026/qs_bar_fill.bmp",
    "wps/Apple2026/qs_bar_track.bmp",
    "wps/Apple2026/qs_sun_max.bmp",
    "wps/Apple2026/qs_sun_min.bmp",
    "wps/Apple2026/shuffle.bmp",
    "wps/Apple2026/shuffleLarge.bmp",
]

REQUIRED_BMP_DIMENSIONS = {
    "icons/Apple2026Icons.bmp": (30, 1020),
    "wps/Apple2026/albumPlaceholder.bmp": (150, 150),
    "wps/Apple2026/art_mask.bmp": (32, 32),
    "wps/Apple2026/miniplayer_bg.bmp": (320, 50),
    "wps/Apple2026/qs_wheel.bmp": (92, 92),
    "wps/Apple2026/qs_slider_fill.bmp": (20, 132),
    "wps/Apple2026/qs_slider_track.bmp": (20, 132),
    "wps/Apple2026/qs_bar_fill.bmp": (176, 6),
    "wps/Apple2026/qs_bar_track.bmp": (176, 6),
    "wps/Apple2026/qs_sun_max.bmp": (14, 14),
    "wps/Apple2026/qs_sun_min.bmp": (14, 14),
    "wps/Apple2026/playerStatusLarge.bmp": (20, 80),
    "wps/Apple2026/repeatLarge.bmp": (20, 15),
    "wps/Apple2026/shuffle.bmp": (16, 11),
    "wps/Apple2026/shuffleLarge.bmp": (20, 15),
    "wps/Apple2026/wpsArtCorners.bmp": (150, 150),
    "wps/Apple2026/wpsBackdrop.bmp": (320, 240),
}

CLAIM_CONTRACTS = {
    "Apple2026.sbs": {
        "required": [
            ("%Vl(batterytext,-70,5,38,20,6)", "SBS battery text must use dense slot 6"),
            ("%Vl(batterytext_root,-70,5,38,20,6)", "root SBS battery text must use dense slot 6"),
            ("%?if(%bl, =, 100)<100%%|%bl%%>", "battery percentage must not contain a space before '%'"),
            ("%Vl(lock,-82,6,9,12,-)", "lock icon must live in the right-side battery cluster"),
            ("%Vl(sleeptimertext,-100,5,58,20,6)", "SBS sleep text must live in the right-side battery cluster"),
            ("%?if(%cs, =, 10)<%VI(qs_blank)|", "quickscreen must suppress underlying content viewport ownership"),
            ("%Vi(qs_blank,0,0,1,1,5)", "quickscreen must define a dedicated blank info viewport"),
            ("%V(80,8,160,18,8)", "quickscreen header must use the smaller centered title block"),
            ("%V(114,84,92,92,-)", "quickscreen wheel must be centered"),
            ("%xd(Q)", "quickscreen must render the Apple2026 quick wheel asset"),
            ("%xd(X)", "quickscreen must render the brightness-up sun symbol"),
            ("%xd(R)", "quickscreen must render the brightness-down sun symbol"),
            ("%St(0,0,176,6,image,V,backdrop,W,setting,brightness)", "quickscreen must render the wider rounded brightness bar"),
            ("%pv(0,0,176,6,image,V,backdrop,W)", "quickscreen must render the wider rounded volume bar"),
            ("%xl(T,playerStatusLarge.bmp,0,0,4)", "SBS mini-player must preload the larger transport strip"),
            ("%?if(%cs, =, 10)<|%?mp<|%xd(Z)||%xd(Z)|%xd(Z)>>", "SBS mini-player body must be hidden in stop/pause and shown only for active playback"),
            ("%V(280,203,20,20,-)", "SBS mini-player transport must use the larger 20x20 slot"),
            ("%?if(%cs, =, 10)<|%?mp<|%?mv(1.2)<|%xd(Tc)>|%?mv(1.2)<|%xd(Tb)>|%?mv(1.2)<|%xd(Tc)>|%?mv(1.2)<|%xd(Tc)>>>", "SBS mini-player transport must show play for play and pause-bars for pause"),
            ("%Vl(mp_volume_bg,60,203,196,20,-)", "SBS mini-player volume overlay must be a transient labeled viewport"),
            ("%Vl(mp_volume_clip,60,203,196,20,-)", "SBS mini-player clipping overlay must be a transient labeled viewport"),
        ],
        "forbidden": [
            ("FBFBF9", "mini-player shell/body split white must not ship"),
            ("%dr(0,0,320,50,FFFFFF,FFFFFF)", "SBS must not hard-clear the full mini-player strip in stop/pause states"),
            ("%dr(0,0,320,50,FAFAF8,FAFAF8)", "SBS must not hard-clear the full mini-player strip in stop/pause states"),
            ("%V(60,203,196,20,-)", "SBS mini-player volume overlay must not be an always-rendered viewport"),
            ("%Vl(home_lock_notif_art,30,174,32,32,-)", "lockscreen has been disabled, lock UI must not ship"),
            ("%?mp<|%xd(Oa)|%xd(Ob)|%xd(Oa)|%xd(Oa)>", "lock notification lock UI must not ship"),
            ("%Vl(batterytext,-70,5,38,20,3)", "old SBS battery slot 3 layout must not ship"),
            ("%Vl(batterytext_root,-70,5,38,20,3)", "old root SBS battery slot 3 layout must not ship"),
            ("%bl %%", "old battery percentage formatting with a space must not ship"),
            ("%Vl(lock,24,6,9,12,-)", "old left-side lock icon layout must not ship"),
            ("%Vl(sleeptimericon,-94,6,9,12,-)", "old tiny sleep icon layout must not ship"),
            ("%Vl(sleeptimericon,42,6,9,12,-)", "old left-side sleep icon layout must not ship"),
            ("%xl(Q,LockBatWarn.bmp,0,0)", "dead SBS low-battery preload must not ship"),
            ("%Vl(home_lock_notif_art,24,168,44,44,-)", "old SBS placeholder lockscreen art lane must not ship"),
            ("%?mp<%xd(Pa)|%xd(Pb)|%xd(Pc)|%xd(Pb)|%xd(Pb)>", "old Apple-style SBS mini-player mapping must not ship"),
            ("%V(280,204,16,18,-)", "old small SBS mini-player transport slot must not ship"),
            ("%?if(%cs, =, 10)<|%?mp<|%?mv(1.2)<|%xd(Pc)>||%?mv(1.2)<|%xd(Pc)>|%?mv(1.2)<|%xd(Pc)>>>", "old SBS play-only transport mapping must not ship"),
            ("%?mp<|%xd(Ob)|%xd(Oa)|%xd(Ob)|%xd(Ob)>", "old Apple-style SBS lock notification mapping must not ship"),
            ("%acSelect", "quickscreen should no longer show the old center Select label"),
            ("%V(148,72,80,16,8)", "old middle-stack quickscreen brightness label must not ship"),
            ("%V(148,122,80,16,8)", "old middle-stack quickscreen volume label must not ship"),
            ("%V(148,174,80,16,8)", "old middle-stack quickscreen shuffle label must not ship"),
            ("%V(148,214,80,16,8)", "old middle-stack quickscreen repeat label must not ship"),
            ("%V(164,102,136,4,-)", "old horizontal quickscreen brightness rail must not ship"),
            ("%V(164,148,136,4,-)", "old horizontal quickscreen volume rail must not ship"),
            ("%V(236,56,1,152,-)", "old vertical quickscreen divider must not ship"),
            ("%St(0,0,20,132,image,T,backdrop,U,setting,brightness)", "old vertical brightness pill must not ship"),
            ("%pv(0,0,20,132,image,T,backdrop,U)", "old vertical volume pill must not ship"),
            ("%V(70,204,92,14,8)", "old bottom brightness label block must not ship"),
            ("%ac%Qb", "bottom brightness numeric readout must not ship in the current Apple2026 pass"),
        ],
    },
    "Apple2026.wps": {
        "required": [
            ("%?if(%bl, =, 100)<100%%|%bl%%>", "WPS battery percentage must not contain a space before '%'"),
            ("%Fl(6,13-SFCompactText-Regular.fnt)", "WPS must load the compact status-label font"),
            ("%xl(N,playerStatusLarge.bmp,0,0,4)", "WPS must preload the dedicated large transport strip"),
            ("%xl(O,repeatLarge.bmp,0,0)", "WPS must preload the dedicated large repeat glyph"),
            ("%xl(Q,shuffleLarge.bmp,0,0)", "WPS must preload the dedicated large shuffle glyph"),
            ("%Vl(title_line,18,-79,258,20,9)", "WPS title lane must reserve the right-side safe area"),
            ("%Vl(artist_line,18,-60,258,18,3)", "WPS artist/album lane must reserve the right-side safe area"),
            ("%Vl(shuffle_state,281,103,20,15,-)", "WPS must define the larger upper-right shuffle slot"),
            ("%?or(%if(%ps, =, s),%if(%mm, =, 3))<%xd(Q)>", "WPS shuffle lane must explicitly cover shuffle and repeat-shuffle states"),
            ("%Vl(repeat_icon_state,281,124,20,15,-)", "WPS must define the larger repeat icon slot"),
            ("%?mm<|%xd(O)|%xd(O)|%xd(O)|%xd(O)>", "WPS repeat icon lane must stay populated for all repeat-enabled modes"),
            ("%Vl(repeat_label_state,264,140,54,15,6)", "WPS must define the compact repeat-label lane under the repeat icon"),
            ("%ac%?mm<||All|One|All|A-B>", "WPS repeat label lane must use short labels and treat repeat-shuffle as All"),
            ("%Vl(player_status_lane,280,178,20,20,-)", "WPS player status must use the larger bottom-right lane"),
            ("%Vl(lossless_ind,127,-12,66,11,-)", "WPS lossless badge must live in the bottom pad"),
            ("%x(M,speaker_mute.bmp,35,1)", "mute icon must match the loud speaker size and sit flush with the volume rail"),
            ("%?mh<|%?mp<|%xd(Nc)|%xd(Nb)|%xd(Nd)|%xd(Nd)|>>", "WPS status icon must use the larger iPod-style play/pause mapping"),
        ],
        "forbidden": [
            ("%xl(P,playerStatus.bmp,0,0,4)", "WPS must not use the old shared small transport strip"),
            ("%xl(R,repeat.bmp,42,3)", "WPS must not preload the old small repeat glyph"),
            ("%xl(S,shuffle.bmp,0,3)", "WPS must not preload the old small shuffle glyph"),
            ("%xl(D,speaker_too_loud.bmp,266,1)", "WPS volume lane must not preload the deprecated red warning stripe"),
            ("%?if(%pv, >, 0)<%xd(D)>", "WPS volume lane must not overlay the deprecated red warning stripe"),
            ("%Vl(lock_notif_art,0,0,0,0,-)", "lockscreen disabled: WPS lockscreen card must not ship"),
            ("%Vl(lock_notif_title,30,168,238,20,9)", "lockscreen disabled: WPS lockscreen title must not ship"),
            ("%Vl(lock_notif_artist,30,190,238,18,3)", "lockscreen disabled: WPS lockscreen artist must not ship"),
            ("%?mp<|%xd(Oa)|%xd(Ob)|%xd(Oa)|%xd(Oa)>", "lockscreen disabled: WPS lock notification must not ship"),
            ("%bl %%", "old WPS battery percentage formatting with a space must not ship"),
            ("%?mm<|%xd(Ra)|%xd(Ra)%xd(X)|%xd(Ra)%xd(Y)|%xd(Ra)%xd(Z)>", "layered repeat icons must not ship"),
            ("%?mm<|%xd(Ra)|%xd(X)|%xd(Y)|%xd(Z)>", "ambiguous icon-only repeat labels must not ship"),
            ("%?mm<|%xd(Ra) ALL|%xd(Ra) ONE|%xd(Ra) SHU|%xd(Ra) A-B>", "old overlapping repeat-label lane must not ship"),
            ("%?ps<%xd(S)|%?mm<|||%xd(S)|>>", "old split shuffle fallback lane must not ship"),
            ("%?mm<|All%xd(R)|One%xd(R)||A-B%xd(R)>", "old combined repeat icon/text lane must not ship"),
            ("%?ps<SHUFFLE|>", "text-only shuffle lane must not ship"),
            ("%V(3,5,16,18,-)", "top-left WPS status icon layout must not ship"),
            ("%xl(Q,LockBatWarn.bmp,0,0)", "dead WPS low-battery preload must not ship"),
            ("%Vl(lock_notif_art,24,168,44,44,-)", "old WPS placeholder lockscreen art lane must not ship"),
            ("%x(M,speaker_mute.bmp,46,5)", "undersized mute icon layout must not ship"),
            ("%x(M,speaker_mute.bmp,39,5)", "misaligned mute icon x=39 must not ship"),
            ("%x(M,speaker_mute.bmp,39,8)", "old mute icon y=8 alignment must not ship"),
            ("%x(speaker_mute,speaker_mute.bmp,39,8)", "old named mute icon y=8 alignment must not ship"),
            ("%?mh<|%?mp<|%xd(Pc)|%xd(Pb)|%xd(Pd)|%xd(Pd)|>>", "WPS must not rely on the old small status strip mapping"),
            ("%?mh<|%?mp<|%xd(Pb)|%xd(Pc)|%xd(Pd)|%xd(Pd)|>>", "old Apple-style WPS status mapping must not ship"),
            ("%?mp<|%xd(Ob)|%xd(Oa)|%xd(Ob)|%xd(Ob)>", "old Apple-style WPS lock notification mapping must not ship"),
        ],
    },
}

ASSET_SAMPLE_EXPECTATIONS = {
    "wps/Apple2026/wpsBackdrop.bmp": {
        (0, 0): SHELL_BG,
        (160, 200): SHELL_BG,
    },
    "wps/Apple2026/miniplayer_bg.bmp": {
        (160, 25): SHELL_BG,
        (160, 4): SHELL_BG,
        (10, 4): SHELL_BG,
    },
    "wps/Apple2026/art_mask.bmp": {
        (0, 0): SHELL_BG,
    },
    "wps/Apple2026/albumPlaceholder.bmp": {
        (0, 0): SHELL_BG,
    },
    "wps/Apple2026/Wallpaper.bmp": {
        (0, 0): SHELL_BG,
    },
    "wps/Apple2026/usbBackdrop.bmp": {
        (0, 0): SHELL_BG,
    },
    "wps/Apple2026/qs_wheel.bmp": {
        (0, 0): SHELL_BG,
    },
    "wps/Apple2026/qs_slider_fill.bmp": {
        (0, 0): SHELL_BG,
        (10, 2): TEXT_SECONDARY,
    },
    "wps/Apple2026/qs_slider_track.bmp": {
        (0, 0): SHELL_BG,
        (10, 2): PROGRESS_TRACK,
    },
    "wps/Apple2026/qs_bar_fill.bmp": {
        (0, 0): SHELL_BG,
        (88, 3): TEXT_SECONDARY,
    },
    "wps/Apple2026/qs_bar_track.bmp": {
        (0, 0): SHELL_BG,
        (88, 3): PROGRESS_TRACK,
    },
    "wps/Apple2026/qs_sun_max.bmp": {
        (0, 0): SHELL_BG,
    },
    "wps/Apple2026/qs_sun_min.bmp": {
        (0, 0): SHELL_BG,
    },
    "wps/Apple2026/pb.bmp": {
        (0, 0): SHELL_BG,
        (5, 2): TEXT_TERTIARY,
    },
    "wps/Apple2026/pb_backdrop.bmp": {
        (0, 0): SHELL_BG,
        (5, 2): PROGRESS_TRACK,
    },
    "wps/Apple2026/vb.bmp": {
        (0, 0): SHELL_BG,
        (5, 2): TEXT_TERTIARY,
    },
    "wps/Apple2026/vb_backdrop.bmp": {
        (0, 0): SHELL_BG,
        (5, 2): PROGRESS_TRACK,
    },
    "wps/Apple2026/LockNotification.bmp": {
        (0, 0): SHELL_BG,
        (10, 10): GROUPED_FILL,
    },
    "icons/Apple2026Icons.bmp": {
        (15, 45): (255, 46, 86),
        (15, 315): (255, 45, 85),
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


def bmp_decoded_size_bytes(data: bytes, label: str) -> tuple[int, int, int]:
    header = data[:54]
    if header[:2] != b"BM":
        raise ValueError(f"{label} is not a BMP")
    width = struct.unpack_from("<i", header, 18)[0]
    height = abs(struct.unpack_from("<i", header, 22)[0])
    return width, height, width * height * 2


def bmp_rgb_at(path: Path, x: int, y: int) -> tuple[int, int, int]:
    data = path.read_bytes()
    return bmp_rgb_at_bytes(data, str(path), x, y)


def bmp_rgb_at_bytes(data: bytes, label: str, x: int, y: int) -> tuple[int, int, int]:
    if data[:2] != b"BM":
        raise ValueError(f"{label} is not a BMP")
    pixel_offset = struct.unpack_from("<I", data, 10)[0]
    width = struct.unpack_from("<i", data, 18)[0]
    height_raw = struct.unpack_from("<i", data, 22)[0]
    bpp = struct.unpack_from("<H", data, 28)[0]
    compression = struct.unpack_from("<I", data, 30)[0]

    if compression != 0 or bpp != 24:
        raise ValueError(f"{label}: unsupported BMP format for pixel audit (bpp={bpp}, compression={compression})")

    height = abs(height_raw)
    if x < 0 or y < 0 or x >= width or y >= height:
        raise ValueError(f"{label}: pixel ({x},{y}) out of bounds for {width}x{height}")

    row_stride = ((width * 3) + 3) & ~3
    row = (height - 1 - y) if height_raw > 0 else y
    offset = pixel_offset + row * row_stride + x * 3
    b, g, r = data[offset:offset + 3]
    return (r, g, b)


def audit_wps_hero_art_assets(read_pixel, label_prefix: str) -> list[str]:
    errors: list[str] = []

    trim_corner = read_pixel("wps/Apple2026/wpsArtCorners.bmp", 0, 0)
    if trim_corner == SHELL_BG:
        errors.append(
            f"{label_prefix}wps/Apple2026/wpsArtCorners.bmp: hero trim corner must not be flat shell-white fill"
        )
    if trim_corner == TRANS_KEY:
        errors.append(
            f"{label_prefix}wps/Apple2026/wpsArtCorners.bmp: hero trim corner must preserve backdrop/shadow pixels"
        )

    trim_cutout = read_pixel("wps/Apple2026/wpsArtCorners.bmp", 90, 12)
    if trim_cutout != TRANS_KEY:
        errors.append(
            f"{label_prefix}wps/Apple2026/wpsArtCorners.bmp: rounded interior must remain transparent via FF00FF"
        )

    backdrop_corner = read_pixel("wps/Apple2026/wpsBackdrop.bmp", 85, 8)
    if backdrop_corner == SHELL_BG:
        errors.append(
            f"{label_prefix}wps/Apple2026/wpsBackdrop.bmp: hero corner pocket must retain the curved-edge shadow"
        )

    backdrop_interior = read_pixel("wps/Apple2026/wpsBackdrop.bmp", 95, 15)
    if backdrop_interior != SHELL_BG:
        errors.append(
            f"{label_prefix}wps/Apple2026/wpsBackdrop.bmp: hero rounded interior must stay flat shell tone"
        )

    return errors


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

    for rel_path, expected in REQUIRED_BMP_DIMENSIONS.items():
        path = ROOT / rel_path
        if not path.exists():
            continue
        width, height, _ = bmp_decoded_size(path)
        if (width, height) != expected:
            errors.append(
                f"{rel_path}: expected {expected[0]}x{expected[1]}, found {width}x{height}"
            )

    if STATUSBAR_SKINNED.exists():
        statusbar_text = STATUSBAR_SKINNED.read_text(encoding="utf-8", errors="replace")
        refresh_call = re.search(
            r"skin_update\(CUSTOM_STATUSBAR,\s*screen,\s*(.*?)\);",
            statusbar_text,
            re.S,
        )
        if not refresh_call:
            errors.append("statusbar-skinned.c: missing CUSTOM_STATUSBAR steady-state update call")
        else:
            refresh_expr = refresh_call.group(1)
            for token in ("SKIN_REFRESH_NON_STATIC", "SKIN_REFRESH_STATIC", "SKIN_REFRESH_SCROLL"):
                if token not in refresh_expr:
                    errors.append(
                        f"statusbar-skinned.c: steady-state CUSTOM_STATUSBAR refresh must include {token}"
                    )

    if ART_FRAME_TOOL.exists():
        generator_text = ART_FRAME_TOOL.read_text(encoding="utf-8", errors="replace")
        if "MINIPLAYER_FILL     = BG_COLOR" not in generator_text:
            errors.append(
                "apple2026_wps_art_frame.py: mini-player fill must match BG_COLOR for same-tone shell/body"
            )

    for rel_path, expectations in ASSET_SAMPLE_EXPECTATIONS.items():
        path = ROOT / rel_path
        if not path.exists():
            continue
        for (x, y), expected in expectations.items():
            sample = bmp_rgb_at(path, x, y)
            if sample != expected:
                errors.append(
                    f"{rel_path}: expected sample ({x},{y}) {expected}, found {sample}"
                )

    errors.extend(
        audit_wps_hero_art_assets(
            lambda rel_path, x, y: bmp_rgb_at(ROOT / rel_path, x, y),
            "",
        )
    )

    return errors


def audit_skin(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    contract = CLAIM_CONTRACTS.get(path.name, {})

    if path.name == "Apple2026.sbs" and re.search(r"(?m)^[^#\n]*%VB", text):
        errors.append(
            "Apple2026.sbs: SBS must not use %VB/backdrop-buffer viewports; "
            "menu/list clears would replay stale framebuffer content"
        )

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

    for rel_path, expected in REQUIRED_BMP_DIMENSIONS.items():
        path = package_root / rel_path
        if not path.exists():
            continue
        width, height, _ = bmp_decoded_size(path)
        if (width, height) != expected:
            errors.append(
                f"{package_root}: {rel_path} expected {expected[0]}x{expected[1]}, "
                f"found {width}x{height}"
            )

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

    errors.extend(
        audit_wps_hero_art_assets(
            lambda rel_path, x, y: bmp_rgb_at(package_root / rel_path, x, y),
            f"{package_root}: ",
        )
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

        for rel_path, expected in REQUIRED_BMP_DIMENSIONS.items():
            member = f".rockbox/{rel_path}"
            if member not in members:
                continue
            width, height, _ = bmp_decoded_size_bytes(zf.read(member), member)
            if (width, height) != expected:
                errors.append(
                    f"{zip_path}: {member} expected {expected[0]}x{expected[1]}, "
                    f"found {width}x{height}"
                )

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

        errors.extend(
            audit_wps_hero_art_assets(
                lambda rel_path, x, y: bmp_rgb_at_bytes(
                    zf.read(f".rockbox/{rel_path}"),
                    f"{zip_path}:.rockbox/{rel_path}",
                    x,
                    y,
                ),
                f"{zip_path}: ",
            )
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
