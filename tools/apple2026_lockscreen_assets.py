#!/usr/bin/env python3
"""Generate Apple2026 lockscreen bitmap assets.

Assets:
  Lockscreen:
    Wallpaper.bmp         320x240 solid white — matches Apple2026 shell background
    LockNotification.bmp  288x70  rounded-rect notification card (light, F2F2F7 fill)
    LockNotifPlay.bmp     12x14   play/pause indicator (2 frames, dark strokes)
    LockBatWarn.bmp       16x16   low-battery warning icon (dark strokes)

All BMPs use Rockbox 24-bit RGB with magenta (FF00FF) transparency key.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
WPS_DIR = ROOT / "wps" / "Apple2026"

TRANSPARENT_KEY = (255, 0, 255)

CLR_ACCENT = (255, 45, 85)       # FF2D55
CLR_TERTIARY = (60, 60, 67)      # 3C3C43
CLR_WHITE = (255, 255, 255)


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
    shell_bg = (255, 255, 255)      # FFFFFF — matches Wallpaper.bmp
    card_fill = (242, 242, 247)     # F2F2F7 — iOS grouped background
    card_border = (198, 198, 200)   # C6C6C8 — Apple separator gray
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


def _lock_bat_warn(path: Path):
    """16x16 low-battery warning icon -- exclamation in circle (dark strokes)."""
    s = 16
    img = Image.new("RGB", (s, s), TRANSPARENT_KEY)
    draw = ImageDraw.Draw(img)
    draw.ellipse([1, 1, s - 2, s - 2], outline=CLR_ACCENT, width=1)
    draw.rectangle([7, 4, 8, 9], fill=CLR_ACCENT)
    draw.rectangle([7, 11, 8, 12], fill=CLR_ACCENT)
    img.save(path)
    print(f"  {path.name}  {s}x{s}")


def main():
    WPS_DIR.mkdir(parents=True, exist_ok=True)

    print("Lockscreen assets:")
    _wallpaper(WPS_DIR / "Wallpaper.bmp")
    _notification_card(WPS_DIR / "LockNotification.bmp")
    _lock_notif_play(WPS_DIR / "LockNotifPlay.bmp")
    _lock_bat_warn(WPS_DIR / "LockBatWarn.bmp")

    print("Done.")


if __name__ == "__main__":
    main()
