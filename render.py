#!/usr/bin/env python3
"""Render the news-image-20261120 front page: 1024x1024, deterministic.

Reads stories.json from this directory and draws a broadsheet front page
with PIL only. No time, randomness, or network calls anywhere, so running
this script twice produces byte-identical output.
"""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1024, 1024
MARGIN = 34
CW = W - 2 * MARGIN  # 956

PAPER = (250, 244, 230)
INK = (26, 22, 18)
RED = (176, 32, 24)
BLUE = (28, 58, 110)
GREY = (112, 102, 90)
FAINT = (198, 188, 172)
LAND = (238, 230, 208)
MAP_FILL = (188, 204, 218)
MAP_EDGE = (96, 110, 124)
NIGHT = (24, 30, 58)
GOLD = (232, 190, 90)
WHITE = (255, 252, 246)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def trunc(d, text, fnt, max_w):
    if d.textlength(text, font=fnt) <= max_w:
        return text
    while text and d.textlength(text + "…", font=fnt) > max_w:
        text = text[:-1]
    return text + "…"


def draw_wrapped(d, x, y, text, fnt, max_w, fill, lh, max_lines=None):
    lines = wrap(d, text, fnt, max_w)
    cut = False
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        cut = True
    for i, ln in enumerate(lines):
        if cut and i == len(lines) - 1:
            ln = trunc(d, ln, fnt, max_w)
        d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def tracked(d, x, y, text, fnt, fill, tracking=2):
    """Draw text with extra space between letters (small-caps headings)."""
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=fnt, fill=fill)
        cx += d.textlength(ch, font=fnt) + tracking
    return cx


def rule(d, x, y, w, weight=1, fill=INK):
    d.rectangle([x, y, x + w - 1, y + weight - 1], fill=fill)


def section_head(d, x, y, text, w):
    fnt = font(F_SANS_B, 12)
    tracked(d, x, y + 1, text, fnt, INK, tracking=2)
    tw = sum(d.textlength(c, font=fnt) + 2 for c in text)
    rule(d, x + tw + 10, y + 6, w - tw - 10, 1, FAINT)
    return y + 15


# ---------------------------------------------------------------- illustrations
# Every illustration is drawn in the same flat engraving style: ink outlines,
# hatch lines, paper fills, and a single red or blue accent at most.

def art_cyclone(d, x, y, w, h):
    # Sea hatching on the left, land on the right, spiral storm above.
    for yy in range(y + 8, y + h - 26, 7):
        d.line([(x + 6, yy), (x + int(w * 0.42), yy)], fill=FAINT, width=1)
    coast = [(x + int(w * 0.55), y + h - 4), (x + int(w * 0.62), y + int(h * 0.62)),
             (x + int(w * 0.74), y + int(h * 0.45)), (x + int(w * 0.88), y + int(h * 0.30)),
             (x + w - 4, y + int(h * 0.22))]
    land = coast + [(x + w - 4, y + h - 4)]
    d.polygon(land, fill=LAND)
    d.line(coast, fill=INK, width=2, joint="curve")
    cx, cy = x + int(w * 0.40), y + int(h * 0.42)
    for r in (8, 16, 24, 32, 40, 48):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=25 + r * 6,
              end=25 + r * 6 + 285, fill=INK, width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
    for i in range(5):
        rx = x + int(w * 0.60) + i * 12
        d.line([(rx, y + h - 22), (rx - 5, y + h - 12)], fill=BLUE, width=1)


def art_podium(d, x, y, w, h):
    cx = x + w // 2
    # Calendar page marked 2027, floating above the lectern.
    px, py, pw, ph = x + int(w * 0.56), y + 6, int(w * 0.38), 34
    d.rectangle([px, py, px + pw, py + ph], fill=WHITE, outline=INK, width=2)
    d.ellipse([px + 8, py - 3, px + 14, py + 3], fill=INK)
    d.ellipse([px + pw - 14, py - 3, px + pw - 8, py + 3], fill=INK)
    fnt = font(F_SERIF_B, 15)
    d.text((px + pw / 2, py + ph / 2 + 1), "2027", font=fnt, fill=RED, anchor="mm")
    # Lectern with a microphone.
    d.polygon([(cx - 30, y + h - 6), (cx + 30, y + h - 6), (cx + 22, y + h - 50),
               (cx - 22, y + h - 50)], fill=(225, 215, 195), outline=INK)
    d.line([(cx - 12, y + h - 50), (cx - 24, y + h - 68)], fill=INK, width=2)
    d.ellipse([cx - 29, y + h - 75, cx - 19, y + h - 65], fill=INK)
    d.line([(cx - 18, y + h - 58), (cx + 18, y + h - 58)], fill=INK, width=1)
    d.line([(cx - 14, y + h - 64), (cx + 14, y + h - 64)], fill=INK, width=1)


def art_missile(d, x, y, w, h):
    # Stepped tower with a missile streaking in from the upper left.
    tx, tw = x + int(w * 0.46), int(w * 0.18)
    d.rectangle([tx, y + int(h * 0.34), tx + tw, y + h - 6], fill=(210, 200, 180),
                outline=INK, width=2)
    d.rectangle([tx + 6, y + int(h * 0.26), tx + tw - 6, y + int(h * 0.34)],
                fill=(210, 200, 180), outline=INK, width=2)
    for r in range(5):
        for c in range(3):
            wx = tx + 6 + c * (tw // 3)
            wy = y + int(h * 0.40) + r * 10
            d.rectangle([wx, wy, wx + 3, wy + 4], fill=INK)
    mx, my = x + int(w * 0.14), y + int(h * 0.14)
    d.line([(mx, my), (tx - 6, y + int(h * 0.30))], fill=INK, width=3)
    d.polygon([(mx - 4, my + 6), (mx + 10, my - 2), (mx + 4, my - 8)],
              fill=RED)
    for i, (sx, sy) in enumerate([(0.72, 0.30), (0.80, 0.24), (0.68, 0.20)]):
        px, py = x + int(w * sx), y + int(h * sy)
        d.ellipse([px - 4 - i, py - 4 - i, px + 4 + i, py + 4 + i], outline=GREY, width=1)
    d.line([(x + 4, y + h - 6), (x + w - 4, y + h - 6)], fill=INK, width=2)


def art_courthouse(d, x, y, w, h):
    # Pediment, four columns, steps, and the scales set into the pediment.
    d.polygon([(x + int(w * 0.06), y + int(h * 0.34)), (x + int(w * 0.94), y + int(h * 0.34)),
               (x + w // 2, y + int(h * 0.06))], fill=(225, 215, 195), outline=INK)
    for i in range(4):
        cx = x + int(w * (0.16 + i * 0.23))
        d.rectangle([cx, y + int(h * 0.38), cx + int(w * 0.07), y + int(h * 0.86)],
                    fill=WHITE, outline=INK, width=2)
    for i in range(3):
        yy = y + int(h * (0.88 + i * 0.04))
        d.line([(x + int(w * 0.06), yy), (x + int(w * 0.94), yy)], fill=INK, width=2)
    cx, cy = x + w // 2, y + int(h * 0.20)
    d.line([(cx, cy - 6), (cx, cy + 8)], fill=INK, width=2)
    d.line([(cx - 12, cy - 2), (cx + 12, cy - 2)], fill=INK, width=2)
    d.arc([cx - 17, cy - 2, cx - 7, cy + 10], start=0, end=180, fill=INK, width=2)
    d.arc([cx + 7, cy - 2, cx + 17, cy + 10], start=0, end=180, fill=INK, width=2)


def art_table(d, x, y, w, h):
    # Skyline behind, one long table, three figures seated at it.
    tops = [(0.04, 0.34), (0.20, 0.22), (0.36, 0.30), (0.52, 0.18), (0.68, 0.28),
            (0.82, 0.36)]
    for fx, ft in tops:
        bx = x + int(w * fx)
        bw = int(w * 0.13)
        d.rectangle([bx, y + int(h * ft), bx + bw, y + int(h * 0.62)],
                    fill=(205, 195, 175), outline=INK, width=1)
    ty = y + int(h * 0.62)
    d.line([(x + int(w * 0.08), ty), (x + int(w * 0.92), ty)], fill=INK, width=3)
    d.line([(x + int(w * 0.16), ty), (x + int(w * 0.16), y + h - 4)], fill=INK, width=2)
    d.line([(x + int(w * 0.84), ty), (x + int(w * 0.84), y + h - 4)], fill=INK, width=2)
    for fx in (0.26, 0.50, 0.74):
        hx = x + int(w * fx)
        hy = y + int(h * 0.44)
        d.ellipse([hx - 8, hy - 8, hx + 8, hy + 8], fill=INK)
        d.polygon([(hx - 16, ty), (hx + 16, ty), (hx + 10, hy + 10),
                   (hx - 10, hy + 10)], fill=INK)


def art_voyager(d, x, y, w, h):
    stars = [(0.10, 0.16), (0.30, 0.08), (0.56, 0.18), (0.82, 0.10),
             (0.90, 0.38), (0.14, 0.52), (0.68, 0.58), (0.44, 0.06)]
    for fx, fy in stars:
        sx, sy = x + int(w * fx), y + int(h * fy)
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=INK)
    sx, sy = x + int(w * 0.72), y + int(h * 0.30)
    d.line([(sx - 5, sy), (sx + 5, sy)], fill=INK, width=1)
    d.line([(sx, sy - 5), (sx, sy + 5)], fill=INK, width=1)
    # Dashed trajectory arc sweeping up to the right.
    for a in range(200, 340, 12):
        d.arc([x - int(w * 0.10), y - int(h * 0.10), x + int(w * 1.05),
               y + int(h * 1.30)], start=a, end=a + 7, fill=BLUE, width=2)
    fnt = font(F_SANS_B, 9)
    d.text((x + w - 4, y + 4), "1 light-day", font=fnt, fill=BLUE, anchor="ra")
    # The probe: dish, body, boom, power unit.
    px, py = x + int(w * 0.30), y + int(h * 0.55)
    d.arc([px - 22, py - 26, px + 6, py + 2], start=270, end=90, fill=INK, width=2)
    d.line([(px - 8, py - 12), (px + 14, py - 4)], fill=INK, width=2)
    d.rectangle([px + 12, py - 12, px + 30, py + 4], fill=WHITE, outline=INK, width=2)
    d.line([(px + 30, py - 4), (px + 48, py - 12)], fill=INK, width=2)
    d.rectangle([px + 46, py - 18, px + 56, py - 6], fill=INK)


def art_neon(d, x, y, w, h):
    # Night city: dark sky, lit windows, neon strips.
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    mx, my = x + int(w * 0.82), y + int(h * 0.14)
    d.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=WHITE)
    d.ellipse([mx - 3, my - 7, mx + 5, my + 7], fill=NIGHT)
    builds = [(0.02, 0.42, 0.20), (0.24, 0.28, 0.22), (0.48, 0.36, 0.20),
              (0.70, 0.24, 0.28)]
    for fx, ft, fw in builds:
        bx = x + int(w * fx)
        bw = int(w * fw)
        top = y + int(h * ft)
        d.rectangle([bx, top, bx + bw, y + h], fill=(14, 18, 40),
                    outline=(64, 74, 116), width=1)
        for r in range(4):
            for c in range(3):
                wx = bx + 5 + c * (bw // 3)
                wy = top + 8 + r * 12
                col = GOLD if (r + c) % 3 else (150, 200, 240)
                d.rectangle([wx, wy, wx + 5, wy + 6], fill=col)
    ny = y + int(h * 0.62)
    d.line([(x + int(w * 0.26), ny), (x + int(w * 0.44), ny)], fill=RED, width=3)
    d.line([(x + int(w * 0.50), ny + 8), (x + int(w * 0.66), ny + 8)], fill=(80, 140, 255),
           width=3)
    d.line([(x, y + h - 3), (x + w, y + h - 3)], fill=GOLD, width=2)


def art_batsman(d, x, y, w, h):
    d.line([(x + 4, y + h - 6), (x + w - 4, y + h - 6)], fill=INK, width=2)
    # Stumps at the right.
    for i in range(3):
        sx = x + int(w * (0.78 + i * 0.035))
        d.line([(sx, y + int(h * 0.62)), (sx, y + h - 6)], fill=INK, width=2)
    d.line([(x + int(w * 0.78), y + int(h * 0.60)),
            (x + int(w * 0.85), y + int(h * 0.60))], fill=INK, width=2)
    # Batsman: head, torso, legs, arms and bat.
    hx, hy = x + int(w * 0.42), y + int(h * 0.30)
    d.ellipse([hx - 8, hy - 8, hx + 8, hy + 8], fill=INK)
    d.line([(hx, hy + 8), (hx - 4, y + int(h * 0.62))], fill=INK, width=3)
    d.line([(hx - 4, y + int(h * 0.62)), (hx - 18, y + h - 8)], fill=INK, width=3)
    d.line([(hx - 4, y + int(h * 0.62)), (hx + 12, y + h - 8)], fill=INK, width=3)
    d.line([(hx, hy + 14), (hx + 16, y + int(h * 0.52))], fill=INK, width=3)
    d.polygon([(hx + 14, y + int(h * 0.50)), (hx + 26, y + int(h * 0.66)),
               (hx + 20, y + int(h * 0.70)), (hx + 8, y + int(h * 0.56))],
              fill=(225, 215, 195), outline=INK)
    bx, by = x + int(w * 0.62), y + int(h * 0.72)
    d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=RED)
    d.line([(bx - 12, by - 2), (bx - 6, by - 1)], fill=RED, width=1)
    d.line([(bx - 12, by + 3), (bx - 6, by + 2)], fill=RED, width=1)


def art_probe(d, x, y, w, h):
    # Hayabusa2: lumpy asteroid, small probe, dashed approach, engine sputter.
    pts = [(0.55, 0.30), (0.72, 0.26), (0.88, 0.38), (0.92, 0.58),
           (0.80, 0.74), (0.62, 0.72), (0.52, 0.52)]
    poly = [(x + int(w * fx), y + int(h * fy)) for fx, fy in pts]
    d.polygon(poly, fill=(200, 190, 170), outline=INK)
    for fx, fy, r in [(0.68, 0.45, 4), (0.78, 0.58, 3), (0.64, 0.60, 2)]:
        cx, cy = x + int(w * fx), y + int(h * fy)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=1)
    px, py = x + int(w * 0.20), y + int(h * 0.30)
    d.rectangle([px - 8, py - 6, px + 8, py + 6], fill=WHITE, outline=INK, width=2)
    d.rectangle([px - 22, py - 4, px - 8, py + 4], fill=MAP_FILL, outline=INK, width=1)
    d.rectangle([px + 8, py - 4, px + 22, py + 4], fill=MAP_FILL, outline=INK, width=1)
    for i in range(6):
        t = i / 5
        lx = int(px + 14 + t * (w * 0.42))
        ly = int(py + 8 + t * (h * 0.30))
        d.line([(lx, ly), (lx + 7, ly + 4)], fill=GREY, width=1)
    ex, ey = x + int(w * 0.14), y + int(h * 0.38)
    d.line([(ex - 5, ey - 5), (ex + 5, ey + 5)], fill=RED, width=2)
    d.line([(ex - 5, ey + 5), (ex + 5, ey - 5)], fill=RED, width=2)


def art_bars(d, x, y, w, h):
    # Anthropic debut: three rising bars, a red arrow, the $81bn label.
    fnt = font(F_SANS_B, 12)
    d.text((x + w - 2, y + 2), "$81bn", font=fnt, fill=BLUE, anchor="ra")
    ox, oy = x + 10, y + h - 14
    d.line([(ox, oy), (ox, y + 16)], fill=INK, width=2)
    d.line([(ox, oy), (x + w - 6, oy)], fill=INK, width=2)
    heights = (0.30, 0.48, 0.68)
    for i, fh in enumerate(heights):
        bx = ox + 14 + i * int(w * 0.26)
        bw = int(w * 0.18)
        top = oy - int(h * fh)
        fill = BLUE if i == 2 else (190, 180, 158)
        d.rectangle([bx, top, bx + bw, oy], fill=fill, outline=INK, width=1)
    d.line([(ox + 8, oy - int(h * 0.18)), (x + w - 16, y + int(h * 0.16))],
           fill=RED, width=2)
    d.polygon([(x + w - 16, y + int(h * 0.16)), (x + w - 26, y + int(h * 0.14)),
               (x + w - 18, y + int(h * 0.26))], fill=RED)


ART = {"cyclone": art_cyclone, "podium": art_podium, "missile": art_missile,
       "courthouse": art_courthouse, "table": art_table, "voyager": art_voyager,
       "neon": art_neon, "batsman": art_batsman, "probe": art_probe,
       "bars": art_bars}

# ---------------------------------------------------------------- world map

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-150, 60)],
    # South America
    [(-80, 10), (-60, 8), (-50, 0), (-40, -5), (-35, -10), (-40, -20),
     (-50, -30), (-60, -40), (-70, -55), (-73, -40), (-70, -20), (-80, -5)],
    # Europe
    [(-10, 36), (0, 38), (10, 38), (20, 40), (28, 36), (30, 42), (25, 45),
     (20, 45), (12, 44), (5, 43), (-2, 48), (-5, 50), (-10, 52), (-5, 58),
     (0, 60), (5, 58), (10, 57), (18, 56), (21, 55), (28, 60), (30, 65),
     (25, 70), (18, 70), (12, 68), (5, 60)],
    # Africa
    [(-6, 35), (10, 37), (20, 32), (30, 31), (35, 28), (40, 15), (48, 11),
     (51, 10), (45, 0), (40, -10), (35, -20), (30, -30), (20, -35), (15, -30),
     (12, -18), (8, -2), (0, 5), (-8, 5), (-15, 12), (-17, 15)],
    # Asia
    [(30, 70), (40, 68), (60, 70), (80, 73), (100, 77), (120, 73), (140, 72),
     (160, 70), (178, 66), (170, 60), (160, 55), (150, 45), (140, 40),
     (130, 35), (127, 35), (122, 30), (120, 25), (110, 20), (105, 10),
     (100, 8), (95, 15), (90, 22), (85, 20), (80, 15), (77, 8), (75, 12),
     (70, 20), (65, 25), (60, 25), (55, 26), (50, 28), (48, 30), (45, 28),
     (40, 35), (35, 36), (30, 36), (30, 42), (35, 45), (40, 48), (45, 50),
     (50, 55), (55, 60), (60, 65), (55, 68), (45, 68)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (150, -22),
     (146, -19), (142, -15), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20)],
]

PINS = [
    (85.5, 19.8, 1, "Odisha", 0, 0),
    (46.7, 24.7, 2, "Riyadh", 0, 0),
    (4.3, 52.1, 3, "The Hague", 0, 0),
    (114.1, 22.5, 4, "Shenzhen", 0, 0),
    (174.8, -41.3, 5, "Wellington", 0, 0),
    (127.0, 37.5, 6, "Seoul", 14, 12),
    (178.4, -18.1, 7, "Suva", 0, 0),
    (-66.9, 10.5, 8, "Caracas", 0, 0),
    (125.8, 39.0, 9, "Pyongyang", -16, -14),
    (-77.0, 38.9, 10, "Washington", 0, 0),
]


def project(lon, lat, box):
    bx, by, bw, bh = box
    px = bx + (lon + 180.0) / 360.0 * bw
    py = by + (85.0 - lat) / 145.0 * bh
    return px, py


def draw_map(d, x, y, w, h):
    box = (x, y, w, h)
    d.rectangle([x, y, x + w, y + h], outline=MAP_EDGE, width=1)
    # Faint equator line for orientation.
    _, ey = project(0, 0, box)
    for xx in range(x, x + w, 10):
        d.line([(xx, ey), (xx + 5, ey)], fill=FAINT, width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat, box) for lon, lat in poly]
        d.polygon(pts, fill=MAP_FILL, outline=MAP_EDGE)
    fnt = font(F_SANS_B, 10)
    for lon, lat, n, _label, dx, dy in PINS:
        px, py = project(lon, lat, box)
        cx = max(x + 10, min(x + w - 10, px + dx))
        cy = max(y + 10, min(y + h - 10, py + dy))
        if dx or dy:
            d.line([(px, py), (cx, cy)], fill=RED, width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED,
                  outline=WHITE, width=1)
        d.text((cx, cy), str(n), font=fnt, fill=WHITE, anchor="mm")


# ---------------------------------------------------------------- page build

def main():
    stories = json.loads((HERE / "stories.json").read_text())
    assert len(stories["lead"]) == 5
    assert len(stories["panels"]) == 4
    assert len(stories["columns"]) == 25
    assert len(stories["briefs"]) == 20  # 17 briefs (35-51) + 28/33/34, which run here, not in the columns
    assert len(stories["numbers"]) == 8

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 14

    # (1) Masthead.
    f_title = font(F_SERIF_B, 36)
    d.text((W // 2, y), "THE WORLD IN ONE DAY", font=f_title, fill=INK,
           anchor="ma")
    y += 42
    f_date = font(F_SERIF, 13)
    d.text((W // 2, y), "Friday 20 November 2026  ·  52 stories  ·  one page",
           font=f_date, fill=INK, anchor="ma")
    y += 19
    rule(d, MARGIN, y, CW, 3)
    rule(d, MARGIN, y + 5, CW, 1)
    y += 9

    # (2) Lead story, full width, large illustration on the right.
    lead = stories["lead"][0]
    art_w, art_h = 290, 84
    ax, ay = W - MARGIN - art_w, y
    ART[lead["art"]](d, ax, ay, art_w, art_h)
    tx = MARGIN
    tw = CW - art_w - 22
    f_kick = font(F_SANS_B, 10)
    d.text((tx, y), lead["kicker"], font=f_kick, fill=RED)
    y += 14
    f_head = font(F_SERIF_B, 28)
    d.text((tx, y), lead["headline"], font=f_head, fill=INK)
    y += 33
    f_deck = font(F_SANS, 12)
    y = draw_wrapped(d, tx, y, lead["deck"], f_deck, tw, INK, 14)
    y = max(y, ay + art_h) + 8
    rule(d, MARGIN, y, CW, 1)
    y += 7

    # (3) Row of four illustrated panels: stories 2-5.
    def panel_row(items, y, art_h, head_size, head_lh, deck_lines):
        n = len(items)
        gap = 12
        pw = (CW - gap * (n - 1)) // n
        row_bottom = y
        for i, it in enumerate(items):
            px = MARGIN + i * (pw + gap)
            ART[it["art"]](d, px, y, pw, art_h)
            yy = y + art_h + 4
            f_k = font(F_SANS_B, 9)
            d.text((px, yy), it["kicker"], font=f_k, fill=RED)
            yy += 12
            f_h = font(F_SERIF_B, head_size)
            yy = draw_wrapped(d, px, yy, it["headline"], f_h, pw, INK,
                              head_lh, max_lines=2)
            yy += 2
            f_d = font(F_SANS, 11)
            yy = draw_wrapped(d, px, yy, it["deck"], f_d, pw, GREY, 12,
                              max_lines=deck_lines)
            row_bottom = max(row_bottom, yy)
        return row_bottom

    y = panel_row(stories["lead"][1:], y, 52, 16, 17, 2)
    y += 5
    rule(d, MARGIN, y, CW, 1)
    y += 7

    # (4) World map strip with ten numbered pins.
    y = section_head(d, MARGIN, y, "THE WORLD TODAY", CW)
    map_h = 62
    draw_map(d, MARGIN, y, CW, map_h)
    y += map_h + 4
    f_leg = font(F_SANS, 10)
    legend = "  ·  ".join(f"{n} {label}" for _lon, _lat, n, label, _dx, _dy
                          in PINS)
    d.text((W // 2, y), legend, font=f_leg, fill=GREY, anchor="ma")
    y += 12
    rule(d, MARGIN, y, CW, 1)
    y += 7

    # (5) Three columns of headline + deck stories.
    # Story 30 is featured as an illustrated panel below, and stories 28,
    # 33 and 34 run as one-line briefs, so none of them is repeated here.
    cols = [c for c in stories["columns"] if c["n"] not in (28, 30, 33, 34)]
    assert len(cols) == 21
    col_gap = 13
    col_w = (CW - 2 * col_gap) // 3
    f_ch = font(F_SERIF_B, 14)
    f_cd = font(F_SANS, 11)
    col_bottom = y
    for ci in range(3):
        cx = MARGIN + ci * (col_w + col_gap)
        yy = y
        for it in cols[ci * 7:(ci + 1) * 7]:
            yy = draw_wrapped(d, cx, yy, it["headline"], f_ch, col_w, INK,
                              14, max_lines=2)
            deck = trunc(d, it["deck"], f_cd, col_w)
            d.text((cx, yy), deck, font=f_cd, fill=GREY)
            yy += 11 + 1
        col_bottom = max(col_bottom, yy)
    y = col_bottom + 2
    rule(d, MARGIN, y, CW, 1)
    y += 7

    # (6) Row of five illustrated panels: Voyager, Hayabusa2, GTA 6,
    # Anthropic, and the cricket batsman (story 30).
    cricket = next(c for c in stories["columns"] if c["n"] == 30)
    panel6 = list(stories["panels"])
    panel6.insert(3, {"art": "batsman", "deck": cricket["deck"],
                      "headline": "Phillips 118, Nicholls 146*",
                      "kicker": "CRICKET", "n": 30})
    # Hayabusa2 and Anthropic need art keys of their own.
    panel6[1]["art"] = "probe"
    panel6[4]["art"] = "bars"
    y = panel_row(panel6, y, 50, 16, 17, 2)
    y += 5
    rule(d, MARGIN, y, CW, 1)
    y += 7

    # (7) The day in numbers.
    y = section_head(d, MARGIN, y, "THE DAY IN NUMBERS", CW)
    cell_w = CW // 8
    f_nv = font(F_SERIF_B, 16)
    f_nl = font(F_SANS, 9)
    for i, num in enumerate(stories["numbers"]):
        cx = MARGIN + i * cell_w + cell_w // 2
        d.text((cx, y), num["value"], font=f_nv, fill=RED, anchor="ma")
        d.text((cx, y + 18), num["label"], font=f_nl, fill=GREY, anchor="ma")
        if i:
            d.line([(MARGIN + i * cell_w, y + 2),
                    (MARGIN + i * cell_w, y + 26)], fill=FAINT, width=1)
    y += 26
    rule(d, MARGIN, y, CW, 1)
    y += 6

    # (8) Also today: one-line briefs in three columns.
    y = section_head(d, MARGIN, y, "ALSO TODAY", CW)
    briefs = stories["briefs"]
    per = 7
    f_b = font(F_SANS, 11)
    for ci in range(3):
        cx = MARGIN + ci * (col_w + col_gap)
        yy = y
        for it in briefs[ci * per:(ci + 1) * per]:
            d.rectangle([cx, yy + 4, cx + 4, yy + 8], fill=RED)
            txt = trunc(d, it["text"], f_b, col_w - 10)
            d.text((cx + 10, yy), txt, font=f_b, fill=INK)
            yy += 12
    y += per * 12 + 4
    rule(d, MARGIN, y, CW, 1)
    y += 6

    # (9) Footer.
    f_f = font(F_SANS, 10)
    d.text((W // 2, y), "Sources: " + stories["sources"], font=f_f,
           fill=GREY, anchor="ma")
    y += 12

    print(f"final_y={y} (page height {H})")
    assert y <= H, f"layout overflow: final_y {y} > {H}"
    out = HERE / "entry.png"
    img.save(out, format="PNG")
    data = out.read_bytes()
    print(f"entry.png: {len(data)} bytes, "
          f"sha256={hashlib.sha256(data).hexdigest()}")
    assert len(data) <= 1_048_576, "entry.png exceeds 1 MiB"


if __name__ == "__main__":
    main()
