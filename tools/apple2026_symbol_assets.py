#!/usr/bin/env python3
"""Generate Apple2026 icon/symbol bitmap assets from sf-symbols-master glyphs.

This script intentionally replaces inherited donor icon sheets for the active
Apple2026 shell pass with symbol-first assets from:
    Sourced Icons/sf-symbols-master/glyphs/*.png
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
GLYPH_DIR = ROOT / "Sourced Icons" / "sf-symbols-master" / "glyphs"
ICONSET_OUT = ROOT / "icons" / "Apple2026Icons.bmp"
WPS_ASSET_DIR = ROOT / "wps" / "Apple2026"
TRANSPARENT_KEY = (255, 0, 255)

# Figma 1:4008: 29×29 icon cell; 30px tiles + list ICON_PADDING give ~Apple Music proportion.
ICON_TILE_W = 30
ICON_TILE_H = 30
CLR_ACCENT = (255, 45, 85, 255)  # FF2D55 — music / root emphasis
CLR_TERTIARY = (60, 60, 67, 255)  # 3C3C43 — settings / secondary chrome

# Downscaling SF glyphs: LANCZOS keeps small tiles sharper than BICUBIC.
_RESAMPLE = Image.Resampling.LANCZOS

# Internal 4x raster before final resize (set via --supersample).
_GLOBAL_SS = 4


def _glyph_name(primary: str, fallback: str) -> str:
    """Use primary SF glyph if present; else fallback (semantic overlays)."""
    if (GLYPH_DIR / f"{primary}.png").is_file():
        return primary
    return fallback


def _load_symbol(name: str) -> Image.Image:
    path = GLYPH_DIR / f"{name}.png"
    if not path.exists():
        raise FileNotFoundError(f"Missing glyph: {path}")

    img = Image.open(path).convert("RGBA")
    alpha = img.split()[3]

    if alpha.getbbox() is None:
        gray = ImageOps.grayscale(img)
        alpha = ImageOps.invert(gray)

    solid = Image.new("RGBA", img.size, (255, 255, 255, 0))
    solid.putalpha(alpha)

    bbox = solid.getbbox()
    return solid.crop(bbox) if bbox else solid


def _rgba_to_keyed_rgb(img: Image.Image, *, alpha_cutoff: int = 40) -> Image.Image:
    """Convert RGBA to magenta-keyed RGB.

    Semi-transparent edge pixels are composited onto white (the shell background)
    before thresholding, yielding smoother perceived edges than a hard alpha cut.
    """
    rgba = img.convert("RGBA")
    bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(bg, rgba)
    comp_rgb = composited.convert("RGB")

    out = Image.new("RGB", rgba.size, TRANSPARENT_KEY)
    src_a = rgba.load()
    src_c = comp_rgb.load()
    dst = out.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            _, _, _, a = src_a[x, y]
            if a >= alpha_cutoff:
                dst[x, y] = src_c[x, y]
    return out


def _render_symbol_tile(
    name: str,
    width: int,
    height: int,
    *,
    padding: int = 4,
    color: tuple[int, int, int, int] = (0, 0, 0, 255),
    scale: float = 1.0,
    y_shift: int = 0,
    supersample: int | None = None,
) -> Image.Image:
    """Rasterize SF glyph at `supersample`× internal resolution, then downscale for crisp edges."""
    src = _load_symbol(name)
    ss = _GLOBAL_SS if supersample is None else supersample
    ss = max(1, min(4, ss))
    w2 = width * ss
    h2 = height * ss
    pad2 = padding * ss
    y_shift2 = y_shift * ss

    max_w = max(1, int((w2 - 2 * pad2) * scale))
    max_h = max(1, int((h2 - 2 * pad2) * scale))

    ratio = min(max_w / src.width, max_h / src.height)
    new_size = (
        max(1, int(round(src.width * ratio))),
        max(1, int(round(src.height * ratio))),
    )

    src = src.resize(new_size, _RESAMPLE)

    tint = Image.new("RGBA", src.size, color)
    tint.putalpha(src.split()[3])

    out_large = Image.new("RGBA", (w2, h2), (0, 0, 0, 0))
    x = (w2 - new_size[0]) // 2
    y = (h2 - new_size[1]) // 2 + y_shift2
    out_large.alpha_composite(tint, (x, y))

    if ss == 1:
        small = out_large
    else:
        small = out_large.resize((width, height), _RESAMPLE)
    return _rgba_to_keyed_rgb(small)


def _save_strip(path: Path, width: int, tile_h: int, symbols: Iterable[Image.Image]) -> None:
    symbols = list(symbols)
    strip = Image.new("RGBA", (width, tile_h * len(symbols)), (0, 0, 0, 0))

    for i, tile in enumerate(symbols):
        strip.alpha_composite(tile.convert("RGBA"), (0, i * tile_h))

    _rgba_to_keyed_rgb(strip).save(path, "BMP")


def _paste_symbol_on_bg(
    image: Image.Image,
    name: str,
    *,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int, int],
    padding: int = 0,
) -> None:
    x, y, w, h = box
    symbol = _load_symbol(name)

    max_w = max(1, w - 2 * padding)
    max_h = max(1, h - 2 * padding)
    ratio = min(max_w / symbol.width, max_h / symbol.height)
    new_size = (
        max(1, int(round(symbol.width * ratio))),
        max(1, int(round(symbol.height * ratio))),
    )

    symbol = symbol.resize(new_size, _RESAMPLE)
    tint = Image.new("RGBA", symbol.size, color)
    tint.putalpha(symbol.split()[3])

    ox = x + (w - new_size[0]) // 2
    oy = y + (h - new_size[1]) // 2
    image.alpha_composite(tint, (ox, oy))


def _main_icon_tint(index: int) -> tuple[int, int, int, int]:
    """Per apps/gui/icon.h Icon_* order.

    Apple2026 color model:
    - Accent red (FF2D55): ALL icons that appear at root menu level and in music
      contexts. This includes nearly everything because the main menu should
      read as a strong red Apple Music-style icon surface.
    - Tertiary gray (3C3C43): ONLY structural nav chrome (cursor, submenu chevrons)
      and items that exclusively appear inside settings submenus.
    """
    gray_structural = {3, 13, 15, 19, 20}
    if index in gray_structural:
        return CLR_TERTIARY
    return CLR_ACCENT


def generate_main_iconset() -> None:
    """Generate a 32-icon vertical strip matching Rockbox themable icon order."""
    ordered_symbols = [
        "music.note",                                          # 0  Icon_Audio
        "folder.fill",                                         # 1  Icon_Folder
        "music.note.list",                                     # 2  Icon_Playlist
        "chevron.right",                                       # 3  Icon_Cursor
        "play.fill",                                           # 4  Icon_Wps
        _glyph_name("memorychip", "gear"),                     # 5  Icon_Firmware
        _glyph_name("textformat.size", "textformat"),          # 6  Icon_Font
        "globe",                                               # 7  Icon_Language
        "slider.horizontal.3",                                 # 8  Icon_Config
        _glyph_name("puzzlepiece.extension.fill", "app.fill"), # 9  Icon_Plugin
        "bookmark.fill",                                       # 10 Icon_Bookmark
        "dot.radiowaves.right",                                # 11 Icon_Preset
        "text.badge.plus",                                     # 12 Icon_Queued
        "arrow.up.and.down",                                   # 13 Icon_Moving
        "keyboard",                                            # 14 Icon_Keyboard
        "chevron.left",                                        # 15 Icon_Reverse_Cursor
        "questionmark.circle",                                 # 16 Icon_Questionmark
        _glyph_name("dial.medium", "slider.horizontal.3"),    # 17 Icon_Menu_setting
        _glyph_name("ellipsis.circle", "gear"),               # 18 Icon_Menu_functioncall
        "chevron.right",                                       # 19 Icon_Submenu
        "chevron.down",                                        # 20 Icon_Submenu_Entered
        "mic.fill",                                            # 21 Icon_Recording
        "speaker.2.fill",                                      # 22 Icon_Voice
        "gear",                                                # 23 Icon_General_settings_menu
        _glyph_name("wrench.and.screwdriver.fill", "wrench.fill"),  # 24 Icon_System_menu
        "play.circle.fill",                                    # 25 Icon_Playback_menu
        "rectangle.stack.fill",                                # 26 Icon_Display_menu
        "tv.fill",                                             # 27 Icon_Remote_Display_menu
        "dot.radiowaves.left.and.right",                       # 28 Icon_Radio_screen
        "doc.text",                                            # 29 Icon_file_view_menu
        "waveform",                                            # 30 Icon_EQ
        "music.house.fill",                                    # 31 Icon_Rockbox
        _glyph_name("person.fill", "person"),                  # 32 Icon_Artist
        _glyph_name("square.stack.fill", "opticaldisc"),       # 33 Icon_Album
    ]

    tiles = [
        _render_symbol_tile(
            name,
            ICON_TILE_W,
            ICON_TILE_H,
            padding=3,
            color=_main_icon_tint(i),
            scale=0.88,
        )
        for i, name in enumerate(ordered_symbols)
    ]
    _save_strip(ICONSET_OUT, ICON_TILE_W, ICON_TILE_H, tiles)


def generate_wps_symbols() -> None:
    # playerStatus.bmp — 4 stacked tiles, 16x18 each.
    #
    # Frame order (matches %mp branch indices used in .wps / .sbs):
    #   Pa (frame 0) = stop       — shown in WPS only when stopped (branch 0)
    #   Pb (frame 1) = pause-bars — shown when PLAYING  (branch 1) — Apple-native: play→show pause
    #   Pc (frame 2) = play-fill  — shown when PAUSED   (branch 2) — Apple-native: pause→show play
    #   Pd (frame 3) = forward    — shown during seek / FF
    #
    # Tile is 16×18 (was 15×16) for a bolder, more Apple-native weight.
    # scale=1.0 + padding=1 fills the cell edge-to-edge for maximum visual presence.
    # The pause.fill glyph renders two vertical bars; play.fill renders a solid right-triangle.
    player_tiles = [
        _render_symbol_tile("stop.fill",    16, 18, padding=1, scale=1.0),   # Pa  stop
        _render_symbol_tile("pause.fill",   16, 18, padding=1, scale=1.0),   # Pb  playing → show pause bars
        _render_symbol_tile("play.fill",    16, 18, padding=1, scale=1.0),   # Pc  paused  → show play triangle
        _render_symbol_tile("forward.fill", 16, 18, padding=1, scale=1.0),   # Pd  seek/FF
    ]
    _save_strip(WPS_ASSET_DIR / "playerStatus.bmp", 16, 18, player_tiles)

    # holdSlider.bmp: §54.2 lock — 2 stacked states, 9x12 each
    hold_tiles = [
        _render_symbol_tile("lock.open", 9, 12, padding=1, scale=0.92),
        _render_symbol_tile("lock.fill", 9, 12, padding=1, scale=0.92),
    ]
    _save_strip(WPS_ASSET_DIR / "holdSlider.bmp", 9, 12, hold_tiles)

    _render_symbol_tile("moon.zzz.fill", 9, 12, padding=1, scale=0.88, color=(110, 110, 115, 255)).save(
        WPS_ASSET_DIR / "sleep.bmp", "BMP"
    )
    _render_symbol_tile("repeat", 16, 11, padding=1, scale=0.90).save(
        WPS_ASSET_DIR / "repeat.bmp", "BMP"
    )
    _render_symbol_tile("repeat.1", 11, 12, padding=1, scale=0.92).save(
        WPS_ASSET_DIR / "repeatOne.bmp", "BMP"
    )
    _render_symbol_tile(
        _glyph_name("shuffle", "repeat"), 11, 12, padding=1, scale=0.92
    ).save(WPS_ASSET_DIR / "repeatShuffle.bmp", "BMP")
    _render_symbol_tile(
        _glyph_name("arrow.left.arrow.right", "repeat"), 15, 11, padding=1, scale=0.88
    ).save(WPS_ASSET_DIR / "repeatAB.bmp", "BMP")
    _render_symbol_tile("shuffle", 17, 11, padding=1, scale=0.90).save(
        WPS_ASSET_DIR / "shuffle.bmp", "BMP"
    )
    _render_symbol_tile("waveform", 66, 11, padding=2, scale=0.88, color=(110, 110, 115, 255)).save(
        WPS_ASSET_DIR / "losslessIndicator.bmp", "BMP"
    )

    # §54.2 speaker icons for volume overlay
    _render_symbol_tile("speaker.2.fill", 19, 17, padding=1, scale=0.90).save(
        WPS_ASSET_DIR / "speaker_loud.bmp", "BMP"
    )
    _render_symbol_tile("speaker.slash.fill", 19, 17, padding=1, scale=0.88).save(
        WPS_ASSET_DIR / "speaker_mute.bmp", "BMP"
    )

    warn = Image.new("RGB", (4, 18), TRANSPARENT_KEY)
    draw = ImageDraw.Draw(warn)
    draw.rounded_rectangle((1, 2, 2, 15), radius=1, fill=(255, 45, 85))
    warn.save(WPS_ASSET_DIR / "speaker_too_loud.bmp", "BMP")

    # busyIndicator.bmp: §54.2 lock — 16-frame activity strip, 9x9 each frame
    busy_strip = Image.new("RGBA", (9, 9 * 16), (0, 0, 0, 0))
    for frame in range(16):
        tile = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
        activity = _load_symbol("rays").resize((5, 5), _RESAMPLE)
        tint = Image.new("RGBA", activity.size, (130, 130, 138, 255))
        tint.putalpha(activity.split()[3])
        tile.alpha_composite(tint, (2, 2))
        angle = int((360 / 16) * frame)
        tile = tile.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)
        busy_strip.alpha_composite(tile, (0, frame * 9))
    _rgba_to_keyed_rgb(busy_strip).save(WPS_ASSET_DIR / "busyIndicator.bmp", "BMP")

    # batteryStatus.bmp — 10-frame strip, 28x15 each: slim capsule, system-green fill
    bw, bh = 28, 15
    battery_strip = Image.new("RGB", (bw, bh * 10), TRANSPARENT_KEY)
    outline = (174, 174, 178)
    shell = (250, 250, 252)
    for idx in range(10):
        level = idx / 9
        tile = Image.new("RGB", (bw, bh), TRANSPARENT_KEY)
        draw = ImageDraw.Draw(tile)
        # Body + small nub (Apple-like proportions, minimal visual noise)
        draw.rounded_rectangle((1, 3, 21, 12), radius=3, outline=outline, fill=shell, width=1)
        draw.rounded_rectangle((22, 6, 25, 9), radius=1, outline=outline, fill=outline, width=1)
        inner_max = 16
        inner_w = int(round(inner_max * level))
        if inner_w > 0:
            if level > 0.35:
                fill_fg = (52, 199, 89)
            elif level > 0.15:
                fill_fg = (255, 149, 0)
            else:
                fill_fg = (255, 59, 48)
            draw.rounded_rectangle((3, 5, 3 + inner_w, 10), radius=2, fill=fill_fg)
        battery_strip.paste(tile, (0, idx * bh))
    battery_strip.save(WPS_ASSET_DIR / "batteryStatus.bmp", "BMP")


def generate_shell_bitmaps() -> None:
    # Full-screen WPS backdrop: pure white shell with subtle art shadow baked in.
    wps_bg = Image.new("RGBA", (320, 240), (255, 255, 255, 255))
    # Bake a subtle shadow ring at the fixed album art position (85,8, 150x150).
    art_cx, art_cy = 85, 8
    for ring in range(4):
        alpha = 20 - ring * 5
        if alpha <= 0:
            break
        sdraw = ImageDraw.Draw(wps_bg)
        x0 = art_cx - 1 - ring
        y0 = art_cy - 1 - ring + 1
        x1 = art_cx + 150 + ring
        y1 = art_cy + 150 + ring + 1
        sdraw.rounded_rectangle((x0, y0, x1, y1), radius=4 + ring,
                                outline=(0, 0, 0, max(0, alpha)), width=1)
    wps_bg.convert("RGB").save(WPS_ASSET_DIR / "wpsBackdrop.bmp", "BMP")

    # USB takeover background aligned to same shell language
    usb_bg = Image.new("RGB", (320, 240), (255, 255, 255))
    draw = ImageDraw.Draw(usb_bg)
    draw.line((0, 25, 319, 25), fill=(198, 198, 200), width=1)
    draw.rounded_rectangle((84, 74, 236, 166), radius=12, outline=(198, 198, 200), width=1)
    usb_bg.save(WPS_ASSET_DIR / "usbBackdrop.bmp", "BMP")

    # Album framing + shadow asset: 156x156 art cell with subtle drop shadow.
    art_sz = 156
    shadow_offset = 2
    shadow_sz = art_sz + shadow_offset * 2
    shadow = Image.new("RGBA", (shadow_sz, shadow_sz), (255, 255, 255, 0))
    sdraw = ImageDraw.Draw(shadow)
    for i in range(3):
        alpha = 25 - i * 8
        sdraw.rounded_rectangle(
            (shadow_offset - i, shadow_offset - i + 1,
             shadow_sz - 1 + i - shadow_offset, shadow_sz - 1 + i - shadow_offset),
            radius=7 + i, outline=(0, 0, 0, max(0, alpha)), width=1)
    shadow_rgb = Image.new("RGB", (shadow_sz, shadow_sz), (255, 255, 255))
    shadow_rgb.paste(
        Image.alpha_composite(
            Image.new("RGBA", (shadow_sz, shadow_sz), (255, 255, 255, 255)),
            shadow
        ).convert("RGB"),
        (0, 0))
    shadow_rgb.save(WPS_ASSET_DIR / "albumShadow.bmp", "BMP")

    frame = Image.new("RGB", (art_sz, art_sz), (255, 255, 255))
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((0, 0, art_sz - 1, art_sz - 1), radius=6, outline=(198, 198, 200), width=1)
    frame.save(WPS_ASSET_DIR / "albumFramed.bmp", "BMP")

    # Art corner mask: 156x156 magenta-keyed bitmap; white pixels paint rounded
    # corners over the 150x150 album art. The art sits at x=85,y=8 in the WPS;
    # this overlay is at x=82,y=5 (3px inset) so it overlaps all four corners.
    # r=6 matches albumFramed.bmp corner radius.
    corner_sz = 156
    corner_r = 6
    art_mask = Image.new("RGB", (corner_sz, corner_sz), TRANSPARENT_KEY)
    c_draw = ImageDraw.Draw(art_mask)
    white = (255, 255, 255)
    # Erase outer pixels: fill a rounded rect with white, then repaint the interior
    # with transparent key. Net result: only corner pixels outside the curve are white.
    c_draw.rounded_rectangle((3, 3, corner_sz - 4, corner_sz - 4),
                             radius=corner_r, outline=(198, 198, 200), fill=TRANSPARENT_KEY, width=1)
    # Corner regions: top-left
    for ry in range(3 + corner_r):
        for rx in range(3 + corner_r):
            px = art_mask.getpixel((rx, ry))
            if px == TRANSPARENT_KEY:
                art_mask.putpixel((rx, ry), white)
    # top-right
    for ry in range(3 + corner_r):
        for rx in range(corner_sz - 3 - corner_r, corner_sz):
            px = art_mask.getpixel((rx, ry))
            if px == TRANSPARENT_KEY:
                art_mask.putpixel((rx, ry), white)
    # bottom-left
    for ry in range(corner_sz - 3 - corner_r, corner_sz):
        for rx in range(3 + corner_r):
            px = art_mask.getpixel((rx, ry))
            if px == TRANSPARENT_KEY:
                art_mask.putpixel((rx, ry), white)
    # bottom-right
    for ry in range(corner_sz - 3 - corner_r, corner_sz):
        for rx in range(corner_sz - 3 - corner_r, corner_sz):
            px = art_mask.getpixel((rx, ry))
            if px == TRANSPARENT_KEY:
                art_mask.putpixel((rx, ry), white)
    art_mask.save(WPS_ASSET_DIR / "wpsArtCorners.bmp", "BMP")

    # Placeholder when no cover: same footprint as art cell
    placeholder = Image.new("RGBA", (art_sz, art_sz), (255, 255, 255, 255))
    draw = ImageDraw.Draw(placeholder)
    draw.rounded_rectangle((0, 0, art_sz - 1, art_sz - 1), radius=6, outline=(198, 198, 200), width=1)
    _paste_symbol_on_bg(
        placeholder,
        "music.note",
        box=(46, 46, 62, 62),
        color=(110, 110, 115, 255),
        padding=0,
    )
    placeholder.convert("RGB").save(WPS_ASSET_DIR / "albumPlaceholder.bmp", "BMP")



def _analyze_main_iconset() -> None:
    """Print non-keyed pixel count per tile (sanity: no empty / all-solid strips)."""
    if not ICONSET_OUT.is_file():
        return
    img = Image.open(ICONSET_OUT).convert("RGB")
    w, h = img.size
    tw, th = ICON_TILE_W, ICON_TILE_H
    n = h // th
    print(f"\nIcon strip analysis ({ICONSET_OUT.name}): {w}×{h}, {n} tiles of {tw}×{th}")
    for i in range(n):
        box = (0, i * th, tw, (i + 1) * th)
        crop = img.crop(box)
        px = list(crop.getdata())
        ink = sum(1 for p in px if p != TRANSPARENT_KEY)
        print(f"  tile {i:2d}: ink_px={ink:5d}  ({100 * ink / len(px):.1f}%)")


def main() -> None:
    global _GLOBAL_SS

    ap = argparse.ArgumentParser(description="Build Apple2026 symbol BMPs from SF Symbols PNGs.")
    ap.add_argument(
        "--supersample",
        type=int,
        default=4,
        help="Internal overscale before downscale (1-4, default 4 for maximum crispness).",
    )
    ap.add_argument(
        "--analyze",
        action="store_true",
        help="After generate, print per-tile ink stats for the main icon strip.",
    )
    args = ap.parse_args()
    _GLOBAL_SS = max(1, min(4, args.supersample))

    if not GLYPH_DIR.exists():
        raise SystemExit(f"Glyph directory not found: {GLYPH_DIR}")

    WPS_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    generate_main_iconset()
    generate_wps_symbols()
    generate_shell_bitmaps()

    if args.analyze:
        _analyze_main_iconset()

    print("Generated:")
    print(f"  {ICONSET_OUT}")
    print(f"  {WPS_ASSET_DIR / 'playerStatus.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'holdSlider.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'sleep.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'repeat.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'repeatOne.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'repeatShuffle.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'repeatAB.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'shuffle.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'losslessIndicator.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'speaker_loud.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'speaker_mute.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'speaker_too_loud.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'busyIndicator.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'batteryStatus.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'albumFramed.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'wpsArtCorners.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'albumShadow.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'albumPlaceholder.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'wpsBackdrop.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'usbBackdrop.bmp'}")


if __name__ == "__main__":
    main()
