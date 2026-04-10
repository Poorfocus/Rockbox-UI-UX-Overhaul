"""Parse Rockbox RB12 .fnt files and compute readability / rhythm metrics."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class RB12Info:
    path: Path
    maxwidth: int
    height: int
    ascent: int
    depth: int
    firstchar: int
    defaultchar: int
    nchars: int
    long_offsets: bool


class RBFont:
    """Minimal RB12 reader (same layout as tools/apple2026_font_prep.RBFont)."""

    def __init__(self, path: Path):
        self.path = path
        data = path.read_bytes()
        if data[:4] != b"RB12":
            raise ValueError(f"Not RB12 font: {path}")

        self.maxwidth, self.height, self.ascent, self.depth = struct.unpack_from("<HHHH", data, 4)
        (
            self.firstchar,
            self.defaultchar,
            self.size,
            self.nbits,
            self.noffset,
            self.nwidth,
        ) = struct.unpack_from("<IIIIII", data, 12)

        pos = 36
        self.bitmap = data[pos : pos + self.nbits]
        pos += self.nbits

        use_long_offset = self.nbits >= 0xFFDB
        self.long_offsets = use_long_offset
        if use_long_offset:
            pos = (pos + 3) & ~3
            self.offsets = list(struct.unpack_from(f"<{self.noffset}I", data, pos))
            pos += self.noffset * 4
        else:
            pos = (pos + 1) & ~1
            self.offsets = list(struct.unpack_from(f"<{self.noffset}H", data, pos))
            pos += self.noffset * 2

        self.widths = list(data[pos : pos + self.nwidth])

    def glyph(self, ch: str) -> Tuple[int, List[int]]:
        cp = ord(ch)
        idx = cp - self.firstchar
        if idx < 0 or idx >= self.size:
            idx = self.defaultchar - self.firstchar
            if idx < 0 or idx >= self.size:
                idx = 0

        width = self.widths[idx]
        if width <= 0:
            return 0, []

        start = self.offsets[idx]
        px_count = width * self.height
        byte_count = (px_count + 1) // 2
        glyph_data = self.bitmap[start : start + byte_count]

        vals: List[int] = []
        for b in glyph_data:
            vals.append(b & 0x0F)
            vals.append((b >> 4) & 0x0F)
            if len(vals) >= px_count:
                break

        return width, vals[:px_count]

    def text_width(self, text: str) -> int:
        total = 0
        for ch in text:
            w, _ = self.glyph(ch)
            total += w
        return total


def font_info(path: Path) -> RB12Info:
    f = RBFont(path)
    return RB12Info(
        path=path,
        maxwidth=f.maxwidth,
        height=f.height,
        ascent=f.ascent,
        depth=f.depth,
        firstchar=f.firstchar,
        defaultchar=f.defaultchar,
        nchars=f.size,
        long_offsets=f.long_offsets,
    )


def ink_ratio_sample(font: RBFont, text: str) -> float:
    """Fraction of non-white pixels in rendered string (approximate rhythm)."""
    glyphs = [font.glyph(ch) for ch in text]
    total_px = 0
    dark = 0
    for width, vals in glyphs:
        if width <= 0:
            continue
        for i, nib in enumerate(vals):
            total_px += 1
            if nib < 15:
                dark += 1
    return dark / max(1, total_px)


def digit_width_stats(font: RBFont) -> Tuple[int, int, int]:
    ws = [font.glyph(ch)[0] for ch in "0123456789"]
    ws = [w for w in ws if w > 0]
    if not ws:
        return 0, 0, 0
    return min(ws), max(ws), sum(ws) // len(ws)
