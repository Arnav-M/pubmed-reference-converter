"""One-off icon generator for PubMed Reference Converter."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "assets"
SIZE = 256


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (SIZE, SIZE), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Document
    draw.rounded_rectangle((56, 44, 200, 212), radius=16, fill=(249, 250, 251, 255), outline=(13, 148, 136, 255), width=6)
    for y in (88, 112, 136, 160, 184):
        draw.rounded_rectangle((80, y, 176, y + 10), radius=4, fill=(204, 251, 241, 255))

    # Citation link nodes
    draw.ellipse((168, 168, 208, 208), fill=(13, 148, 136, 255))
    draw.ellipse((188, 148, 228, 188), fill=(15, 118, 110, 255))
    draw.arc((188, 148, 228, 208), start=200, end=340, fill=(255, 255, 255, 255), width=6)

    png = OUT / "icon.png"
    ico = OUT / "icon.ico"
    img.save(png)
    img.save(ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Wrote {png} and {ico}")


if __name__ == "__main__":
    main()
