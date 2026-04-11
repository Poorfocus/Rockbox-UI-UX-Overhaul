#!/usr/bin/env python3
"""Generate Apple2026 icon/symbol bitmap assets from sf-symbols-master glyphs.

This script intentionally replaces inherited donor icon sheets for the active
Apple2026 shell pass with symbol-first assets from:
    Sourced Icons/sf-symbols-master/glyphs/*.png
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
GLYPH_DIR = ROOT / "Sourced Icons" / "sf-symbols-master" / "glyphs"
ICONSET_OUT = ROOT / "icons" / "Apple2026Icons.bmp"
WPS_ASSET_DIR = ROOT / "wps" / "Apple2026"
TRANSPARENT_KEY = (255, 0, 255)


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


def _rgba_to_keyed_rgb(img: Image.Image, *, alpha_cutoff: int = 160) -> Image.Image:
    """Convert RGBA to magenta-keyed RGB without pink halo fringing."""
    rgba = img.convert("RGBA")
    out = Image.new("RGB", rgba.size, TRANSPARENT_KEY)

    src = rgba.load()
    dst = out.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = src[x, y]
            if a >= alpha_cutoff:
                dst[x, y] = (r, g, b)
    return out


def _render_symbol_tile(
    name: str,
    width: int,
    height: int,
    *,
    padding: int = 2,
    color: tuple[int, int, int, int] = (0, 0, 0, 255),
    scale: float = 1.0,
    y_shift: int = 0,
) -> Image.Image:
    src = _load_symbol(name)

    max_w = max(1, int((width - 2 * padding) * scale))
    max_h = max(1, int((height - 2 * padding) * scale))

    ratio = min(max_w / src.width, max_h / src.height)
    new_size = (
        max(1, int(round(src.width * ratio))),
        max(1, int(round(src.height * ratio))),
    )

    src = src.resize(new_size, Image.Resampling.BICUBIC)

    tint = Image.new("RGBA", src.size, color)
    tint.putalpha(src.split()[3])

    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    x = (width - new_size[0]) // 2
    y = (height - new_size[1]) // 2 + y_shift
    out.alpha_composite(tint, (x, y))
    return _rgba_to_keyed_rgb(out)


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

    symbol = symbol.resize(new_size, Image.Resampling.LANCZOS)
    tint = Image.new("RGBA", symbol.size, color)
    tint.putalpha(symbol.split()[3])

    ox = x + (w - new_size[0]) // 2
    oy = y + (h - new_size[1]) // 2
    image.alpha_composite(tint, (ox, oy))


def generate_main_iconset() -> None:
    """Generate a 32-icon vertical strip matching Rockbox themable icon order."""
    ordered_symbols = [
        "music.note",                       # Icon_Audio
        "folder.fill",                      # Icon_Folder
        "music.note.list",                  # Icon_Playlist
        "chevron.right",                    # Icon_Cursor
        "play.fill",                        # Icon_Wps
        "gear",                             # Icon_Firmware
        "textformat",                       # Icon_Font
        "globe",                            # Icon_Language
        "slider.horizontal.3",              # Icon_Config
        "app.fill",                         # Icon_Plugin
        "bookmark.fill",                    # Icon_Bookmark
        "dot.radiowaves.right",             # Icon_Preset
        "text.badge.plus",                  # Icon_Queued
        "arrow.up.and.down",                # Icon_Moving
        "keyboard",                         # Icon_Keyboard
        "chevron.left",                     # Icon_Reverse_Cursor
        "questionmark.circle",              # Icon_Questionmark
        "slider.horizontal.3",              # Icon_Menu_setting
        "gear",                             # Icon_Menu_functioncall
        "chevron.right",                    # Icon_Submenu
        "chevron.down",                     # Icon_Submenu_Entered
        "mic.fill",                         # Icon_Recording
        "speaker.2.fill",                   # Icon_Voice
        "gear",                             # Icon_General_settings_menu
        "wrench.fill",                      # Icon_System_menu
        "play.circle.fill",                 # Icon_Playback_menu
        "rectangle.stack.fill",             # Icon_Display_menu
        "tv.fill",                          # Icon_Remote_Display_menu
        "dot.radiowaves.left.and.right",    # Icon_Radio_screen
        "doc.text",                         # Icon_file_view_menu
        "waveform",                         # Icon_EQ
        "music.house.fill",                 # Icon_Rockbox
    ]

    tiles = [
        _render_symbol_tile(name, 15, 16, padding=2, color=(0, 0, 0, 255), scale=0.90)
        for name in ordered_symbols
    ]
    _save_strip(ICONSET_OUT, 15, 16, tiles)


def generate_wps_symbols() -> None:
    # playerStatus.bmp: 4 stacked states, 15x16 each
    player_tiles = [
        _render_symbol_tile("stop.fill", 15, 16, padding=2, scale=0.88),
        _render_symbol_tile("play.fill", 15, 16, padding=2, scale=0.88),
        _render_symbol_tile("pause.fill", 15, 16, padding=2, scale=0.88),
        _render_symbol_tile("forward.fill", 15, 16, padding=2, scale=0.88),
    ]
    _save_strip(WPS_ASSET_DIR / "playerStatus.bmp", 15, 16, player_tiles)

    # holdSlider.bmp: 2 stacked states, 9x12 each
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
    _render_symbol_tile("repeat", 11, 12, padding=1, scale=0.92).save(
        WPS_ASSET_DIR / "repeatShuffle.bmp", "BMP"
    )
    _render_symbol_tile("repeat", 15, 11, padding=1, scale=0.90).save(
        WPS_ASSET_DIR / "repeatAB.bmp", "BMP"
    )
    _render_symbol_tile("shuffle", 17, 11, padding=1, scale=0.90).save(
        WPS_ASSET_DIR / "shuffle.bmp", "BMP"
    )
    _render_symbol_tile("waveform", 66, 11, padding=2, scale=0.88, color=(110, 110, 115, 255)).save(
        WPS_ASSET_DIR / "losslessIndicator.bmp", "BMP"
    )

    _render_symbol_tile("speaker.2.fill", 19, 17, padding=1, scale=0.90).save(
        WPS_ASSET_DIR / "speaker_loud.bmp", "BMP"
    )
    _render_symbol_tile("speaker.slash.fill", 8, 13, padding=0, scale=0.90).save(
        WPS_ASSET_DIR / "speaker_mute.bmp", "BMP"
    )

    # loudness warning mark: compact Apple2026 accent bar
    warn = Image.new("RGB", (4, 18), TRANSPARENT_KEY)
    draw = ImageDraw.Draw(warn)
    draw.rounded_rectangle((1, 2, 2, 15), radius=1, fill=(255, 45, 85))
    warn.save(WPS_ASSET_DIR / "speaker_too_loud.bmp", "BMP")

    # busyIndicator.bmp: 16-frame activity strip, 9x9 each frame
    # Keep a larger transparent work area to avoid rotational clipping.
    busy_strip = Image.new("RGBA", (9, 9 * 16), (0, 0, 0, 0))
    for frame in range(16):
        tile = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
        activity = _load_symbol("rays").resize((5, 5), Image.Resampling.BICUBIC)
        tint = Image.new("RGBA", activity.size, (130, 130, 138, 255))
        tint.putalpha(activity.split()[3])
        tile.alpha_composite(tint, (2, 2))
        angle = int((360 / 16) * frame)
        tile = tile.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)
        busy_strip.alpha_composite(tile, (0, frame * 9))
    _rgba_to_keyed_rgb(busy_strip).save(WPS_ASSET_DIR / "busyIndicator.bmp", "BMP")

    # batteryStatus.bmp: 10-frame strip, 27x19 each frame
    battery_strip = Image.new("RGB", (27, 19 * 10), TRANSPARENT_KEY)
    for idx in range(10):
        level = idx / 9
        tile = Image.new("RGB", (27, 19), TRANSPARENT_KEY)
        draw = ImageDraw.Draw(tile)

        outline = (70, 70, 78)
        fill_bg = (233, 233, 236)
        fill_fg = (0, 0, 0) if level > 0.2 else (255, 45, 85)

        draw.rounded_rectangle((1, 3, 22, 15), radius=2, outline=outline, fill=fill_bg, width=1)
        draw.rounded_rectangle((23, 7, 25, 11), radius=1, outline=outline, fill=outline, width=1)

        inner_w = int(round(18 * level))
        if inner_w > 0:
            draw.rounded_rectangle((3, 5, 3 + inner_w, 13), radius=1, fill=fill_fg)

        battery_strip.paste(tile, (0, idx * 19))
    battery_strip.save(WPS_ASSET_DIR / "batteryStatus.bmp", "BMP")


def generate_shell_bitmaps() -> None:
    # Full-screen WPS backdrop (light-shell baseline)
    wps_bg = Image.new("RGB", (320, 240), (248, 248, 248))
    draw = ImageDraw.Draw(wps_bg)
    draw.line((0, 25, 319, 25), fill=(227, 227, 227), width=1)
    draw.line((0, 203, 319, 203), fill=(227, 227, 227), width=1)
    wps_bg.save(WPS_ASSET_DIR / "wpsBackdrop.bmp", "BMP")

    # USB takeover background aligned to same shell language
    usb_bg = Image.new("RGB", (320, 240), (248, 248, 248))
    draw = ImageDraw.Draw(usb_bg)
    draw.line((0, 25, 319, 25), fill=(227, 227, 227), width=1)
    draw.rounded_rectangle((84, 74, 236, 166), radius=12, outline=(214, 214, 219), width=1)
    usb_bg.save(WPS_ASSET_DIR / "usbBackdrop.bmp", "BMP")

    # Album framing card (used for album art fallback framing)
    frame = Image.new("RGB", (130, 130), (239, 239, 239))
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((0, 0, 129, 129), radius=8, outline=(214, 214, 219), width=1)
    draw.rounded_rectangle((2, 2, 127, 127), radius=7, outline=(231, 231, 235), width=1)
    frame.save(WPS_ASSET_DIR / "albumFramed.bmp", "BMP")

    # Album placeholder card with centered music-note symbol
    placeholder = Image.new("RGBA", (130, 130), (239, 239, 239, 255))
    draw = ImageDraw.Draw(placeholder)
    draw.rounded_rectangle((0, 0, 129, 129), radius=8, outline=(214, 214, 219), width=1)
    _paste_symbol_on_bg(
        placeholder,
        "music.note",
        box=(37, 37, 56, 56),
        color=(110, 110, 115, 255),
        padding=0,
    )
    placeholder.convert("RGB").save(WPS_ASSET_DIR / "albumPlaceholder.bmp", "BMP")



def main() -> None:
    if not GLYPH_DIR.exists():
        raise SystemExit(f"Glyph directory not found: {GLYPH_DIR}")

    WPS_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    generate_main_iconset()
    generate_wps_symbols()
    generate_shell_bitmaps()

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
    print(f"  {WPS_ASSET_DIR / 'albumPlaceholder.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'wpsBackdrop.bmp'}")
    print(f"  {WPS_ASSET_DIR / 'usbBackdrop.bmp'}")


if __name__ == "__main__":
    main()
