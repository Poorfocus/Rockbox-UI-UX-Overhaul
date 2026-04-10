from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Sourced Icons" / "iPhone-Rebooting.png"
DST = ROOT / "apps" / "bitmaps" / "native" / "rockboxlogo.320x98x16.bmp"

OUT_W, OUT_H = 320, 98
LOGO_H = 40
BLACK_THRESHOLD = 20


def find_logo_bbox(img: Image.Image):
    px = img.convert("RGB")
    w, h = px.size
    data = px.load()

    min_x, min_y = w, h
    max_x, max_y = -1, -1

    for y in range(h):
        for x in range(w):
            r, g, b = data[x, y]
            if max(r, g, b) > BLACK_THRESHOLD:
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y

    if max_x < min_x or max_y < min_y:
        raise RuntimeError("Could not detect non-black logo bounds in source image")

    return (min_x, min_y, max_x + 1, max_y + 1)


def main():
    src = Image.open(SRC).convert("RGB")
    bbox = find_logo_bbox(src)
    logo = src.crop(bbox)

    ratio = logo.width / logo.height
    logo_w = max(1, int(round(LOGO_H * ratio)))
    logo = logo.resize((logo_w, LOGO_H), Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", (OUT_W, OUT_H), (0, 0, 0))
    x = (OUT_W - logo.width) // 2
    y = (OUT_H - logo.height) // 2
    canvas.paste(logo, (x, y))

    canvas.save(DST, format="BMP")
    print(f"Wrote {DST}")
    print(f"Source logo bbox: {bbox}, resized to: {logo.width}x{logo.height}, pasted at: ({x},{y})")


if __name__ == "__main__":
    main()
