"""Melted-cheese burger, drawn programmatically with Pillow only.

Deterministic: stdlib + Pillow, no network, no external files, no text.
Renders at 2x supersampling (2048) and downscales to 1024x1024 with
Image.Resampling.LANCZOS. Output: /output/entry.png
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

S = 2  # supersampling factor
W = 1024 * S
H = 1024 * S
OUT = "/output/entry.png"


def B(x0, y0, x1, y1):
    """Bounding box in 1024-space, scaled to render space."""
    return [x0 * S, y0 * S, x1 * S, y1 * S]


def XY(x, y):
    return (x * S, y * S)


def lerp(a, b, t):
    return int(round(a + (b - a) * t))


def lerp_color(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def main():
    # ---- background: warm dark-brown vertical gradient -------------------
    img = Image.new("RGB", (W, H), (38, 22, 12))
    d = ImageDraw.Draw(img)
    top = (62, 38, 22)
    bottom = (30, 17, 9)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=lerp_color(top, bottom, y / (H - 1)))

    # ---- top warm light (overlay layer, then alpha_composite) ------------
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse(B(120, -160, 904, 340), fill=(255, 196, 110, 70))
    ov = ov.filter(ImageFilter.GaussianBlur(90 * S))
    img = Image.alpha_composite(img.convert("RGBA"), ov)

    # ---- wooden board -----------------------------------------------------
    d = ImageDraw.Draw(img)
    d.ellipse(B(118, 788, 906, 926), fill=(110, 68, 32))
    d.ellipse(B(146, 802, 878, 912), fill=(146, 94, 46))
    d.ellipse(B(146, 802, 878, 912), outline=(84, 52, 24), width=4 * S)

    # ---- bottom bun (sits on the board) -----------------------------------
    d.rounded_rectangle(B(305, 722, 719, 800), radius=30 * S, fill=(222, 158, 62))
    d.rounded_rectangle(B(305, 722, 719, 756), radius=30 * S, fill=(232, 172, 80))

    # ---- beef patty with grill marks --------------------------------------
    d.rounded_rectangle(B(294, 654, 730, 730), radius=28 * S, fill=(74, 44, 20))
    d.rounded_rectangle(B(294, 654, 730, 676), radius=28 * S, fill=(88, 54, 26))
    for x in range(350, 700, 56):
        d.line([XY(x, 668), XY(x + 34, 712)], fill=(44, 24, 8), width=6 * S)

    # ---- melted cheese: one sheet, wavy bottom edge, three soft bumps -----
    pts = [(282, 616), (742, 616)]
    for i in range(61):
        x = 742 - i * (460 / 60)
        bump = math.sin(math.pi * 3 * (x - 282) / 460.0) ** 2
        y = 652 + 26 * bump
        pts.append((x, y))
    d.polygon([XY(x, y) for x, y in pts], fill=(245, 154, 31))

    # ---- tomato slice ------------------------------------------------------
    d.rounded_rectangle(B(288, 586, 736, 622), radius=16 * S, fill=(217, 58, 43))
    d.rounded_rectangle(B(288, 586, 736, 600), radius=16 * S, fill=(228, 84, 62))

    # ---- lettuce: wavy band + overlapping flat leaves ----------------------
    top_pts = []
    bot_pts = []
    for i in range(61):
        x = 268 + i * (488 / 60)
        top_pts.append((x, 560 + 7 * math.sin(i * 0.55)))
        bot_pts.append((x, 590 + 9 * math.sin(i * 0.55 + 1.2)))
    d.polygon([XY(x, y) for x, y in top_pts] + [XY(x, y) for x, y in reversed(bot_pts)],
              fill=(93, 163, 58))
    leaves = [
        (292, 580, 96, 34, (110, 178, 70)),
        (408, 588, 116, 38, (80, 148, 48)),
        (528, 586, 108, 36, (116, 186, 74)),
        (636, 590, 112, 36, (84, 152, 50)),
        (706, 578, 84, 30, (108, 176, 68)),
    ]
    for x, y, w, h, col in leaves:
        d.ellipse(B(x, y, x + w, y + h), fill=col)

    # ---- dome bun: upper half of a wide flat ellipse + flat lip ------------
    d.pieslice(B(262, 330, 762, 790), 180, 360, fill=(232, 169, 78))
    d.rounded_rectangle(B(262, 544, 762, 580), radius=12 * S, fill=(232, 169, 78))

    # ---- dome shading + highlight (overlay layers, blurred) ---------------
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse(B(300, 468, 724, 606), fill=(120, 60, 10, 60))
    ov = ov.filter(ImageFilter.GaussianBlur(40 * S))
    img = Image.alpha_composite(img.convert("RGBA"), ov)

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse(B(330, 348, 566, 472), fill=(255, 222, 150, 95))
    ov = ov.filter(ImageFilter.GaussianBlur(50 * S))
    img = Image.alpha_composite(img.convert("RGBA"), ov)

    # ---- sesame seeds on the dome (~15, along the dome arc) ---------------
    d = ImageDraw.Draw(img)
    cx, cy, rx, ry = 512, 560, 180, 156
    for i in range(15):
        ang = math.radians(20 + i * (140 / 14))
        x = cx + rx * 0.78 * math.cos(ang)
        y = cy - ry * 0.72 * math.sin(ang)
        w = 15 - (560 - y) * 0.012
        h = w * 0.62
        d.ellipse(B(x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=(247, 227, 176))
        d.ellipse(B(x - w / 2, y - h / 2, x + w / 2 - 3, y + h / 2 - 4),
                  fill=(250, 236, 196))

    # ---- sesame seeds + herb leaves on the board ---------------------------
    for x, y in [(196, 852), (822, 862), (858, 828)]:
        d.ellipse(B(x, y, x + 16, y + 10), fill=(247, 227, 176))
    for x, y in [(768, 838), (812, 852)]:
        d.polygon([XY(x, y), XY(x + 20, y - 9), XY(x + 42, y), XY(x + 20, y + 9)],
                  fill=(63, 122, 38))
        d.line([XY(x + 2, y), XY(x + 40, y)], fill=(44, 92, 26), width=2 * S)

    # ---- downscale to 1024 --------------------------------------------------
    img = img.convert("RGB").resize((1024, 1024), Image.Resampling.LANCZOS)

    # ---- vignette: per-pixel distance mask (centre clear, corners darker) --
    mask = Image.new("L", (1024, 1024), 0)
    px = mask.load()
    for y in range(1024):
        ny = (y - 512) / 512.0
        for x in range(1024):
            nx = (x - 512) / 512.0
            dist = math.sqrt(nx * nx + ny * ny)
            a = (dist - 0.55) / 0.45
            if a > 0:
                px[x, y] = int(min(a, 1.0) * 105)
    black = Image.new("RGB", (1024, 1024), (0, 0, 0))
    img = Image.composite(black, img, mask)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("wrote", OUT, img.size, img.mode)


if __name__ == "__main__":
    main()
