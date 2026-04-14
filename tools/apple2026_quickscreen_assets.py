#!/usr/bin/env python3
"""Generate Apple2026 quick settings bitmap assets.

Assets:
  qs_wheel.bmp          92x92 neutral Themeify-style clickwheel graphic
  qs_slider_fill.bmp    20x132 legacy vertical active-fill pill
  qs_slider_track.bmp   20x132 legacy vertical inactive track pill
  qs_bar_fill.bmp      176x6 rounded horizontal active bar
  qs_bar_track.bmp     176x6 rounded horizontal track bar
  qs_sun_max.bmp        14x14 SF Symbols brightness-up icon
  qs_sun_min.bmp        14x14 SF Symbols brightness-down icon
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from apple2026_palette import PROGRESS_TRACK, QS_WHEEL_FILL, QS_WHEEL_OUTLINE, SHELL_BG, TEXT_SECONDARY

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "wps" / "Apple2026"
GLYPHS = ROOT / "Sourced Icons" / "sf-symbols-master" / "glyphs"


def generate_qs_wheel() -> None:
    img = Image.new("RGB", (92, 92), SHELL_BG)
    draw = ImageDraw.Draw(img)

    outer = (0, 0, 91, 91)
    center = (26, 26, 65, 65)
    center_fill = (232, 232, 236)
    arrow = TEXT_SECONDARY

    draw.ellipse(outer, fill=QS_WHEEL_FILL)
    draw.ellipse(center, fill=center_fill)

    # Themeify-style directional ticks, but quieter and neutral for Apple2026.
    draw.polygon([(46, 17), (42, 23), (50, 23)], fill=arrow)
    draw.polygon([(46, 75), (42, 69), (50, 69)], fill=arrow)
    draw.polygon([(17, 46), (23, 42), (23, 50)], fill=arrow)
    draw.polygon([(75, 46), (69, 42), (69, 50)], fill=arrow)

    img.save(OUT / "qs_wheel.bmp", "BMP")


def _vertical_pill(fill: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (20, 132), SHELL_BG)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((4, 0, 15, 131), radius=6, fill=fill)
    return img


def generate_qs_sliders() -> None:
    _vertical_pill(TEXT_SECONDARY).save(OUT / "qs_slider_fill.bmp", "BMP")
    _vertical_pill(PROGRESS_TRACK).save(OUT / "qs_slider_track.bmp", "BMP")


def _rounded_bar(fill: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (176, 6), SHELL_BG)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, 175, 5), radius=3, fill=fill)
    return img


def generate_qs_bars() -> None:
    _rounded_bar(TEXT_SECONDARY).save(OUT / "qs_bar_fill.bmp", "BMP")
    _rounded_bar(PROGRESS_TRACK).save(OUT / "qs_bar_track.bmp", "BMP")


def _symbol_to_bmp(source_name: str, dest_name: str, canvas_size: tuple[int, int]) -> None:
    icon = Image.open(GLYPHS / source_name).convert("RGBA")
    icon.thumbnail(canvas_size, Image.LANCZOS)

    tint = Image.new("RGBA", icon.size, (*TEXT_SECONDARY, 255))
    alpha = icon.getchannel("A")
    tinted = Image.new("RGBA", icon.size, (0, 0, 0, 0))
    tinted.paste(tint, mask=alpha)

    canvas = Image.new("RGBA", canvas_size, (*SHELL_BG, 255))
    x = (canvas_size[0] - tinted.size[0]) // 2
    y = (canvas_size[1] - tinted.size[1]) // 2
    canvas.alpha_composite(tinted, (x, y))
    canvas.convert("RGB").save(OUT / dest_name, "BMP")


def generate_qs_icons() -> None:
    _symbol_to_bmp("sun.max.fill.png", "qs_sun_max.bmp", (14, 14))
    _symbol_to_bmp("sun.min.png", "qs_sun_min.bmp", (14, 14))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    generate_qs_wheel()
    generate_qs_sliders()
    generate_qs_bars()
    generate_qs_icons()
    print("Generated:")
    print(f"  {OUT / 'qs_wheel.bmp'}")
    print(f"  {OUT / 'qs_slider_fill.bmp'}")
    print(f"  {OUT / 'qs_slider_track.bmp'}")
    print(f"  {OUT / 'qs_bar_fill.bmp'}")
    print(f"  {OUT / 'qs_bar_track.bmp'}")
    print(f"  {OUT / 'qs_sun_max.bmp'}")
    print(f"  {OUT / 'qs_sun_min.bmp'}")


if __name__ == "__main__":
    main()
