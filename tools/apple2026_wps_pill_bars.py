#!/usr/bin/env python3
"""Generate pill-style progress/volume bar BMPs for Apple2026 WPS (Apple Music-like track + fill).

Rockbox draws the backdrop full-width, then clips the bar image from the left by progress.
Both images share geometry: full-width pill (rounded caps). No slider/knob image.

Bar geometry derived from Apple iOS Music scrubber (SVG reference, 390px wide screen):
  Track path:  height 3px, fill #979798 (mid-gray unplayed)
  Played path: fill #3C3C43 opacity 0.6 (dark charcoal played, darker than track)
  Pill radius: 0.5 -- effectively a perfect stadium cap at 3px height.

Adapted for 320x240 iPod hardware: 4px height (half of old 8px).
  CLR_UNPLAYED  #C7C7CC  iOS secondary label gray -- lighter, unplayed portion
  CLR_PLAYED    #3C3C43  Apple's exact played fill, direct from SVG reference
  CLR_SHELL     #FFFFFF  outer canvas matches WPS background"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from apple2026_palette import PROGRESS_TRACK, SHELL_BG, TEXT_TERTIARY

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "wps" / "Apple2026"

# Apple Music scrubber colors (from iOS Stocks SVG reference).
CLR_UNPLAYED = PROGRESS_TRACK
CLR_PLAYED   = TEXT_TERTIARY
CLR_SHELL    = SHELL_BG

def _pill_rgb(width, height, fill):
    """Render a full-width pill on a CLR_SHELL canvas.

    The canvas matches the WPS backdrop so any exposed edge pixels are invisible.
    radius = height//2 gives a perfect stadium (half-circle) cap."""
    img = Image.new("RGB", (width, height), CLR_SHELL)
    r = max(1, height // 2)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=r, fill=fill)
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    # Progress bar -- 4px height (down from 8px), 280px wide (320 - 40px margins)
    pw, ph = 280, 4
    _pill_rgb(pw, ph, CLR_UNPLAYED).save(OUT / "pb_backdrop.bmp")  # unplayed portion
    _pill_rgb(pw, ph, CLR_PLAYED).save(OUT / "pb.bmp")             # played fill
    # Active/seek variant: 1px taller for subtle visual weight during interaction
    ah = 5
    _pill_rgb(pw, ah, CLR_UNPLAYED).save(OUT / "pb_active_backdrop.bmp")
    _pill_rgb(pw, ah, CLR_PLAYED).save(OUT / "pb_active.bmp")

    # Volume bar -- same 4px family, 204px wide (between speaker icons)
    vw, vh = 204, 4
    _pill_rgb(vw, vh, CLR_UNPLAYED).save(OUT / "vb_backdrop.bmp")
    _pill_rgb(vw, vh, CLR_PLAYED).save(OUT / "vb.bmp")

    print("Wrote pill bar BMPs to {}".format(OUT))


if __name__ == "__main__":
    main()
