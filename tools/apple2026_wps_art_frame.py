#!/usr/bin/env python3
"""
apple2026_wps_art_frame.py

Generate Apple Music-style album art framing assets for Apple2026 WPS:
  1. wpsBackdrop.bmp       -- 320x240 stock-neutral backdrop WITH soft shadow baked in
  2. wpsArtCorners.bmp     -- 150x150 cutout overlay sampled from the live backdrop
  3. albumPlaceholder.bmp  -- 150x150 neutral no-art fill that matches the live art box
  4. miniplayer_bg.bmp     -- 320x50 rounded-rectangle mini-player surface
  5. art_mask.bmp          -- 32x32 mini-player art corner mask

The shadow is baked directly into the backdrop to avoid color-mismatch artifacts.
The hero trim uses FF00FF (magenta) as the Rockbox transparency key, but the
opaque corner pixels are copied from the already-shadowed backdrop so the
rounded edge reveals the correct shadowed shell instead of flat white fill.

Reference: iOS Stocks 07 SVG (Apple Music Now Playing screen)

Usage:
  python apple2026_wps_art_frame.py                      # Apple Music defaults
  python apple2026_wps_art_frame.py -r 4 -o 0.08         # tighter corners, softer shadow
  python apple2026_wps_art_frame.py -o 0.15 -b 4.0       # heavier shadow
"""

import argparse
import os
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

from apple2026_palette import SHELL_BG, SHELL_BG_HEX, TEXT_SECONDARY

# -- Defaults (Apple Music reference, fine-tunable via CLI) ------------------

SCREEN_W     = 320
SCREEN_H     = 240
ART_SIZE     = 150       # Album art dimensions (square)
ART_X        = 85        # Album art x position on screen
ART_Y        = 8         # Album art y position on screen
CORNER_R     = 6         # Corner radius in pixels
BG_COLOR     = SHELL_BG            # FFFFFF stock neutral white reset baseline
TRANS_KEY    = (0xFF, 0x00, 0xFF)   # FF00FF magenta (Rockbox transparency convention)

# WPS hero shadow parameters
WPS_SHADOW_DY      = 2       # Downward offset (px)
WPS_SHADOW_BLUR    = 3.2     # Gaussian blur radius
WPS_SHADOW_OPACITY = 0.35    # 35% opacity

# Mini-player shadow parameters
PILL_SHADOW_DY      = 2
PILL_SHADOW_BLUR    = 2.8
PILL_SHADOW_OPACITY = 0.35
MINIPLAYER_FILL     = BG_COLOR
MINIPLAYER_ART_SIZE = 32
MINIPLAYER_ART_R    = 5

# Supersampling scale for smooth curves
SS = 4

# Shadow canvas padding (how far the shadow can spread beyond art edges)
SHADOW_PAD = 8
PLACEHOLDER_BG = BG_COLOR
PLACEHOLDER_NOTE = TEXT_SECONDARY

# Output directory
ASSET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "wps", "Apple2026")
GLYPH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Sourced Icons",
    "sf-symbols-master",
    "glyphs",
)


def _clear_wps_rounded_interior(canvas):
    """Flatten only the rounded silhouette interior back to the shell tone.

    This preserves shadow in the square corner pockets outside the rounded edge
    so the trim overlay can reveal the correct curved-perimeter shadow instead
    of a flat white cap.
    """
    pix = canvas.load()
    for y in range(ART_SIZE):
        for x in range(ART_SIZE):
            if _pixel_in_rounded_rect(x, y, ART_SIZE, ART_SIZE, CORNER_R):
                pix[ART_X + x, ART_Y + y] = BG_COLOR


def generate_backdrop_with_shadow():
    """Generate wpsBackdrop.bmp -- full 320x240 stock-neutral backdrop with
    soft shadow baked in at the album art position."""

    canvas = Image.new('RGB', (SCREEN_W, SCREEN_H), BG_COLOR)

    # Build shadow in a local region then composite onto the backdrop.
    # Shadow region is larger than art to hold blur spread.
    region_w = ART_SIZE + SHADOW_PAD * 2
    region_h = ART_SIZE + SHADOW_PAD * 2

    # Create shadow at supersampled resolution
    shadow = Image.new('RGBA', (region_w * SS, region_h * SS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)

    sx = SHADOW_PAD * SS
    sy = (SHADOW_PAD + WPS_SHADOW_DY) * SS
    sw = ART_SIZE * SS
    sh = ART_SIZE * SS
    sr = CORNER_R * SS

    opacity = int(255 * WPS_SHADOW_OPACITY)
    draw.rounded_rectangle(
        [sx, sy, sx + sw - 1, sy + sh - 1],
        radius=sr,
        fill=(0, 0, 0, opacity)
    )

    # Downsample then blur
    shadow = shadow.resize((region_w, region_h), resample=Image.Resampling.LANCZOS)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=WPS_SHADOW_BLUR))

    # Paste shadow onto backdrop at correct position
    paste_x = ART_X - SHADOW_PAD
    paste_y = ART_Y - SHADOW_PAD
    canvas.paste(shadow, (paste_x, paste_y), shadow)

    # Keep the rounded silhouette interior flat so non-square art padding stays
    # clean, while the square corner pockets still retain the backdrop pixels
    # that the trim overlay needs to reveal around the curved perimeter.
    _clear_wps_rounded_interior(canvas)

    out = os.path.join(ASSET_DIR, "wpsBackdrop.bmp")
    canvas.save(out, "BMP")
    print(f"  [OK] {out}  ({SCREEN_W}x{SCREEN_H}, shadow baked at ({ART_X},{ART_Y}))")
    return out


def _pixel_in_rounded_rect(x, y, w, h, r):
    """Return True if pixel center (x+0.5, y+0.5) is inside a rounded rect."""
    px, py = x + 0.5, y + 0.5
    if px < r and py < r:  # top-left
        return (r - px)**2 + (r - py)**2 <= r * r
    if px > (w - r) and py < r:  # top-right
        return (px - (w - r))**2 + (r - py)**2 <= r * r
    if px < r and py > (h - r):  # bottom-left
        return (r - px)**2 + (py - (h - r))**2 <= r * r
    if px > (w - r) and py > (h - r):  # bottom-right
        return (px - (w - r))**2 + (py - (h - r))**2 <= r * r
    return True  # inside non-corner region


def generate_corners():
    """Generate wpsArtCorners.bmp -- rounded cutout overlay.

    Rockbox color LCD transparency is literal FF00FF, so the hero trim can use
    magenta for the live rounded-art interior and preserve the already-shadowed
    backdrop pixels outside the silhouette. This makes the rounded corners read
    like a real cutout rather than a white matte laid over the shadow.
    """
    backdrop_path = os.path.join(ASSET_DIR, "wpsBackdrop.bmp")
    if not os.path.exists(backdrop_path):
        raise FileNotFoundError(
            "wpsBackdrop.bmp must exist before wpsArtCorners.bmp can be generated"
        )

    result = Image.open(backdrop_path).convert("RGB").crop(
        (ART_X, ART_Y, ART_X + ART_SIZE, ART_Y + ART_SIZE)
    )
    pix = result.load()

    cutout_count = 0
    for y in range(ART_SIZE):
        for x in range(ART_SIZE):
            if _pixel_in_rounded_rect(x, y, ART_SIZE, ART_SIZE, CORNER_R):
                pix[x, y] = TRANS_KEY
                cutout_count += 1

    out = os.path.join(ASSET_DIR, "wpsArtCorners.bmp")
    result.save(out, "BMP")
    print(
        f"  [OK] {out}  ({ART_SIZE}x{ART_SIZE}, "
        f"{cutout_count} cutout px, backdrop-matched corners, key=FF00FF)"
    )
    return out


def _load_symbol_alpha(name):
    path = os.path.join(GLYPH_DIR, f"{name}.png")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing glyph: {path}")

    img = Image.open(path).convert("RGBA")
    alpha = img.split()[3]
    if alpha.getbbox() is None:
        alpha = ImageOps.invert(ImageOps.grayscale(img))

    bbox = alpha.getbbox()
    if bbox:
        alpha = alpha.crop(bbox)
    return alpha


def generate_placeholder():
    """Generate albumPlaceholder.bmp -- exact-fit placeholder with no extra frame."""
    canvas = Image.new("RGBA", (ART_SIZE, ART_SIZE), PLACEHOLDER_BG + (255,))
    symbol_alpha = _load_symbol_alpha("music.note")

    max_w = int(ART_SIZE * 0.44)
    max_h = int(ART_SIZE * 0.44)
    ratio = min(max_w / symbol_alpha.width, max_h / symbol_alpha.height)
    new_size = (
        max(1, int(round(symbol_alpha.width * ratio))),
        max(1, int(round(symbol_alpha.height * ratio))),
    )

    symbol_alpha = symbol_alpha.resize(new_size, Image.Resampling.LANCZOS)
    tint = Image.new("RGBA", new_size, PLACEHOLDER_NOTE + (255,))
    tint.putalpha(symbol_alpha)

    x = (ART_SIZE - new_size[0]) // 2
    y = (ART_SIZE - new_size[1]) // 2
    canvas.alpha_composite(tint, (x, y))

    out = os.path.join(ASSET_DIR, "albumPlaceholder.bmp")
    canvas.convert("RGB").save(out, "BMP")
    print(f"  [OK] {out}  ({ART_SIZE}x{ART_SIZE}, exact-fit no-art placeholder)")
    return out


def generate_miniplayer():
    """Generate miniplayer_bg.bmp as a restrained rounded rectangle.
    Size: 320x50. Background and body both use stock-neutral white; shadow provides separation."""
    width, height = 320, 50
    pill_w, pill_h = 300, 40
    pill_x, pill_y = 10, 4
    r = 13

    canvas = Image.new('RGB', (width, height), BG_COLOR)

    # Shadow
    shadow = Image.new('RGBA', (width * SS, height * SS), (0,0,0,0))
    s_draw = ImageDraw.Draw(shadow)
    sx, sy = pill_x * SS, (pill_y + PILL_SHADOW_DY) * SS
    sw, sh = pill_w * SS, pill_h * SS
    s_draw.rounded_rectangle([sx, sy, sx + sw - 1, sy + sh - 1], radius=r * SS,
                             fill=(0,0,0, int(255 * PILL_SHADOW_OPACITY)))

    shadow = shadow.resize((width, height), resample=Image.Resampling.LANCZOS)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=PILL_SHADOW_BLUR))

    # Bias the pill shadow downward so the shell/body transition stays clean at
    # the top edge instead of reading as a halo around the full perimeter.
    shadow_alpha = shadow.getchannel("A")
    top_bias = Image.new("L", (width, height), 255)
    bias_draw = ImageDraw.Draw(top_bias)
    bias_draw.rectangle([0, 0, width, pill_y], fill=0)
    bias_draw.rectangle([0, pill_y + 4, width, height], fill=255)
    for offset in range(4):
        alpha = int(255 * ((offset + 1) / 4.0))
        bias_draw.rectangle([0, pill_y + offset, width, pill_y + offset], fill=alpha)
    shadow.putalpha(ImageChops.multiply(shadow_alpha, top_bias))
    canvas.paste(shadow, (0, 0), shadow)

    # Body
    # Use a hard mask for the body pass so the shell-toned fill cleanly erases
    # the shadow from the pill interior without leaving a bright or tinted fringe
    # at the rounded edge. The shadow alone should define the separation.
    mask_ss = Image.new("L", (width * SS, height * SS), 0)
    mask_draw = ImageDraw.Draw(mask_ss)
    mask_draw.rounded_rectangle(
        [pill_x * SS, pill_y * SS, (pill_x + pill_w) * SS - 1, (pill_y + pill_h) * SS - 1],
        radius=r * SS,
        fill=255,
    )
    mask = mask_ss.resize((width, height), resample=Image.Resampling.LANCZOS)
    mask = mask.point(lambda value: 255 if value >= 128 else 0, mode="L")
    body = Image.new("RGB", (width, height), MINIPLAYER_FILL)
    canvas.paste(body, (0, 0), mask)

    out = os.path.join(ASSET_DIR, "miniplayer_bg.bmp")
    canvas.save(out, "BMP")
    print(f"  [OK] {out}  ({width}x{height}, 300x40 rounded rectangle, r=13, fill={SHELL_BG_HEX})")
    return out


def generate_miniplayer_art_mask():
    """Generate art_mask.bmp for the 32x32 mini-player art slot."""
    result = Image.new("RGB", (MINIPLAYER_ART_SIZE, MINIPLAYER_ART_SIZE), TRANS_KEY)
    pix = result.load()

    for y in range(MINIPLAYER_ART_SIZE):
        for x in range(MINIPLAYER_ART_SIZE):
            if not _pixel_in_rounded_rect(
                x, y, MINIPLAYER_ART_SIZE, MINIPLAYER_ART_SIZE, MINIPLAYER_ART_R
            ):
                pix[x, y] = MINIPLAYER_FILL

    out = os.path.join(ASSET_DIR, "art_mask.bmp")
    result.save(out, "BMP")
    print(
        f"  [OK] {out}  ({MINIPLAYER_ART_SIZE}x{MINIPLAYER_ART_SIZE}, "
        f"r={MINIPLAYER_ART_R}, fill={SHELL_BG_HEX})"
    )
    return out


def parse_args():
    p = argparse.ArgumentParser(
        description="Generate Apple Music-style album-art framing for Apple2026 WPS.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  python %(prog)s                              # Apple Music defaults
  python %(prog)s -r 4 -o 0.08                 # tighter corners, softer shadow
  python %(prog)s -o 0.15 -b 4.0               # heavier shadow
"""
    )
    p.add_argument("--corner-radius", "-r", type=int, default=CORNER_R,
                   help=f"Corner radius in pixels (default: {CORNER_R})")
    p.add_argument("--shadow-opacity", "-o", type=float, default=WPS_SHADOW_OPACITY,
                   help=f"WPS shadow opacity 0.0-1.0 (default: {WPS_SHADOW_OPACITY})")
    p.add_argument("--shadow-offset", "-y", type=int, default=WPS_SHADOW_DY,
                   help=f"WPS shadow vertical offset in px (default: {WPS_SHADOW_DY})")
    p.add_argument("--shadow-blur", "-b", type=float, default=WPS_SHADOW_BLUR,
                   help=f"WPS shadow gaussian blur radius (default: {WPS_SHADOW_BLUR})")
    return p.parse_args()


def main():
    global CORNER_R, WPS_SHADOW_OPACITY, WPS_SHADOW_DY, WPS_SHADOW_BLUR

    args = parse_args()
    CORNER_R       = args.corner_radius
    WPS_SHADOW_OPACITY = args.shadow_opacity
    WPS_SHADOW_DY      = args.shadow_offset
    WPS_SHADOW_BLUR    = args.shadow_blur

    print("Apple2026 WPS Album Art Frame Generator")
    print(f"  Background:      {SHELL_BG_HEX} (stock neutral white)")
    print(f"  Mini-player:     fill={SHELL_BG_HEX}  body=300x40  radius=13")
    print(f"  Corner radius:   {CORNER_R}px")
    print(f"  WPS shadow:      opacity={WPS_SHADOW_OPACITY:.0%}  dy={WPS_SHADOW_DY}px  blur={WPS_SHADOW_BLUR}px")
    print(f"  Pill shadow:     opacity={PILL_SHADOW_OPACITY:.0%}  dy={PILL_SHADOW_DY}px  blur={PILL_SHADOW_BLUR}px")
    print(f"  Trans key:       FF00FF (magenta)")
    print()

    os.makedirs(ASSET_DIR, exist_ok=True)

    generate_backdrop_with_shadow()
    generate_corners()
    generate_placeholder()
    generate_miniplayer()
    generate_miniplayer_art_mask()

    print()
    print("Done. Assets regenerated in wps/Apple2026/.")


if __name__ == "__main__":
    main()
