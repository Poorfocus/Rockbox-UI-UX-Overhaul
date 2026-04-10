#!/usr/bin/env python3
"""Convert OTF/TTF to Rockbox RB12 .fnt via FreeType (outline rasterization, not .fnt scaling).

Matches the intent of tools/convttf.c: FT_Load_Glyph + 4-bpp nibble packing.

Spacing: Rockbox sums each glyph's stored width as the cursor advance (no GPOS / pair
kerning tables in RB12 or in lcd-bitmap-common text). This tool uses the scaled
horizontal advance and places the rendered bitmap at bitmap_left so sidebearings match
the outline font. That fixes the usual "squeezed" look from using ink width or pitch
as advance. OpenType pair kerning (e.g. AV, To) is not available on device; use
`--track` (and optionally `--space-extra`) to tune perceived density toward Apple UI.

Example (repo includes SF Pro under Apple Fonts/SF Pro/):
  python tools/otf_to_rb12_fnt.py "Apple Fonts/SF Pro/SF-Pro-Display-Bold.otf" \\
    fonts/35-SFProDisplay-Bold.fnt -p 35

Requires: pip install freetype-py
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path
from typing import List

import freetype as ft


def get_char_index(face: ft.Face, code: int) -> int:
    idx = face.get_char_index(code)
    if idx <= 0 or idx > face.num_glyphs:
        return 0
    return idx


def glyph_cell_width(
    face: ft.Face,
    digit_width: int,
    code: int,
    *,
    track_fixed: int = 0,
    space_extra_px: int = 0,
) -> int:
    """Width of each glyph cell: Rockbox uses this as both bitmap stride and advance.

    track_fixed: added to FT advance in 1/64 px (global tracking / letter-spacing).
    space_extra_px: extra pixels for U+0020 only (word-spacing tweak).
    """
    if ord("0") <= code <= ord("9") and digit_width:
        extra = (track_fixed + 32) >> 6
        return max(1, digit_width + extra)
    slot = face.glyph
    adv = (int(slot.advance.x) + track_fixed + 32) >> 6
    if adv < 1:
        adv = 1
    if code == 32 and space_extra_px > 0:
        adv += space_extra_px
    bl = int(slot.bitmap_left)
    bw = int(slot.bitmap.width) if slot.bitmap.width else 0
    ink_right = bl + bw
    if ink_right > adv:
        adv = ink_right
    return adv


def check_digit_width(face: ft.Face, load_flags: int) -> int:
    last_adv = -1
    for code in range(ord("0"), ord("9") + 1):
        face.load_char(chr(code), load_flags)
        adv = face.glyph.metrics.horiAdvance
        if last_adv != -1 and last_adv != adv:
            return 0
        if face.glyph.metrics.horiBearingX < 0:
            return 0
        last_adv = adv
    return last_adv >> 6 if last_adv and last_adv > 0 else 0


def convert(
    otf_path: Path,
    out_path: Path,
    *,
    pixel_size: int,
    start_char: int,
    limit_char: int,
    light_hinting: bool,
    digits_equal: bool,
    track_px: float = 0.0,
    space_extra_px: int = 0,
) -> None:
    face = ft.Face(str(otf_path))
    face.set_pixel_sizes(0, pixel_size)

    load_flags = ft.FT_LOAD_RENDER | ft.FT_LOAD_NO_BITMAP
    if light_hinting:
        load_flags |= ft.FT_LOAD_TARGET_LIGHT

    digit_width = check_digit_width(face, load_flags) if digits_equal else 0
    track_fixed = int(round(track_px * 64))

    trim_ap = trim_dp = trim_aa = trim_da = 0
    between_row = 0.0
    extra_space = float(between_row - trim_aa - trim_da)
    asc_raw = face.size.ascender * (100 - trim_ap) // 100
    desc_raw = face.size.descender * (100 - trim_dp) // 100
    ascent = (asc_raw >> 6) - trim_aa
    height = ((asc_raw - desc_raw) >> 6) + int(extra_space)

    depth = 2
    bit_shift = 1 << depth
    pixel_per_byte = 8 // bit_shift  # 2 nibbles per byte

    maxwidth = 1
    firstchar = limit_char
    lastchar = start_char
    total_bits = 0

    for code in range(start_char, limit_char + 1):
        charindex = get_char_index(face, code)
        if not charindex:
            continue
        err = face.load_glyph(charindex, load_flags)
        if err:
            continue
        w = glyph_cell_width(
            face,
            digit_width,
            code,
            track_fixed=track_fixed,
            space_extra_px=space_extra_px,
        )
        empty_l = empty_r = 0
        if w == 0:
            continue
        maxwidth = max(maxwidth, w)
        total_bits += (w * height + pixel_per_byte - 1) // pixel_per_byte
        if code >= lastchar:
            lastchar = code
        if code <= firstchar:
            firstchar = code

    if firstchar > lastchar:
        raise SystemExit("No glyphs in range; check font file.")

    size = lastchar - firstchar + 1
    use_long = total_bits >= 0xFFDB

    bitmap = bytearray(total_bits + 1024)
    offsets_l: List[int] = []
    widths: List[int] = []

    idx_out = 0

    def pack_glyph(code: int) -> tuple[int, int]:
        nonlocal idx_out
        charindex = get_char_index(face, code)
        if not charindex:
            return 0, 0
        err = face.load_glyph(charindex, load_flags)
        if err:
            return 0, 0
        slot = face.glyph
        source = slot.bitmap
        w = glyph_cell_width(
            face,
            digit_width,
            code,
            track_fixed=track_fixed,
            space_extra_px=space_extra_px,
        )
        if w == 0:
            return 0, 0
        src = source.buffer
        tmpbuf = bytearray([0xFF] * (w * height))
        start_y = ascent - int(slot.bitmap_top)
        glyph_height = int(source.rows)
        stride = int(source.pitch)
        bl = int(slot.bitmap_left)
        bw = int(source.width) if source.width else 0

        for row in range(glyph_height):
            ry = row + start_y
            if ry < 0 or ry >= height:
                continue
            for col in range(bw):
                dst_x = bl + col
                if dst_x < 0 or dst_x >= w:
                    continue
                dst = ry * w + dst_x
                tsrc = row * stride + col
                if tsrc < len(src):
                    tmpbuf[dst] = 0xFF - src[tsrc]

        start_idx = idx_out
        numbits = pixel_per_byte
        field = 0
        for row in range(height):
            for col in range(w):
                src2 = tmpbuf[row * w + col]
                cur_col = (int(src2) + 8) // 17
                field |= cur_col << (bit_shift * (pixel_per_byte - numbits))
                numbits -= 1
                if numbits == 0:
                    bitmap[idx_out] = field & 0xFF
                    idx_out += 1
                    numbits = pixel_per_byte
                    field = 0
        if numbits != pixel_per_byte:
            bitmap[idx_out] = field & 0xFF
            idx_out += 1
        return w, start_idx

    offset_table: List[int] = []
    width_table: List[int] = []

    for code in range(firstchar, lastchar + 1):
        charindex = get_char_index(face, code)
        if not charindex:
            offset_table.append(offset_table[0] if offset_table else 0)
            width_table.append(width_table[0] if width_table else 0)
            continue
        err = face.load_glyph(charindex, load_flags)
        if err:
            offset_table.append(offset_table[0] if offset_table else 0)
            width_table.append(width_table[0] if width_table else 0)
            continue
        w = glyph_cell_width(
            face,
            digit_width,
            code,
            track_fixed=track_fixed,
            space_extra_px=space_extra_px,
        )
        if w == 0:
            offset_table.append(offset_table[0] if offset_table else 0)
            width_table.append(width_table[0] if width_table else 0)
            continue
        w2, off = pack_glyph(code)
        offset_table.append(off)
        width_table.append(w2)

    nbits = idx_out
    bitmap = bytes(bitmap[:nbits])

    defaultchar = firstchar

    out = bytearray()
    out.extend(b"RB12")
    out.extend(struct.pack("<HHHH", maxwidth, height, ascent, 1))
    out.extend(
        struct.pack(
            "<IIIIII",
            firstchar,
            defaultchar,
            size,
            nbits,
            size,
            size,
        )
    )
    out.extend(bitmap)
    pad = b"\x00" * 16
    if use_long:
        skip = ((nbits + 3) & ~3) - nbits
        out.extend(pad[:skip])
        for o in offset_table:
            out.extend(struct.pack("<I", o))
    else:
        skip = ((nbits + 1) & ~1) - nbits
        out.extend(pad[:skip])
        for o in offset_table:
            out.extend(struct.pack("<H", o & 0xFFFF))
    out.extend(bytes(width_table))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(out)
    print(
        f"Wrote {out_path} (px={pixel_size}, h={height}, ascent={ascent}, "
        f"maxw={maxwidth}, nbits={nbits}, long={use_long}, "
        f"track_px={track_px}, space+={space_extra_px})"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("otf", type=Path)
    ap.add_argument("out_fnt", type=Path)
    ap.add_argument("-p", "--pixels", type=int, required=True)
    ap.add_argument("-s", type=int, default=32, dest="start")
    ap.add_argument("-l", type=int, default=255, dest="limit")
    ap.add_argument("-L", dest="light", action="store_true", default=True)
    ap.add_argument("--no-light", action="store_true")
    ap.add_argument("--no-equal-digits", action="store_true")
    ap.add_argument(
        "--track",
        type=float,
        default=0.0,
        help="Global letter-spacing in px (added to each glyph advance; typical 0–0.5).",
    )
    ap.add_argument(
        "--space-extra",
        type=int,
        default=0,
        help="Extra px for U+0020 space only (word spacing; 0–2).",
    )
    args = ap.parse_args()
    convert(
        args.otf,
        args.out_fnt,
        pixel_size=args.pixels,
        start_char=args.start,
        limit_char=args.limit,
        light_hinting=args.light and not args.no_light,
        digits_equal=not args.no_equal_digits,
        track_px=args.track,
        space_extra_px=max(0, min(2, args.space_extra)),
    )


if __name__ == "__main__":
    main()
