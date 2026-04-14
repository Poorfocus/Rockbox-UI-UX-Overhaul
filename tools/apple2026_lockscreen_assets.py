#!/usr/bin/env python3
"""Generate Apple2026 lockscreen bitmap assets.

Assets:
  Lockscreen:
    Wallpaper.bmp         320x240 solid white — matches Apple2026 shell background
    LockNotification.bmp  288x70  rounded-rect notification card (light, F2F2F7 fill)
    LockNotifPlay.bmp     12x14   play/pause indicator (2 frames, dark strokes)

All BMPs use Rockbox 24-bit RGB with magenta (FF00FF) transparency key.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from apple2026_palette import ACCENT, GROUPED_FILL, OPAQUE_SEPARATOR, SHELL_BG, TEXT_TERTIARY

ROOT = Path(__file__).resolve().parents[1]
WPS_DIR = ROOT / "wps" / "Apple2026"

TRANSPARENT_KEY = (255, 0, 255)

CLR_ACCENT = ACCENT
CLR_TERTIARY = TEXT_TERTIARY
CLR_WHITE = SHELL_BG


def _wallpaper(path: Path):
    """320x240 solid white — matches the Apple2026 shell background.

    Text colors in the theme are black/gray, so this is always legible.
    Users who swap in a custom wallpaper should also edit the theme cfg
    to choose a dark wallpaper variant; the default ships clean white.
    """
    img = Image.new("RGB", (320, 240), CLR_WHITE)
    img.save(path)
    print(f"  {path.name}  320x240  (solid white)")


def _notification_card(path: Path):
    """288x70 rounded-rect notification card, light Apple system-tray style.

    F2F2F7 fill (iOS grouped table background) with a 1px C6C6C8 border,
    giving it the same visual weight as the Apple Music mini-player separator.
    Rendered opaque — no alpha composite needed.
    """
    w, h, r = 288, 70, 14
    shell_bg = SHELL_BG
    card_fill = GROUPED_FILL
    card_border = OPAQUE_SEPARATOR
    img = Image.new("RGB", (w, h), shell_bg)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=card_fill, outline=card_border, width=1)
    img.save(path)
    print(f"  {path.name}  {w}x{h}  (light card)")


def _lock_notif_play(path: Path):
    """12x14 play/pause indicator, 2 horizontal frames (play, pause).

    Frame 1: play triangle (dark on transparent)
    Frame 2: pause bars (dark on transparent)
    Strokes are 3C3C43 (Apple tertiary) to read on the light card.
    """
    fw, fh = 12, 14
    img = Image.new("RGB", (fw * 2, fh), TRANSPARENT_KEY)
    draw = ImageDraw.Draw(img)
    draw.polygon([(2, 1), (2, 12), (10, 7)], fill=CLR_TERTIARY)
    ox = fw
    draw.rectangle([ox + 2, 1, ox + 4, 12], fill=CLR_TERTIARY)
    draw.rectangle([ox + 7, 1, ox + 9, 12], fill=CLR_TERTIARY)
    img.save(path)
    print(f"  {path.name}  {fw * 2}x{fh}  (2 frames)")


def main():
    WPS_DIR.mkdir(parents=True, exist_ok=True)

    print("Lockscreen assets:")
    _wallpaper(WPS_DIR / "Wallpaper.bmp")
    _notification_card(WPS_DIR / "LockNotification.bmp")
    _lock_notif_play(WPS_DIR / "LockNotifPlay.bmp")

    print("Done.")


if __name__ == "__main__":
    main()
