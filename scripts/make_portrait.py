"""One-off: turn a portrait image into ASCII rows saved as data/portrait.txt.

Usage: python scripts/make_portrait.py path/to/portrait.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

COLS, ROWS = 92, 70
RAMP = " .'`,:;-~+=*xo%#&@"
CROP = (330, 230, 1880, 2048)  # left, top, right, bottom of the subject


def main(src: str) -> None:
    full = Image.open(src).convert("RGB")
    w, h = full.size
    fa = np.asarray(full).astype(float)
    yy, xx = np.mgrid[0:h, 0:w]
    inside = (xx - w / 2) ** 2 + (yy - h / 2) ** 2 < (w * 0.455) ** 2
    cream = np.array([249, 238, 216])
    subject = inside & (np.linalg.norm(fa - cream, axis=2) > 45)
    mask = Image.fromarray((subject * 255).astype("uint8")).crop(CROP)
    mask = np.asarray(mask.resize((COLS, ROWS), Image.BILINEAR)).astype(float) / 255

    im = full.crop(CROP).resize((COLS, ROWS), Image.LANCZOS)
    a = np.asarray(im).astype(float)
    lum = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]) / 255

    # edges keep the outline (glasses, jaw, ear) readable
    edges = np.asarray(im.convert("L").filter(ImageFilter.FIND_EDGES)).astype(float) / 255

    # bright skin = dense, dark hair and shirt still visible as a low tone
    v = 0.18 + 0.82 * lum ** 1.2
    v = np.clip(v + edges * 0.35, 0, 1)
    v = v * (mask > 0.5)

    idx = np.clip((v * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)
    rows = ["".join(RAMP[i] for i in r).rstrip() for r in idx]
    out = Path(__file__).resolve().parent.parent / "data" / "portrait.txt"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(rows)} rows)")


if __name__ == "__main__":
    main(sys.argv[1])
