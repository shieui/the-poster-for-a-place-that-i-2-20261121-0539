#!/usr/bin/env python3
"""VELMARA - Isles of the Glass Tide.

A travel poster for a place that does not exist. Drawn entirely with PIL:
vector-style shapes, gradients, a glass lighthouse, a golden-hour sea.
No network, no downloaded assets, no randomness. Deterministic output.

Writes exactly one image to /output/entry.png (1024x1024 PNG).
Fonts ship in this repository (fonts/, DejaVu, freely redistributable)
so the program works in a sandbox with no system fonts.
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1024, 1024
OUT = "/output/entry.png"
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette
INDIGO = (24, 28, 66)        # top of sky
VIOLET = (74, 52, 110)       # mid sky
ROSE = (196, 96, 110)        # low sky
PEACH = (255, 178, 110)      # horizon glow
SUN_CORE = (255, 236, 180)
SUN_EDGE = (255, 178, 96)
SEA_TOP = (44, 128, 138)     # sea at horizon
SEA_DEEP = (8, 52, 76)       # sea at bottom
CLIFF = (22, 22, 52)         # silhouette
ROCK = (38, 30, 62)
CREAM = (255, 246, 226)      # title
GOLD = (255, 205, 120)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(draw, x0, y0, x1, y1, stops):
    """Vertical gradient between (r,g,b) stops; stops = [(pos0..1, color)]."""
    span = y1 - y0
    for y in range(y0, y1):
        t = (y - y0) / max(span - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                lt = 0.0 if p1 == p0 else (t - p0) / (p1 - p0)
                draw.line([(x0, y), (x1, y)], fill=lerp(c0, c1, lt))
                break


def glow(img, cx, cy, r, color, alpha):
    """Soft radial glow: concentric translucent discs on an overlay."""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    steps = 24
    for i in range(steps, 0, -1):
        rr = r * i / steps
        a = int(alpha * (1 - i / steps) ** 2)
        od.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                   fill=color + (a,))
    img.alpha_composite(ov)


def beam(img, x0, y0, x1, y1, width, color, alpha):
    """A translucent wedge of light, widening away from (x0, y0)."""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.polygon([(x0, y0 - 4), (x1, y1 - width), (x1, y1 + width),
                (x0, y0 + 4)], fill=color + (alpha,))
    img.alpha_composite(ov)


def cloud(draw, cx, cy, w, h, color, alpha):
    ov = Image.new("RGBA", draw._image.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for dx, dy, rw, rh in [(-0.32, 0.10, 0.42, 0.42), (0.0, -0.08, 0.5, 0.5),
                           (0.34, 0.08, 0.40, 0.40), (0.0, 0.12, 0.95, 0.34)]:
        od.ellipse([cx + dx * w - rw * w / 2, cy + dy * h - rh * h / 2,
                    cx + dx * w + rw * w / 2, cy + dy * h + rh * h / 2],
                   fill=color + (alpha,))
    ov = ov.filter(ImageFilter.GaussianBlur(6))
    draw._image.alpha_composite(ov)


def tracked_text(draw, cx, y, text, font, fill, tracking, shadow=None):
    """Draw centred text with letter spacing; optional offset shadow."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, wch in zip(text, widths):
        if shadow is not None:
            draw.text((x + 3, y + 4), ch, font=font, fill=shadow)
        draw.text((x, y), ch, font=font, fill=fill)
        x += wch + tracking
    return total


def bird(draw, x, y, s, color):
    draw.arc([x - s, y - s * 0.6, x, y + s * 0.6], 200, 340, fill=color, width=3)
    draw.arc([x, y - s * 0.6, x + s, y + s * 0.6], 200, 340, fill=color, width=3)


def main():
    img = Image.new("RGBA", (W, H), INDIGO)
    d = ImageDraw.Draw(img)

    # --- sky ----------------------------------------------------------------
    vgrad(d, 0, 0, W, 660, [(0.0, INDIGO), (0.45, VIOLET),
                            (0.78, ROSE), (1.0, PEACH)])
    # faint stars fading out toward the horizon
    for (sx, sy, sr) in [(80, 60, 2), (180, 130, 2), (420, 48, 2),
                         (640, 90, 3), (880, 55, 2), (950, 140, 2),
                         (300, 200, 2), (760, 180, 2), (540, 130, 2)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                  fill=(255, 244, 214, 200))

    # --- sun, low over the sea, left of centre ------------------------------
    sun_x, sun_y, sun_r = 330, 585, 92
    glow(img, sun_x, sun_y, 300, (255, 170, 90), 90)
    glow(img, sun_x, sun_y, 170, (255, 200, 130), 130)
    d = ImageDraw.Draw(img)
    d.ellipse([sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r],
              fill=SUN_CORE + (255,))
    d.ellipse([sun_x - sun_r * 0.72, sun_y - sun_r * 0.72,
               sun_x + sun_r * 0.72, sun_y + sun_r * 0.72],
              fill=(255, 244, 205, 255))

    # --- clouds -------------------------------------------------------------
    cloud(d, 820, 180, 300, 46, (255, 214, 178), 110)
    cloud(d, 170, 300, 260, 40, (255, 196, 160), 90)
    cloud(d, 700, 330, 200, 34, (255, 205, 170), 80)

    # --- birds ---------------------------------------------------------------
    for bx, by, bs in [(120, 210, 16), (170, 180, 12), (880, 260, 14),
                       (920, 225, 10), (610, 150, 11)]:
        bird(d, bx, by, bs, (40, 30, 70, 220))

    # --- distant headland, left horizon --------------------------------------
    d.polygon([(0, 660), (0, 600), (90, 622), (190, 596), (300, 628),
               (360, 640), (360, 660)], fill=(58, 42, 92, 255))

    # --- sea -----------------------------------------------------------------
    vgrad(d, 0, 660, W, H, [(0.0, SEA_TOP), (1.0, SEA_DEEP)])
    # sun path: sparse shimmering strokes under the sun, fading with depth
    import math
    for i in range(34):
        yy = 672 + i * 9
        t = i / 33
        half = (18 + i * 2.2) * (0.55 + 0.45 * abs(math.sin(i * 2.3)))
        wob = math.sin(i * 1.7) * 16
        x0 = sun_x - half + wob
        x1 = sun_x + half + wob
        a = int(max(0, 190 - i * 5.5))
        d.line([(x0, yy), (x1, yy)], fill=(255, 205, 130, a), width=2)
    # a few calm wave lines
    for (wx, wy, wl) in [(120, 760, 90), (700, 800, 130), (880, 900, 110),
                         (240, 920, 120), (560, 950, 150), (60, 860, 80)]:
        d.line([(wx, wy), (wx + wl, wy)], fill=(140, 210, 205, 90), width=2)

    # --- sailboat, small, on the sun path ------------------------------------
    bx, by = 250, 800
    d.polygon([(bx - 34, by), (bx + 34, by), (bx, by + 12)],
              fill=(30, 24, 58, 255))
    d.line([(bx, by), (bx, by - 62)], fill=(30, 24, 58, 255), width=3)
    d.polygon([(bx + 3, by - 60), (bx + 3, by - 6), (bx + 42, by - 6)],
              fill=(255, 236, 200, 255))
    d.polygon([(bx - 3, by - 52), (bx - 3, by - 6), (bx - 30, by - 6)],
              fill=(255, 205, 140, 255))

    # --- the islet and the glass lighthouse ----------------------------------
    # rocky islet, centre-right, rising from the sea
    d.polygon([(560, 700), (620, 668), (700, 652), (800, 660), (880, 690),
               (900, 700), (560, 700)], fill=ROCK + (255,))
    d.polygon([(600, 690), (660, 664), (760, 656), (830, 676), (860, 692),
               (620, 694)], fill=(52, 40, 78, 255))
    # warm rim light on the islet's sun-facing edge
    d.line([(600, 690), (660, 664), (700, 656)], fill=(255, 190, 130, 170),
           width=3)
    # dark waterline shadow under the islet
    d.ellipse([560, 694, 900, 716], fill=(6, 40, 62, 160))

    # glass tower: tapered, faceted, catching the sunset
    tx = 730  # tower centre x
    base_y, top_y = 668, 470
    bw, tw = 34, 16  # half-widths at base and top
    # right facet (deep blue glass)
    d.polygon([(tx, top_y), (tx + tw, top_y), (tx + bw, base_y),
               (tx, base_y)], fill=(58, 130, 168, 255))
    # left facet (pale glass, sunlit)
    d.polygon([(tx, top_y), (tx - tw, top_y), (tx - bw, base_y),
               (tx, base_y)], fill=(150, 215, 225, 255))
    # centre spine of light
    d.polygon([(tx - 5, top_y), (tx + 5, top_y), (tx + 8, base_y),
               (tx - 8, base_y)], fill=(235, 250, 250, 255))
    # horizontal glass bands
    for fy in (520, 565, 610):
        t = (fy - top_y) / (base_y - top_y)
        hw = tw + (bw - tw) * t
        d.line([(tx - hw, fy), (tx + hw, fy)], fill=(255, 255, 255, 130),
               width=2)
    # gallery + lamp room
    d.rectangle([tx - 26, 452, tx + 26, 470], fill=(30, 26, 56, 255))
    d.rectangle([tx - 20, 420, tx + 20, 452], fill=(255, 214, 130, 255))
    d.rectangle([tx - 20, 420, tx + 20, 452], outline=(255, 244, 200, 255),
                width=2)
    d.line([(tx - 20, 436), (tx + 20, 436)], fill=(255, 244, 200, 255), width=2)
    # dome
    d.pieslice([tx - 22, 396, tx + 22, 440], 180, 360, fill=(30, 26, 56, 255))
    d.line([(tx, 392), (tx, 384)], fill=(30, 26, 56, 255), width=3)
    d.ellipse([tx - 3, 380, tx + 3, 386], fill=(255, 214, 130, 255))
    # lamp glow + beams
    glow(img, tx, 436, 120, (255, 210, 120), 120)
    d = ImageDraw.Draw(img)
    beam(img, tx, 436, 1024, 400, 26, (255, 220, 140), 70)
    beam(img, tx, 436, 0, 470, 20, (255, 220, 140), 45)
    d = ImageDraw.Draw(img)

    # --- foreground cliffs framing the bottom corners ------------------------
    d.polygon([(0, 1024), (0, 900), (70, 940), (150, 916), (210, 962),
               (180, 1024)], fill=CLIFF + (255,))
    d.polygon([(1024, 1024), (1024, 910), (950, 946), (880, 922),
               (830, 968), (860, 1024)], fill=CLIFF + (255,))
    # a lone pine on the left cliff
    d.polygon([(96, 946), (116, 946), (106, 900)], fill=(16, 18, 44, 255))
    d.polygon([(92, 922), (120, 922), (106, 884)], fill=(16, 18, 44, 255))
    d.line([(106, 946), (106, 958)], fill=(16, 18, 44, 255), width=4)

    # --- title ---------------------------------------------------------------
    serif = ImageFont.truetype(os.path.join(HERE, "fonts", "DejaVuSerif-Bold.ttf"), 118)
    sans = ImageFont.truetype(os.path.join(HERE, "fonts", "DejaVuSans.ttf"), 30)
    tracked_text(d, W // 2, 92, "VELMARA", serif, CREAM + (255,),
                 tracking=26, shadow=(20, 16, 52, 200))
    # thin gold rule under the name
    d.line([(W // 2 - 130, 236), (W // 2 + 130, 236)], fill=GOLD + (255,),
           width=3)
    tracked_text(d, W // 2, 256, "ISLES OF THE GLASS TIDE", sans,
                 (255, 232, 196, 255), tracking=10,
                 shadow=(20, 16, 52, 180))

    img.convert("RGB").save(OUT, "PNG", optimize=True)


if __name__ == "__main__":
    main()
