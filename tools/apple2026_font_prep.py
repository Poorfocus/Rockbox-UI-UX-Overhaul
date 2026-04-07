from __future__ import annotations

import csv
import datetime
import json
import math
import os
import struct
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CONVTTF = ROOT / "tools" / "convttf.exe"
OUTPUT_ROOT = ROOT / "Apple Fonts" / "Generated FNT" / "Apple2026"
PREVIEW_ROOT = OUTPUT_ROOT / "previews"
GLYPH_SHEET_ROOT = OUTPUT_ROOT / "glyph_sheets"
INVENTORY_MD = OUTPUT_ROOT / "APPLE2026_FONT_INVENTORY.md"
GLYPH_AUDIT_MD = OUTPUT_ROOT / "APPLE2026_GLYPH_AUDIT.md"
INVENTORY_JSON = OUTPUT_ROOT / "apple2026_font_inventory.json"
INVENTORY_CSV = OUTPUT_ROOT / "apple2026_font_inventory.csv"

START_CHAR = 32
LIMIT_CHAR = 255


@dataclass(frozen=True)
class FamilyPlan:
    family: str
    family_slug: str
    family_type: str
    source_dir: Path
    sizes: List[int]
    weights: Dict[str, str]


@dataclass(frozen=True)
class RolePlan:
    name: str
    target_size: int
    size_min: int
    size_max: int
    families: Tuple[str, ...]
    weights: Tuple[str, ...]


FAMILY_PLANS: List[FamilyPlan] = [
    FamilyPlan(
        family="SF Pro Display",
        family_slug="SFProDisplay",
        family_type="display",
        source_dir=ROOT / "Apple Fonts" / "SF Pro",
        sizes=list(range(19, 26)),
        weights={
            "Regular": "SF-Pro-Display-Regular.otf",
            "Medium": "SF-Pro-Display-Medium.otf",
            "Semibold": "SF-Pro-Display-Semibold.otf",
            "Bold": "SF-Pro-Display-Bold.otf",
        },
    ),
    FamilyPlan(
        family="SF Compact Display",
        family_slug="SFCompactDisplay",
        family_type="display",
        source_dir=ROOT / "Apple Fonts" / "SF Compact",
        sizes=list(range(19, 26)),
        weights={
            "Regular": "SF-Compact-Display-Regular.otf",
            "Medium": "SF-Compact-Display-Medium.otf",
            "Semibold": "SF-Compact-Display-Semibold.otf",
            "Bold": "SF-Compact-Display-Bold.otf",
        },
    ),
    FamilyPlan(
        family="SF Pro Text",
        family_slug="SFProText",
        family_type="text",
        source_dir=ROOT / "Apple Fonts" / "SF Pro",
        sizes=list(range(12, 20)) + [10, 11],
        weights={
            "Regular": "SF-Pro-Text-Regular.otf",
            "Medium": "SF-Pro-Text-Medium.otf",
            "Semibold": "SF-Pro-Text-Semibold.otf",
            "Bold": "SF-Pro-Text-Bold.otf",
        },
    ),
    FamilyPlan(
        family="SF Compact Text",
        family_slug="SFCompactText",
        family_type="text",
        source_dir=ROOT / "Apple Fonts" / "SF Compact",
        sizes=list(range(8, 20)),
        weights={
            "Regular": "SF-Compact-Text-Regular.otf",
            "Medium": "SF-Compact-Text-Medium.otf",
            "Semibold": "SF-Compact-Text-Semibold.otf",
            "Bold": "SF-Compact-Text-Bold.otf",
        },
    ),
]


ROLE_PLANS: List[RolePlan] = [
    RolePlan("Large title / header", 22, 19, 25, ("SF Pro Display", "SF Compact Display"), ("Medium", "Semibold", "Bold")),
    RolePlan("Section/list title", 16, 13, 19, ("SF Pro Text", "SF Compact Text"), ("Medium", "Semibold", "Bold", "Regular")),
    RolePlan("Body primary", 15, 12, 18, ("SF Pro Text", "SF Compact Text"), ("Regular", "Medium", "Semibold")),
    RolePlan("Body secondary", 14, 11, 17, ("SF Pro Text", "SF Compact Text"), ("Regular", "Medium", "Semibold")),
    RolePlan("Compact metadata", 13, 10, 16, ("SF Compact Text", "SF Pro Text"), ("Regular", "Medium", "Semibold")),
    RolePlan("Mini-player title", 16, 13, 19, ("SF Pro Text", "SF Compact Text"), ("Medium", "Semibold", "Bold")),
    RolePlan("Mini-player metadata", 13, 10, 16, ("SF Compact Text", "SF Pro Text"), ("Regular", "Medium", "Semibold")),
    RolePlan("Tracklist primary", 15, 12, 18, ("SF Pro Text", "SF Compact Text"), ("Regular", "Medium", "Semibold")),
    RolePlan("Tracklist secondary", 13, 10, 16, ("SF Compact Text", "SF Pro Text"), ("Regular", "Medium", "Semibold")),
    RolePlan("Loading text", 14, 11, 17, ("SF Pro Text", "SF Compact Text"), ("Regular", "Medium", "Semibold", "Bold")),
    RolePlan("Micro labels / tab labels / tiny shell labels", 11, 8, 14, ("SF Compact Text", "SF Pro Text"), ("Regular", "Medium", "Semibold")),
]


SAMPLE_LONG = "Now Playing: Collected Works of Midnight Radios"
SAMPLE_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SAMPLE_LOWER = "abcdefghijklmnopqrstuvwxyz"
SAMPLE_DIGITS = "0123456789"
SAMPLE_PUNCT = ".,;:!?-_/()[]&+"


def ensure_dirs() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    GLYPH_SHEET_ROOT.mkdir(parents=True, exist_ok=True)


class RBFont:
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

    def render_text(self, text: str, spacing: int = 1) -> Image.Image:
        glyphs: List[Tuple[int, List[int]]] = [self.glyph(ch) for ch in text]
        total_w = sum(g[0] for g in glyphs if g[0] > 0) + spacing * max(0, len(glyphs) - 1)
        if total_w <= 0:
            total_w = 1

        img = Image.new("L", (total_w, self.height), color=255)
        x = 0
        for width, vals in glyphs:
            if width <= 0:
                x += spacing
                continue
            for y in range(self.height):
                row_off = y * width
                for xx in range(width):
                    nib = vals[row_off + xx]
                    img.putpixel((x + xx, y), nib * 17)
            x += width + spacing

        return img



def png_name_safe(text: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in text).strip("_")


def run_convttf(source: Path, output: Path, size: int) -> Tuple[int, str, str]:
    env = os.environ.copy()
    msys_bins = [r"C:\msys64\ucrt64\bin", r"C:\msys64\mingw64\bin", r"C:\msys64\usr\bin"]
    env["PATH"] = ";".join(msys_bins + [env.get("PATH", "")])

    cmd = [
        str(CONVTTF),
        "-s",
        str(START_CHAR),
        "-l",
        str(LIMIT_CHAR),
        "-p",
        str(size),
        "-L",
        "-o",
        str(output),
        str(source),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return proc.returncode, proc.stdout, proc.stderr


def calc_metrics(font: RBFont, size: int, family_type: str, weight: str) -> Dict[str, float | int | str]:
    img_long = font.render_text(SAMPLE_LONG)
    img_digits = font.render_text(SAMPLE_DIGITS)
    img_punct = font.render_text(SAMPLE_PUNCT)

    def ink_ratio(img: Image.Image) -> float:
        px = list(img.getdata())
        dark = sum(1 for p in px if p < 220)
        return dark / max(1, len(px))

    def dark_energy(img: Image.Image) -> int:
        px = list(img.getdata())
        return sum(255 - p for p in px)

    digit_widths = [font.glyph(ch)[0] for ch in SAMPLE_DIGITS]
    digit_w_min = min(digit_widths) if digit_widths else 0
    digit_w_max = max(digit_widths) if digit_widths else 0

    ir = ink_ratio(img_long)
    punct_dark = dark_energy(img_punct)
    digit_dark = dark_energy(img_digits)

    score = 100.0
    score -= min(40.0, abs(ir - 0.18) * 180.0)

    if punct_dark < 900:
        score -= 20
    elif punct_dark < 1300:
        score -= 10

    if digit_w_min < 3 and size >= 12:
        score -= 25
    elif digit_w_min < 2:
        score -= 35

    if abs(digit_w_max - digit_w_min) > 5:
        score -= 8

    if family_type == "text" and size <= 9 and weight in {"Bold", "Semibold"}:
        score -= 15

    score = max(0.0, min(100.0, score))

    status = "primary"
    reasons: List[str] = []

    if ir < 0.065:
        status = "reject"
        reasons.append("too_thin")
    if ir > 0.39:
        status = "reject"
        reasons.append("too_heavy_or_muddy")
    if punct_dark < 700:
        status = "reject"
        reasons.append("punctuation_unclear")
    if size <= 8 and weight == "Bold":
        status = "reject"
        reasons.append("micro_bold_muddy_risk")

    if status != "reject":
        if score < 72:
            status = "fallback"
        if family_type == "text" and size <= 9 and weight in {"Bold", "Semibold"}:
            status = "fallback"
            reasons.append("micro_weight_risk")

    return {
        "ink_ratio": round(ir, 4),
        "punct_dark": punct_dark,
        "digit_dark": digit_dark,
        "digit_w_min": digit_w_min,
        "digit_w_max": digit_w_max,
        "quality_score": round(score, 2),
        "status": status,
        "reasons": reasons,
        "height": font.height,
        "ascent": font.ascent,
        "maxwidth": font.maxwidth,
        "long_width": img_long.width,
    }


def glyph_dark_bbox(width: int, height: int, vals: List[int], threshold: int = 220) -> Tuple[int, int, int, int, int]:
    min_x = width
    min_y = height
    max_x = -1
    max_y = -1
    dark_count = 0

    for y in range(height):
        row_off = y * width
        for x in range(width):
            p = vals[row_off + x] * 17
            if p < threshold:
                dark_count += 1
                if x < min_x:
                    min_x = x
                if x > max_x:
                    max_x = x
                if y < min_y:
                    min_y = y
                if y > max_y:
                    max_y = y

    if dark_count == 0:
        return -1, -1, -1, -1, 0

    return min_x, min_y, max_x, max_y, dark_count


def is_printable_latin_glyph(cp: int) -> bool:
    if 33 <= cp <= 126:
        return True
    if 160 <= cp <= 255 and cp not in {160, 173}:
        return True
    return False


def audit_all_glyphs(font: RBFont) -> Dict[str, int | float | str | List[str]]:
    signatures: Dict[bytes, int] = {}
    missing_nonspace = 0
    blank_nonspace = 0
    top_touch = 0
    bottom_touch = 0
    left_touch = 0
    right_touch = 0

    printable_total = 0

    for cp in range(START_CHAR, LIMIT_CHAR + 1):
        ch = chr(cp)
        width, vals = font.glyph(ch)
        printable = is_printable_latin_glyph(cp)

        if printable:
            printable_total += 1

        if width <= 0:
            if printable:
                missing_nonspace += 1
            continue

        min_x, min_y, max_x, max_y, dark_count = glyph_dark_bbox(width, font.height, vals)
        if printable and dark_count == 0:
            blank_nonspace += 1

        if printable and dark_count > 0:
            if min_y == 0:
                top_touch += 1
            if max_y == font.height - 1:
                bottom_touch += 1
            if min_x == 0:
                left_touch += 1
            if max_x == width - 1:
                right_touch += 1

            sig = bytes([width]) + bytes(vals)
            signatures[sig] = signatures.get(sig, 0) + 1

    duplicate_groups_ge_6 = sum(1 for cnt in signatures.values() if cnt >= 6)
    largest_duplicate_group = max(signatures.values(), default=0)

    glyph_score = 100.0
    glyph_score -= missing_nonspace * 20.0
    glyph_score -= blank_nonspace * 8.0
    glyph_score -= duplicate_groups_ge_6 * 4.0
    if largest_duplicate_group > 8:
        glyph_score -= (largest_duplicate_group - 8) * 2.0
    glyph_score = max(0.0, min(100.0, glyph_score))

    glyph_status = "primary"
    reasons: List[str] = []

    if missing_nonspace > 0:
        glyph_status = "reject"
        reasons.append("glyph_missing_nonspace")
    if blank_nonspace > 2:
        glyph_status = "reject"
        reasons.append("glyph_blank_nonspace")
    if largest_duplicate_group >= 20:
        glyph_status = "reject"
        reasons.append("glyph_suspicious_large_duplicate_cluster")

    if glyph_status != "reject":
        if blank_nonspace > 0 or duplicate_groups_ge_6 > 0 or largest_duplicate_group >= 10:
            glyph_status = "fallback"
            if blank_nonspace > 0:
                reasons.append("glyph_blank_nonspace")
            if duplicate_groups_ge_6 > 0:
                reasons.append("glyph_duplicate_cluster_watch")
            if largest_duplicate_group >= 10:
                reasons.append("glyph_duplicate_cluster_large")

    return {
        "glyph_total": LIMIT_CHAR - START_CHAR + 1,
        "glyph_printable_total": printable_total,
        "glyph_missing_nonspace": missing_nonspace,
        "glyph_blank_nonspace": blank_nonspace,
        "glyph_top_touch_count": top_touch,
        "glyph_bottom_touch_count": bottom_touch,
        "glyph_left_touch_count": left_touch,
        "glyph_right_touch_count": right_touch,
        "glyph_duplicate_groups_ge_6": duplicate_groups_ge_6,
        "glyph_largest_duplicate_group": largest_duplicate_group,
        "glyph_integrity_score": round(glyph_score, 2),
        "glyph_status": glyph_status,
        "glyph_reasons": reasons,
    }


def render_glyph_sheet(font: RBFont, output_path: Path) -> None:
    cols = 16
    rows = math.ceil((LIMIT_CHAR - START_CHAR + 1) / cols)
    cell_w = max(6, font.maxwidth + 4)
    cell_h = max(8, font.height + 4)

    img_w = cols * cell_w
    img_h = rows * cell_h
    img = Image.new("L", (img_w, img_h), color=255)

    index = 0
    for cp in range(START_CHAR, LIMIT_CHAR + 1):
        width, vals = font.glyph(chr(cp))
        col = index % cols
        row = index // cols
        x0 = col * cell_w + 2
        y0 = row * cell_h + 2

        if width > 0 and vals:
            for y in range(font.height):
                row_off = y * width
                for x in range(width):
                    nib = vals[row_off + x]
                    xx = x0 + x
                    yy = y0 + y
                    if 0 <= xx < img_w and 0 <= yy < img_h:
                        img.putpixel((xx, yy), nib * 17)

        index += 1

    img.save(output_path)


def role_candidate_score(entry: Dict, role: RolePlan) -> float:
    score = float(entry["quality_score"])
    score -= abs(int(entry["size"]) - role.target_size) * 4.0

    if entry["weight"] in {"Semibold", "Medium"}:
        score += 4.0
    elif entry["weight"] == "Bold":
        score += 1.0

    if entry["family"] == role.families[0]:
        score += 2.5

    if entry["status"] == "fallback":
        score -= 10.0

    return score


def render_role_preview(role: RolePlan, candidates: List[Dict], output_path: Path) -> None:
    if not candidates:
        return

    label_font = ImageFont.load_default()
    line_h = 58
    width = 1400
    height = 20 + line_h * len(candidates)
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.text((10, 2), f"{role.name} | target={role.target_size}", fill=(0, 0, 0), font=label_font)

    y = 20
    for c in candidates:
        rb = RBFont(Path(c["file"]))
        sample = rb.render_text("Now Playing — Track 07 (Live)")
        sample = sample.resize((sample.width * 2, sample.height * 2), Image.Resampling.NEAREST)

        label = f"{c['size']:>2}px {c['family']} {c['weight']} | {c['status']} | score={c['quality_score']}"
        draw.text((10, y + 4), label, fill=(0, 0, 0), font=label_font)

        sample_rgb = Image.new("RGB", sample.size, (255, 255, 255))
        sample_rgb.paste(sample, mask=None)
        img.paste(sample_rgb, (560, y + 2))

        y += line_h

    img.save(output_path)


def generate_fonts() -> List[Dict]:
    entries: List[Dict] = []

    print("[1/4] Generating .fnt candidates...")
    for plan in FAMILY_PLANS:
        family_dir = OUTPUT_ROOT / plan.family_slug
        family_dir.mkdir(parents=True, exist_ok=True)

        for weight, file_name in plan.weights.items():
            source = plan.source_dir / file_name
            if not source.exists():
                print(f"  [skip] Missing source: {source}")
                continue

            weight_dir = family_dir / weight
            weight_dir.mkdir(parents=True, exist_ok=True)

            for size in sorted(set(plan.sizes)):
                out_name = f"{size:02d}-{plan.family_slug}-{weight}.fnt"
                output = weight_dir / out_name

                rc, out, err = run_convttf(source, output, size)
                entry = {
                    "family": plan.family,
                    "family_slug": plan.family_slug,
                    "family_type": plan.family_type,
                    "weight": weight,
                    "size": size,
                    "source": str(source),
                    "file": str(output),
                    "generated": rc == 0 and output.exists(),
                    "convttf_rc": rc,
                    "convttf_stdout_tail": (out or "")[-3000:],
                    "convttf_stderr_tail": (err or "")[-3000:],
                }
                entries.append(entry)

    print("[2/4] Parsing fonts, scoring readability, and auditing all glyphs...")
    for entry in entries:
        if not entry["generated"]:
            entry.update(
                {
                    "status": "reject",
                    "reasons": ["generation_failed"],
                    "quality_score": 0.0,
                    "glyph_integrity_score": 0.0,
                    "glyph_status": "reject",
                    "glyph_reasons": ["generation_failed"],
                    "glyph_total": LIMIT_CHAR - START_CHAR + 1,
                    "glyph_missing_nonspace": LIMIT_CHAR - START_CHAR,
                    "glyph_blank_nonspace": 0,
                    "glyph_top_touch_count": 0,
                    "glyph_bottom_touch_count": 0,
                    "glyph_left_touch_count": 0,
                    "glyph_right_touch_count": 0,
                    "glyph_duplicate_groups_ge_6": 0,
                    "glyph_largest_duplicate_group": 0,
                    "ink_ratio": 0.0,
                    "punct_dark": 0,
                    "digit_dark": 0,
                    "digit_w_min": 0,
                    "digit_w_max": 0,
                    "height": 0,
                    "ascent": 0,
                    "maxwidth": 0,
                    "long_width": 0,
                }
            )
            continue

        try:
            rb = RBFont(Path(entry["file"]))
            metrics = calc_metrics(rb, int(entry["size"]), str(entry["family_type"]), str(entry["weight"]))
            glyph_metrics = audit_all_glyphs(rb)
            sheet_name = Path(entry["file"]).with_suffix(".png").name
            sheet_path = GLYPH_SHEET_ROOT / sheet_name
            render_glyph_sheet(rb, sheet_path)

            entry.update(metrics)
            entry.update(glyph_metrics)
            entry["glyph_sheet"] = str(sheet_path)

            glyph_status = str(entry.get("glyph_status", "primary"))
            if glyph_status == "reject":
                entry["status"] = "reject"
                entry["reasons"] = sorted(set(list(entry.get("reasons", [])) + list(entry.get("glyph_reasons", []))))
            elif glyph_status == "fallback" and entry.get("status") == "primary":
                entry["status"] = "fallback"
                entry["reasons"] = sorted(set(list(entry.get("reasons", [])) + list(entry.get("glyph_reasons", []))))
        except Exception as exc:  # noqa: BLE001
            entry.update(
                {
                    "status": "reject",
                    "reasons": [f"analysis_failed:{exc}"],
                    "quality_score": 0.0,
                    "glyph_integrity_score": 0.0,
                    "glyph_status": "reject",
                    "glyph_reasons": [f"analysis_failed:{exc}"],
                    "glyph_total": LIMIT_CHAR - START_CHAR + 1,
                    "glyph_missing_nonspace": 0,
                    "glyph_blank_nonspace": 0,
                    "glyph_top_touch_count": 0,
                    "glyph_bottom_touch_count": 0,
                    "glyph_left_touch_count": 0,
                    "glyph_right_touch_count": 0,
                    "glyph_duplicate_groups_ge_6": 0,
                    "glyph_largest_duplicate_group": 0,
                    "glyph_sheet": "",
                    "ink_ratio": 0.0,
                    "punct_dark": 0,
                    "digit_dark": 0,
                    "digit_w_min": 0,
                    "digit_w_max": 0,
                    "height": 0,
                    "ascent": 0,
                    "maxwidth": 0,
                    "long_width": 0,
                }
            )

    print("[3/4] Building role recommendations and preview sheets...")
    role_recs: Dict[str, List[Dict]] = {}
    non_reject = [e for e in entries if e.get("status") != "reject"]

    for role in ROLE_PLANS:
        cands = [
            e
            for e in non_reject
            if e["family"] in role.families
            and e["weight"] in role.weights
            and role.size_min <= int(e["size"]) <= role.size_max
        ]
        cands.sort(key=lambda e: role_candidate_score(e, role), reverse=True)
        picked = cands[:8]
        role_recs[role.name] = picked

        preview_path = PREVIEW_ROOT / f"role_{png_name_safe(role.name.lower())}.png"
        render_role_preview(role, picked, preview_path)

    print("[4/4] Writing inventory outputs...")

    INVENTORY_JSON.write_text(
        json.dumps(
            {
                "generated_at": datetime.datetime.now(datetime.UTC).isoformat(),
                "output_root": str(OUTPUT_ROOT),
                "role_recommendations": role_recs,
                "entries": entries,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    with INVENTORY_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "family",
                "weight",
                "size",
                "status",
                "quality_score",
                "ink_ratio",
                "punct_dark",
                "digit_w_min",
                "digit_w_max",
                "height",
                "ascent",
                "long_width",
                "glyph_integrity_score",
                "glyph_status",
                "glyph_missing_nonspace",
                "glyph_blank_nonspace",
                "glyph_duplicate_groups_ge_6",
                "glyph_largest_duplicate_group",
                "glyph_sheet",
                "file",
                "reasons",
            ]
        )
        for e in sorted(entries, key=lambda x: (x["family"], x["weight"], int(x["size"]))):
            writer.writerow(
                [
                    e["family"],
                    e["weight"],
                    e["size"],
                    e.get("status", "reject"),
                    e.get("quality_score", 0),
                    e.get("ink_ratio", 0),
                    e.get("punct_dark", 0),
                    e.get("digit_w_min", 0),
                    e.get("digit_w_max", 0),
                    e.get("height", 0),
                    e.get("ascent", 0),
                    e.get("long_width", 0),
                    e.get("glyph_integrity_score", 0),
                    e.get("glyph_status", "reject"),
                    e.get("glyph_missing_nonspace", 0),
                    e.get("glyph_blank_nonspace", 0),
                    e.get("glyph_duplicate_groups_ge_6", 0),
                    e.get("glyph_largest_duplicate_group", 0),
                    e.get("glyph_sheet", ""),
                    e["file"],
                    ";".join(e.get("reasons", [])),
                ]
            )

    primary_count = sum(1 for e in entries if e.get("status") == "primary")
    fallback_count = sum(1 for e in entries if e.get("status") == "fallback")
    reject_count = sum(1 for e in entries if e.get("status") == "reject")

    md_lines: List[str] = []
    md_lines.append("# Apple2026 Font Inventory (Wave 2 Font-System Readiness)\n")
    md_lines.append(f"- Output root: `{OUTPUT_ROOT}`")
    md_lines.append(f"- Total generated candidates: **{len(entries)}**")
    md_lines.append(f"- Primary: **{primary_count}** | Fallback: **{fallback_count}** | Reject: **{reject_count}**\n")

    md_lines.append("## Family and size/weight coverage\n")
    for plan in FAMILY_PLANS:
        md_lines.append(f"### {plan.family}")
        md_lines.append(f"- Type: {plan.family_type}")
        md_lines.append(f"- Sizes prepared: {min(plan.sizes)}-{max(plan.sizes)}")
        md_lines.append(f"- Weights prepared: {', '.join(plan.weights.keys())}\n")

    md_lines.append("## Role-based primary candidate sets\n")
    for role in ROLE_PLANS:
        md_lines.append(f"### {role.name}")
        md_lines.append(
            f"- Target cluster: {role.target_size} (range {role.size_min}-{role.size_max}), "
            f"families: {', '.join(role.families)}, weights: {', '.join(role.weights)}"
        )
        picks = role_recs.get(role.name, [])
        if not picks:
            md_lines.append("- No valid candidates found.\n")
            continue
        md_lines.append("- Top picks:")
        for p in picks[:5]:
            md_lines.append(
                f"  - `{Path(p['file']).name}` | status={p['status']} | score={p['quality_score']} | "
                f"ink={p['ink_ratio']} | punct={p['punct_dark']}"
            )
        preview_name = f"role_{png_name_safe(role.name.lower())}.png"
        md_lines.append(f"- Preview sheet: `previews/{preview_name}`\n")

    rejected = [e for e in entries if e.get("status") == "reject"]
    md_lines.append("## Rejected candidates (quality filter)\n")
    if not rejected:
        md_lines.append("- None.\n")
    else:
        for e in sorted(rejected, key=lambda x: (x["family"], x["weight"], int(x["size"]))):
            md_lines.append(
                f"- `{Path(e['file']).name}` -> {', '.join(e.get('reasons', ['quality_fail']))}"
            )
        md_lines.append("")

    md_lines.append("## Existing fallback compatibility fonts (kept, not regenerated)\n")
    existing_fallbacks = [
        ROOT / "Imported Reference Themes" / "Interpod" / ".rockbox" / "fonts" / "16-Inter-SemiBold.fnt",
        ROOT / "Imported Reference Themes" / "Interpod" / ".rockbox" / "fonts" / "16-Inter-V.fnt",
        ROOT / "Imported Reference Themes" / "Interpod" / ".rockbox" / "fonts" / "15-Inter-Bold.fnt",
        ROOT / "Imported Reference Themes" / "Interpod 2" / ".rockbox" / "fonts" / "13-Inter-SemiBold.fnt",
        ROOT / "Imported Reference Themes" / "iRB_Modern" / ".rockbox" / "fonts" / "14-Ubuntu-B.fnt",
    ]
    for fp in existing_fallbacks:
        state = "present" if fp.exists() else "missing"
        md_lines.append(f"- `{fp.relative_to(ROOT)}` ({state})")

    md_lines.append("")
    md_lines.append("## Notes\n")
    md_lines.append("- Generation used: `convttf -s 32 -l 255 -p <size> -L` (no `-x` trim to avoid glyph clipping artifacts).")
    md_lines.append("- Keep this set broad for Wave 3 speed; choose per-surface final locks from role picks without regenerating ad hoc.")

    md_lines.append("")
    md_lines.append("## Full glyph audit summary (U+0020 to U+00FF)\n")
    glyph_primary = sum(1 for e in entries if e.get("glyph_status") == "primary")
    glyph_fallback = sum(1 for e in entries if e.get("glyph_status") == "fallback")
    glyph_reject = sum(1 for e in entries if e.get("glyph_status") == "reject")
    md_lines.append(
        f"- Glyph integrity classification: primary=**{glyph_primary}**, fallback=**{glyph_fallback}**, reject=**{glyph_reject}**"
    )
    md_lines.append("- Per-font glyph sheets: `glyph_sheets/*.png`")
    md_lines.append("- Detailed glyph audit report: `APPLE2026_GLYPH_AUDIT.md`")

    INVENTORY_MD.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    glyph_md: List[str] = []
    glyph_md.append("# Apple2026 Full Glyph Audit (U+0020-U+00FF)\n")
    glyph_md.append(f"- Total fonts scanned: **{len(entries)}**")
    glyph_md.append(f"- Glyphs per font scanned: **{LIMIT_CHAR - START_CHAR + 1}**")
    glyph_md.append("")
    glyph_md.append("## Summary\n")
    glyph_md.append(f"- Primary: **{glyph_primary}**")
    glyph_md.append(f"- Fallback: **{glyph_fallback}**")
    glyph_md.append(f"- Reject: **{glyph_reject}**\n")

    glyph_md.append("## Per-font audit rows\n")
    glyph_md.append("| Font | Glyph status | Integrity score | Missing nonspace | Blank nonspace | Dup groups>=6 | Largest dup group | Glyph sheet |")
    glyph_md.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for e in sorted(entries, key=lambda x: (x["family"], x["weight"], int(x["size"]))):
        glyph_md.append(
            "| "
            + f"`{Path(e['file']).name}` | {e.get('glyph_status', 'reject')} | {e.get('glyph_integrity_score', 0)} | "
            + f"{e.get('glyph_missing_nonspace', 0)} | {e.get('glyph_blank_nonspace', 0)} | "
            + f"{e.get('glyph_duplicate_groups_ge_6', 0)} | {e.get('glyph_largest_duplicate_group', 0)} | "
            + f"`{Path(str(e.get('glyph_sheet', ''))).name}` |"
        )

    GLYPH_AUDIT_MD.write_text("\n".join(glyph_md) + "\n", encoding="utf-8")

    return entries


def main() -> None:
    if not CONVTTF.exists():
        raise SystemExit(f"Missing converter: {CONVTTF}")

    ensure_dirs()
    entries = generate_fonts()

    generated_ok = sum(1 for e in entries if e.get("generated"))
    print("\nDone.")
    print(f"Generated files: {generated_ok}/{len(entries)}")
    print(f"Inventory: {INVENTORY_MD}")
    print(f"Preview sheets: {PREVIEW_ROOT}")


if __name__ == "__main__":
    main()
