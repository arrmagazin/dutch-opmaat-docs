#!/usr/bin/env python3
"""Generate one illustration per item in data/speaking.json.

Each A2 speaking prompt gets a flat-vector scene at images/speaking/<id>.svg,
styled like the existing per-topic images/<topic>.svg: 800x600, rounded frame,
topic gradient background, white cards holding the pictograms, topic caption.

Prompts ending in "Gebruik alle plaatjes" ("use all the pictures") are drawn as
a numbered three-panel strip, the way the real exam presents them. Two-way
choice prompts get two panels; the rest a single scene.

Run: python3 scripts/gen_speaking_images.py
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "images", "speaking")
DATA = os.path.join(ROOT, "data", "speaking.json")

W, H = 800, 600

# Background gradient + caption colour per topic, matching images/<topic>.svg.
TOPICS = {
    "body-and-health": ("#ffecec", "#ffbcbc", "#b02a2a"),
    "daily-routines": ("#fff7e0", "#ffe08a", "#9a6b12"),
    "dutch-culture-and-traditions": ("#fff2df", "#ffce8f", "#a55f10"),
    "family": ("#fff0ec", "#ffc9b8", "#a8412a"),
    "food-and-shopping": ("#eafaef", "#b4e6bf", "#2f7d43"),
    "free-time": ("#e3f7f4", "#a7e6dc", "#1d6f63"),
    "friends": ("#ffeef6", "#ffc2df", "#b23070"),
    "home-and-living": ("#fbeee2", "#e8c3a0", "#8a5320"),
    "job-and-workplace": ("#eaf0fb", "#b9c8ec", "#2f4a86"),
    "learning-dutch": ("#fff1e2", "#ffcf9e", "#a85a10"),
    "life-in-the-netherlands": ("#e6f0fb", "#aecbee", "#264f86"),
    "money-and-prices": ("#e6f7ee", "#a7e3c4", "#1c7a4d"),
    "personal-introduction": ("#eef0ff", "#c9cdff", "#3a3d8f"),
    "technology": ("#e9ecfb", "#b7bff0", "#37409a"),
    "transportation": ("#e3f6fb", "#a5dcec", "#1a6d86"),
    "travel": ("#e4f2fe", "#a9d4f7", "#1c5f9e"),
    "weather-and-seasons": ("#e6f4ff", "#aad4f5", "#1f6aa8"),
}

# Object colours. Pictograms keep natural colours so they read the same on any
# topic background; only the frame and caption follow the topic palette.
INK = "#33404f"
LINE = "#5b6b7d"
SKIN = "#f0c49b"
SKIN_D = "#d09a6d"
HAIR = "#3c2f2a"
HAIR_L = "#8a5a2b"
WHITE = "#ffffff"
RED = "#e0483d"
ORANGE = "#f28c28"
YELLOW = "#f7c948"
GREEN = "#4caf50"
GREEN_D = "#2e7d32"
BLUE = "#3f7fd0"
BLUE_D = "#2a5da8"
TEAL = "#2fa899"
PURPLE = "#8e6ac4"
PINK = "#e87fa8"
BROWN = "#8d6042"
BROWN_D = "#6b4630"
GREY = "#9aa5b1"
GREY_L = "#d6dee7"
GREY_D = "#68757f"
SKY = "#8ecdf0"
WATER = "#4aa3d8"
SAND = "#f0dca8"
CREAM = "#f7ecd4"


# --------------------------------------------------------------------------
# primitives — all icons draw inside a 0..100 box
# --------------------------------------------------------------------------


def rect(x, y, w, h, fill, rx=0, stroke=None, sw=2):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    r = f' rx="{rx}"' if rx else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}"{r} fill="{fill}"{s}/>'


def circ(cx, cy, r, fill, stroke=None, sw=2):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{s}/>'


def ell(cx, cy, rx, ry, fill, stroke=None, sw=2):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"{s}/>'


def path(d, fill="none", stroke=None, sw=3, cap="round"):
    s = f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}" stroke-linejoin="round"' if stroke else ""
    return f'<path d="{d}" fill="{fill}"{s}/>'


def line(x1, y1, x2, y2, stroke=LINE, sw=3):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}"'
        f' stroke-width="{sw}" stroke-linecap="round"/>'
    )


def poly(points, fill, stroke=None, sw=2):
    pts = " ".join(f"{x},{y}" for x, y in points)
    s = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"' if stroke else ""
    return f'<polygon points="{pts}" fill="{fill}"{s}/>'


def grp(body, tx=0, ty=0, s=1, rot=None, ox=50, oy=50):
    t = f"translate({tx},{ty}) scale({s})"
    if rot:
        t += f" rotate({rot},{ox},{oy})"
    return f'<g transform="{t}">{body}</g>'


def label(text, x=50, y=95, size=13, fill=INK, weight="700"):
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}"'
        f' font-weight="{weight}" fill="{fill}">{esc(text)}</text>'
    )


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def head(cx, cy, r, skin=SKIN, hair=HAIR, hat=None):
    out = circ(cx, cy, r, skin)
    out += path(
        f"M {cx - r} {cy - r * 0.15} a {r} {r} 0 0 1 {2 * r} 0 "
        f"a {r} {r * 0.7} 0 0 0 {-2 * r} 0 Z",
        fill=hair,
    )
    if hat:
        out += path(
            f"M {cx - r * 1.25} {cy - r * 0.5} h {r * 2.5} l {-r * 0.35} {-r * 0.75} h {-r * 1.8} Z",
            fill=hat,
        )
    out += circ(cx - r * 0.35, cy + r * 0.12, r * 0.11, INK)
    out += circ(cx + r * 0.35, cy + r * 0.12, r * 0.11, INK)
    return out


def body(cx, top, w, h, color):
    """Torso with rounded shoulders."""
    return path(
        f"M {cx - w / 2} {top + h} L {cx - w / 2} {top + w * 0.35} "
        f"a {w / 2} {w * 0.4} 0 0 1 {w} 0 L {cx + w / 2} {top + h} Z",
        fill=color,
    )


def person(cx, top, scale=1.0, shirt=BLUE, skin=SKIN, hair=HAIR, hat=None, legs=True, pants=INK):
    """Standing figure; `top` is the crown of the head. ~46x62 at scale 1."""
    r = 11 * scale
    out = head(cx, top + r, r, skin, hair, hat)
    out += body(cx, top + 2 * r + 1 * scale, 30 * scale, 26 * scale, shirt)
    if legs:
        y0 = top + 2 * r + 27 * scale
        out += rect(cx - 12 * scale, y0, 9 * scale, 18 * scale, pants, rx=3 * scale)
        out += rect(cx + 3 * scale, y0, 9 * scale, 18 * scale, pants, rx=3 * scale)
    return out


# --------------------------------------------------------------------------
# icons
# --------------------------------------------------------------------------


def i_sun():
    out = "".join(
        line(50 + 30 * c, 50 + 30 * s, 50 + 42 * c, 50 + 42 * s, YELLOW, 6)
        for c, s in _dirs(8)
    )
    return out + circ(50, 50, 24, YELLOW)


def _dirs(n):
    import math

    return [(math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n)) for i in range(n)]


def i_cloud(fill=WHITE, y=44):
    return (
        ell(38, y + 4, 20, 15, fill)
        + ell(58, y, 22, 18, fill)
        + ell(70, y + 8, 15, 11, fill)
        + rect(30, y + 6, 50, 12, fill, rx=6)
    )


def i_rain():
    out = i_cloud(GREY_L, 34)
    for x in (34, 50, 66):
        out += line(x, 62, x - 5, 80, WATER, 5)
    return out


def i_snow():
    out = i_cloud("#e9f2f8", 32)
    out += path("M 20 40 q 8 -20 28 -14 q 14 -10 24 6 q 14 0 12 16", stroke=GREY, sw=4)
    for x, y in ((32, 70), (50, 78), (68, 70)):
        out += circ(x, y, 6, "#8fc9e8")
        out += line(x - 9, y, x + 9, y, "#5aa8d0", 3) + line(x, y - 9, x, y + 9, "#5aa8d0", 3)
    return out


def i_sun_cloud():
    return (
        "".join(line(70 + 20 * c, 30 + 20 * s, 70 + 30 * c, 30 + 30 * s, YELLOW, 5) for c, s in _dirs(8))
        + circ(70, 30, 16, YELLOW)
        + i_cloud("#eef4f8", 54)
        + path("M 20 62 q 8 -20 26 -14 q 12 -8 22 4 q 12 0 12 14", stroke=GREY, sw=4)
    )


def i_calendar():
    out = rect(16, 20, 68, 66, WHITE, rx=8, stroke=LINE, sw=3)
    out += rect(16, 20, 68, 18, RED, rx=8)
    out += rect(16, 32, 68, 6, RED)
    out += line(32, 12, 32, 26, INK, 5) + line(68, 12, 68, 26, INK, 5)
    for r in range(3):
        for c in range(4):
            out += rect(25 + c * 15, 46 + r * 13, 10, 8, GREY_L, rx=2)
    return out


def i_calendar_check():
    return i_calendar() + path("M 34 66 l 10 11 l 22 -25", stroke=GREEN_D, sw=8)


def i_clock(h=6, m=0):
    import math

    out = circ(50, 50, 36, WHITE, stroke=INK, sw=5)
    for i in range(12):
        a = 2 * math.pi * i / 12
        out += line(
            50 + 28 * math.sin(a), 50 - 28 * math.cos(a),
            50 + 32 * math.sin(a), 50 - 32 * math.cos(a), GREY, 3,
        )
    ah = 2 * math.pi * ((h % 12) + m / 60) / 12
    am = 2 * math.pi * m / 60
    out += line(50, 50, 50 + 18 * math.sin(ah), 50 - 18 * math.cos(ah), INK, 6)
    out += line(50, 50, 50 + 26 * math.sin(am), 50 - 26 * math.cos(am), INK, 4)
    return out + circ(50, 50, 4, RED)


def i_alarm():
    return (
        line(22, 18, 32, 26, INK, 6)
        + line(78, 18, 68, 26, INK, 6)
        + i_clock(6, 0)
    )


def i_hourglass():
    return (
        rect(26, 14, 48, 8, BROWN, rx=3)
        + rect(26, 78, 48, 8, BROWN, rx=3)
        + path("M 32 22 L 68 22 L 52 50 L 68 78 L 32 78 L 48 50 Z", fill=WHITE, stroke=INK, sw=3)
        + path("M 36 26 L 64 26 L 50 48 Z", fill=YELLOW)
        + path("M 38 74 L 62 74 L 50 60 Z", fill=YELLOW)
    )


# ---- people -------------------------------------------------------------


def i_family():
    return (
        person(28, 22, 0.95, BLUE)
        + person(58, 20, 1.0, PINK, hair=HAIR_L)
        + person(80, 46, 0.62, GREEN)
    )


def i_two_people():
    return person(34, 24, 1.05, BLUE) + person(68, 26, 1.0, ORANGE, hair=HAIR_L)


def i_mother_daughter():
    return person(36, 18, 1.15, PINK, hair=HAIR_L) + person(72, 48, 0.7, YELLOW)


def i_crowd():
    out = person(20, 34, 0.8, PURPLE) + person(50, 26, 0.9, BLUE) + person(80, 34, 0.8, TEAL)
    return out + person(35, 46, 0.7, ORANGE) + person(66, 46, 0.7, RED)


def i_friends_visit():
    return (
        rect(6, 40, 30, 52, BROWN, rx=4)
        + rect(12, 52, 18, 30, CREAM, rx=3)
        + person(58, 24, 1.05, PINK, hair=HAIR_L)
        + person(84, 30, 0.9, TEAL)
        + path("M 42 34 q 10 -12 22 -4", stroke=GREEN_D, sw=4)
    )


def i_neighbours():
    return (
        rect(4, 34, 40, 58, "#e07a5f", rx=4)
        + poly([(2, 36), (24, 16), (46, 36)], BROWN_D)
        + rect(56, 34, 40, 58, BLUE, rx=4)
        + poly([(54, 36), (76, 16), (98, 36)], BROWN_D)
        + person(24, 56, 0.62, YELLOW)
        + person(76, 56, 0.62, WHITE)
    )


def i_angry():
    out = circ(50, 50, 34, "#f3a3a3", stroke=RED, sw=4)
    out += line(30, 34, 44, 42, INK, 5) + line(70, 34, 56, 42, INK, 5)
    out += circ(38, 52, 5, INK) + circ(62, 52, 5, INK)
    out += path("M 34 76 q 16 -14 32 0", stroke=INK, sw=5)
    return out


def i_sleeping():
    out = rect(10, 56, 80, 26, BLUE, rx=6) + rect(6, 44, 22, 20, WHITE, rx=6)
    out += circ(38, 52, 11, SKIN) + path("M 27 48 a 11 11 0 0 1 22 0 Z", fill=HAIR)
    for i, (x, y, s) in enumerate(((62, 34, 12), (74, 22, 16), (88, 10, 20))):
        out += f'<text x="{x}" y="{y}" font-size="{s}" font-weight="800" fill="{BLUE_D}">z</text>'
    return out


def i_walking():
    return (
        head(50, 20, 11)
        + body(50, 32, 28, 24, ORANGE)
        + line(46, 56, 34, 84, INK, 8)
        + line(52, 56, 68, 82, INK, 8)
        + line(38, 40, 24, 52, ORANGE, 8)
        + line(62, 40, 76, 34, ORANGE, 8)
    )


def i_runner():
    return (
        head(58, 18, 11)
        + body(54, 30, 28, 22, RED)
        + line(48, 52, 30, 74, INK, 8)
        + line(56, 52, 74, 66, INK, 8)
        + line(30, 74, 22, 86, INK, 8)
        + line(42, 36, 24, 30, RED, 8)
        + line(66, 36, 82, 46, RED, 8)
    )


def i_swimmer():
    return (
        rect(0, 60, 100, 40, WATER, rx=6)
        + path("M 0 62 q 12 -8 24 0 t 24 0 t 24 0 t 24 0", stroke=WHITE, sw=4)
        + circ(38, 48, 12, SKIN)
        + path("M 26 44 a 12 12 0 0 1 24 0 Z", fill=RED)
        + path("M 50 54 q 18 -6 34 -22", stroke=SKIN_D, sw=8)
        + path("M 26 58 q -14 4 -22 -6", stroke=SKIN_D, sw=8)
    )


def i_dancer():
    return (
        head(56, 14, 10, hair=HAIR_L)
        + path("M 56 26 L 48 58 L 64 58 Z", fill=PINK)
        + line(48, 58, 34, 84, INK, 7)
        + line(62, 58, 72, 84, INK, 7)
        + line(50, 34, 28, 22, SKIN, 7)
        + line(62, 34, 84, 26, SKIN, 7)
        + circ(24, 20, 6, YELLOW)
    )


def i_street_musician():
    return (
        person(38, 12, 1.0, PURPLE)
        + rect(60, 44, 10, 34, BROWN, rx=3)
        + ell(72, 74, 18, 16, BROWN_D)
        + circ(72, 74, 6, INK)
        + f'<text x="86" y="30" font-size="26" fill="{PURPLE}">&#9834;</text>'
    )


def i_painter():
    return (
        person(28, 20, 0.95, TEAL)
        + rect(56, 20, 40, 46, WHITE, rx=3, stroke=BROWN, sw=4)
        + circ(70, 36, 8, RED)
        + rect(64, 46, 24, 12, GREEN)
        + line(66, 66, 60, 92, BROWN, 4)
        + line(86, 66, 92, 92, BROWN, 4)
    )


def i_alone():
    return person(50, 22, 1.3, TEAL) + circ(50, 50, 44, "none", stroke=TEAL, sw=3)


def i_children_class():
    return (
        rect(6, 16, 88, 34, GREEN_D, rx=4)
        + line(18, 28, 60, 28, WHITE, 4)
        + line(18, 38, 46, 38, WHITE, 4)
        + person(26, 58, 0.62, RED)
        + person(50, 58, 0.62, YELLOW)
        + person(74, 58, 0.62, BLUE)
    )


def i_children_sport():
    return (
        person(28, 24, 0.8, RED)
        + person(72, 24, 0.8, BLUE)
        + circ(50, 78, 14, WHITE, stroke=INK, sw=3)
        + poly([(50, 68), (58, 74), (55, 84), (45, 84), (42, 74)], INK)
    )


def i_teacher():
    return (
        rect(52, 12, 46, 40, GREEN_D, rx=4)
        + line(60, 24, 90, 24, WHITE, 4)
        + line(60, 34, 80, 34, WHITE, 4)
        + person(28, 22, 1.1, ORANGE)
        + line(40, 46, 56, 34, BROWN, 4)
    )


def i_cleaner():
    return (
        person(34, 14, 1.05, GREEN)
        + line(62, 20, 70, 78, BROWN, 5)
        + path("M 58 78 q 12 -10 24 0 l -4 16 h -16 Z", fill=BLUE)
        + rect(10, 68, 20, 22, YELLOW, rx=3)
    )


def i_nurse():
    """White coat needs its own outline — the panel behind it is white too."""
    return (
        head(50, 30, 14)
        + path("M 50 6 a 14 14 0 0 1 14 14 l -28 0 a 14 14 0 0 1 14 -14 Z", fill=WHITE, stroke=GREY_D, sw=3)
        + rect(45, 10, 10, 4, RED) + rect(48, 7, 4, 10, RED)
        + body(50, 46, 42, 40, WHITE).replace("/>", f' stroke="{GREY_D}" stroke-width="3"/>')
        + rect(43, 62, 14, 5, RED) + rect(47, 58, 6, 13, RED)
        + rect(34, 86, 12, 12, "#4a5b6b", rx=3) + rect(54, 86, 12, 12, "#4a5b6b", rx=3)
    )


def i_office_worker():
    return (
        person(30, 14, 1.0, BLUE_D)
        + rect(52, 44, 44, 30, GREY_L, rx=3, stroke=INK, sw=3)
        + rect(58, 50, 32, 18, BLUE)
        + rect(48, 76, 52, 6, GREY_D, rx=2)
    )


def i_butcher():
    """Butcher in a white coat + striped apron, outlined so it reads on white."""
    return (
        head(40, 32, 14)
        + path("M 26 18 L 54 18 L 54 12 L 26 12 Z", fill=WHITE, stroke=GREY_D, sw=3)
        + body(40, 48, 42, 42, WHITE).replace("/>", f' stroke="{GREY_D}" stroke-width="3"/>')
        + rect(28, 58, 24, 32, "#e8eef2", rx=3, stroke=RED, sw=3)
        + line(40, 58, 40, 90, RED, 3)
        + path("M 62 46 L 88 50 L 86 60 L 60 56 Z", fill=GREY_L, stroke=INK, sw=3)
        + rect(84, 48, 14, 8, BROWN, rx=3, stroke=BROWN_D, sw=2)
    )


def i_knife():
    return (
        path("M 12 64 L 60 20 L 70 32 L 24 76 Z", fill=GREY_L, stroke=INK, sw=3)
        + path("M 14 66 L 58 26", stroke=WHITE, sw=3)
        + rect(64, 20, 26, 14, BROWN, rx=5, stroke=BROWN_D, sw=3)
    )


def i_builder():
    return (
        person(46, 18, 1.15, ORANGE, hat=YELLOW)
        + rect(70, 52, 26, 10, GREY, rx=2)
        + rect(74, 40, 8, 22, GREY_D, rx=2)
    )


# ---- buildings ----------------------------------------------------------


def i_row_houses():
    out = ""
    for i, c in enumerate(("#c0553f", "#d98b4a", "#5b7fb5", "#7a9e5b")):
        x = 4 + i * 24
        out += rect(x, 40, 22, 54, c, rx=2)
        out += poly([(x - 2, 42), (x + 11, 22), (x + 24, 42)], BROWN_D)
        out += rect(x + 6, 58, 10, 14, CREAM, rx=2)
        out += rect(x + 7, 78, 8, 16, BROWN_D, rx=1)
    return out


def i_house_garden():
    return (
        rect(20, 44, 56, 44, CREAM, rx=3, stroke=BROWN, sw=3)
        + poly([(14, 46), (48, 16), (82, 46)], RED)
        + rect(42, 62, 14, 26, BROWN, rx=2)
        + rect(26, 54, 12, 12, SKY, rx=2)
        + rect(60, 54, 12, 12, SKY, rx=2)
        + circ(88, 70, 10, GREEN_D)
        + rect(86, 78, 4, 12, BROWN)
        + rect(0, 88, 100, 8, GREEN, rx=2)
    )


def i_flat_building():
    out = rect(24, 10, 52, 84, GREY_L, rx=4, stroke=GREY_D, sw=3)
    for r in range(5):
        for c in range(3):
            out += rect(30 + c * 15, 18 + r * 15, 10, 10, SKY, rx=2)
    return out + rect(44, 78, 14, 16, BROWN, rx=2)


def i_villa():
    return (
        rect(8, 46, 84, 42, WHITE, rx=3, stroke=GREY_D, sw=3)
        + poly([(4, 48), (50, 20), (96, 48)], "#c0553f")
        + rect(42, 62, 16, 26, BROWN, rx=2)
        + rect(16, 56, 16, 14, SKY, rx=2)
        + rect(68, 56, 16, 14, SKY, rx=2)
        + circ(50, 34, 5, YELLOW)
    )


def i_city():
    return (
        rect(6, 44, 20, 50, "#7d8fa6", rx=2)
        + rect(30, 26, 22, 68, "#5f7391", rx=2)
        + rect(56, 38, 18, 56, "#8fa2b8", rx=2)
        + rect(78, 52, 18, 42, "#6c7f9b", rx=2)
        + "".join(
            rect(x, y, 5, 6, YELLOW, rx=1)
            for x, y in (
                (10, 52), (18, 52), (10, 66), (18, 66),
                (34, 34), (43, 34), (34, 50), (43, 50), (34, 66),
                (60, 46), (68, 46), (60, 62), (68, 62),
                (82, 60), (90, 60), (82, 74),
            )
        )
    )


def i_village():
    return (
        rect(0, 84, 100, 12, GREEN, rx=2)
        + rect(10, 54, 30, 30, CREAM, rx=2, stroke=BROWN, sw=2)
        + poly([(6, 56), (25, 38), (44, 56)], "#c0553f")
        + rect(56, 60, 26, 24, CREAM, rx=2, stroke=BROWN, sw=2)
        + poly([(52, 62), (69, 46), (86, 62)], "#c0553f")
        + circ(92, 66, 9, GREEN_D)
        + rect(20, 68, 8, 16, BROWN)
        + rect(64, 70, 8, 14, BROWN)
    )


def i_school():
    return (
        rect(12, 38, 76, 54, "#e8cf9d", rx=3, stroke=BROWN, sw=3)
        + poly([(8, 40), (50, 14), (92, 40)], "#b0543f")
        + rect(42, 64, 16, 28, BROWN, rx=2)
        + rect(20, 50, 14, 12, SKY, rx=2)
        + rect(66, 50, 14, 12, SKY, rx=2)
        + circ(50, 30, 8, WHITE, stroke=INK, sw=2)
        + line(50, 30, 50, 25, INK, 2)
        + line(50, 30, 54, 32, INK, 2)
    )


def i_museum():
    out = poly([(6, 34), (50, 12), (94, 34)], "#c9b18a")
    out += rect(6, 34, 88, 8, "#b9a179", rx=2)
    for x in (14, 32, 50, 68):
        out += rect(x, 42, 12, 40, WHITE, rx=2, stroke=GREY, sw=2)
    return out + rect(4, 82, 92, 10, "#b9a179", rx=2)


def i_hotel():
    out = rect(18, 24, 64, 70, "#e6dcc8", rx=4, stroke=BROWN, sw=3)
    for r in range(3):
        for c in range(3):
            out += rect(26 + c * 17, 34 + r * 16, 11, 11, SKY, rx=2)
    out += rect(42, 82, 16, 12, BROWN, rx=2)
    for i in range(5):
        out += _star(26 + i * 12, 16, 5, YELLOW)
    return out


def _star(cx, cy, r, fill):
    import math

    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.pi / 2 * 3 + i * math.pi / 5
        pts.append((round(cx + rr * math.cos(a), 1), round(cy + rr * math.sin(a), 1)))
    return poly(pts, fill)


def i_canal_houses():
    out = rect(0, 76, 100, 24, WATER, rx=2)
    for i, (c, top) in enumerate(((("#8a4a3a"), 22), ("#4a6b8a", 16), ("#8a7a3a", 24), ("#5a7a5a", 18))):
        x = 6 + i * 23
        out += rect(x, top, 20, 76 - top, c, rx=2)
        out += poly([(x, top), (x + 10, top - 10), (x + 20, top)], BROWN_D)
        out += rect(x + 5, top + 12, 10, 12, CREAM, rx=1)
        out += rect(x + 5, top + 32, 10, 12, CREAM, rx=1)
    return out + path("M 0 80 q 12 -6 24 0 t 24 0 t 24 0 t 24 0", stroke=WHITE, sw=3)


def i_windmill():
    return (
        rect(0, 86, 100, 12, GREEN, rx=2)
        + poly([(34, 86), (42, 34), (58, 34), (66, 86)], "#b9865c")
        + poly([(38, 36), (62, 36), (50, 22)], BROWN_D)
        + line(50, 40, 22, 14, BROWN, 5)
        + line(50, 40, 78, 66, BROWN, 5)
        + line(50, 40, 24, 66, BROWN, 5)
        + line(50, 40, 76, 14, BROWN, 5)
        + circ(50, 40, 5, INK)
        + rect(44, 66, 12, 20, BROWN_D, rx=2)
    )


def i_floorplan():
    out = rect(10, 14, 80, 74, WHITE, rx=4, stroke=INK, sw=4)
    out += line(50, 14, 50, 52, INK, 4)
    out += line(10, 52, 90, 52, INK, 4)
    out += line(70, 52, 70, 88, INK, 4)
    for x, y in ((26, 34), (66, 34), (34, 72), (80, 72)):
        out += f'<text x="{x}" y="{y}" text-anchor="middle" font-size="12" font-weight="700" fill="{GREY_D}">&#9634;</text>'
    return out


def i_modern_room():
    return (
        rect(6, 20, 88, 62, WHITE, rx=4, stroke=GREY, sw=3)
        + rect(14, 52, 46, 22, GREY_L, rx=4)
        + rect(14, 44, 46, 10, "#4d5b6b", rx=4)
        + rect(66, 30, 24, 16, INK, rx=2)
        + circ(78, 62, 8, ORANGE)
        + rect(20, 74, 60, 4, "#c8b79a", rx=2)
    )


def i_classic_room():
    return (
        rect(6, 20, 88, 62, CREAM, rx=4, stroke=BROWN, sw=3)
        + rect(14, 50, 44, 26, "#a3453c", rx=6)
        + rect(18, 44, 36, 10, BROWN_D, rx=4)
        + rect(66, 28, 24, 20, BROWN, rx=2, stroke=YELLOW, sw=3)
        + line(24, 76, 84, 76, BROWN_D, 4)
        + circ(78, 60, 7, GREEN_D)
    )


def i_classroom():
    return (
        rect(8, 12, 84, 34, GREEN_D, rx=4)
        + line(18, 24, 66, 24, WHITE, 4)
        + line(18, 34, 48, 34, WHITE, 4)
        + rect(10, 62, 34, 8, BROWN, rx=2)
        + rect(56, 62, 34, 8, BROWN, rx=2)
        + person(27, 48, 0.55, BLUE, legs=False)
        + person(73, 48, 0.55, PINK, legs=False)
    )


def i_theatre():
    return (
        rect(4, 12, 92, 60, INK, rx=4)
        + path("M 4 12 q 24 26 46 12 q 22 -14 46 -12 l 0 -2 l -92 0 Z", fill=RED)
        + rect(12, 20, 76, 44, "#2b3a4d", rx=3)
        + person(50, 30, 0.8, PINK)
        + rect(0, 76, 100, 22, "#3d2f45", rx=3)
        + "".join(rect(8 + i * 18, 82, 14, 10, "#6b4f78", rx=3) for i in range(5))
    )


def i_cinema():
    return (
        rect(6, 10, 88, 58, INK, rx=4)
        + rect(12, 16, 76, 46, "#7fb3e0", rx=2)
        + poly([(30, 54), (50, 26), (70, 54)], WHITE)
        + circ(50, 34, 6, YELLOW)
        + "".join(rect(10 + i * 20, 76, 16, 18, RED, rx=4) for i in range(5))
    )


def i_gym():
    return (
        rect(10, 62, 80, 12, GREY_D, rx=4)
        + rect(16, 74, 68, 8, INK, rx=3)
        + line(84, 62, 84, 26, GREY_D, 5)
        + rect(70, 20, 28, 10, INK, rx=3)
        + person(44, 12, 0.9, RED, legs=False)
        + line(40, 52, 30, 64, INK, 6)
        + line(50, 52, 60, 64, INK, 6)
    )


def i_police_office():
    return (
        rect(12, 30, 76, 60, "#dbe4f0", rx=4, stroke=BLUE_D, sw=3)
        + rect(36, 60, 28, 30, BLUE_D, rx=2)
        + rect(20, 42, 16, 12, SKY, rx=2)
        + rect(64, 42, 16, 12, SKY, rx=2)
        + poly([(50, 8), (62, 14), (60, 28), (50, 32), (40, 28), (38, 14)], BLUE)
        + f'<text x="50" y="26" text-anchor="middle" font-size="14" font-weight="800" fill="{WHITE}">P</text>'
    )


def i_market():
    out = poly([(4, 30), (96, 30), (88, 44), (12, 44)], RED)
    out += "".join(rect(12 + i * 19, 30, 9, 14, WHITE) for i in range(4))
    out += rect(10, 44, 6, 46, BROWN) + rect(84, 44, 6, 46, BROWN)
    out += rect(18, 60, 64, 22, "#c9a882", rx=3)
    out += circ(30, 56, 7, RED) + circ(44, 56, 7, ORANGE) + circ(58, 56, 7, GREEN) + circ(72, 56, 7, PURPLE)
    return out


def i_supermarket():
    return (
        rect(8, 26, 84, 58, "#dfe7ef", rx=4, stroke=GREY_D, sw=3)
        + rect(8, 26, 84, 14, GREEN_D, rx=4)
        + rect(20, 48, 26, 30, WHITE, rx=2)
        + rect(54, 48, 26, 30, WHITE, rx=2)
        + line(20, 60, 46, 60, GREY, 3)
        + line(54, 60, 80, 60, GREY, 3)
        + circ(28, 54, 4, RED) + circ(38, 54, 4, ORANGE)
        + circ(62, 68, 4, GREEN) + circ(72, 68, 4, PURPLE)
    )


def i_snackbar():
    return (
        rect(10, 34, 80, 54, "#f2d9a8", rx=4, stroke=BROWN, sw=3)
        + poly([(6, 36), (50, 16), (94, 36)], RED)
        + rect(22, 52, 56, 22, WHITE, rx=3)
        + path("M 34 70 l 6 -18 l 6 18 Z", fill=YELLOW)
        + rect(52, 54, 20, 16, "#c9773f", rx=3)
        + circ(62, 50, 5, RED)
    )


def i_restaurant():
    return (
        circ(50, 50, 34, WHITE, stroke=GREY, sw=3)
        + circ(50, 50, 22, GREY_L)
        + line(16, 24, 16, 76, INK, 5)
        + path("M 10 24 l 0 16 M 22 24 l 0 16", stroke=INK, sw=4)
        + path("M 84 24 q 10 6 4 24 l -4 28", stroke=INK, sw=5)
    )


def i_clothes_shop():
    out = rect(8, 30, 84, 60, "#f0e2ee", rx=4, stroke=PINK, sw=3)
    out += rect(8, 30, 84, 12, PINK, rx=4)
    out += line(20, 52, 80, 52, GREY_D, 3)
    for i, c in enumerate((RED, BLUE, GREEN, PURPLE)):
        x = 26 + i * 16
        out += path(f"M {x} 52 l -6 10 l 4 4 l 0 16 l 12 0 l 0 -16 l 4 -4 Z", fill=c)
    return out


# ---- transport ----------------------------------------------------------


def i_bicycle():
    return (
        circ(24, 66, 20, "none", stroke=INK, sw=5)
        + circ(76, 66, 20, "none", stroke=INK, sw=5)
        + path("M 24 66 L 44 36 L 68 36 L 76 66", stroke=BLUE, sw=5)
        + path("M 44 36 L 52 66 L 76 66", stroke=BLUE, sw=5)
        + line(40, 30, 52, 30, INK, 5)
        + rect(62, 30, 14, 6, INK, rx=3)
    )


def i_bikes_row():
    return grp(i_bicycle(), 0, 20, 0.62) + grp(i_bicycle(), 38, 20, 0.62) + grp(i_bicycle(), 19, 50, 0.62)


def i_car(color=RED):
    return (
        path("M 8 66 L 12 46 q 2 -6 8 -6 L 80 40 q 6 0 8 6 L 92 66 Z", fill=color)
        + path("M 24 42 L 28 26 q 1 -4 6 -4 L 66 22 q 5 0 6 4 L 76 42 Z", fill=SKY, stroke=color, sw=3)
        + rect(6, 60, 88, 12, color, rx=5)
        + circ(26, 74, 11, INK) + circ(26, 74, 5, GREY_L)
        + circ(74, 74, 11, INK) + circ(74, 74, 5, GREY_L)
    )


def i_broken_car():
    return i_car(GREY) + f'<text x="72" y="24" font-size="30" font-weight="800" fill="{RED}">&#10007;</text>' + path(
        "M 44 18 l 8 -12 l -3 10 l 8 -2 l -12 14 l 3 -10 Z", fill=ORANGE
    )


def i_car_wash():
    return i_car(BLUE) + "".join(
        path(f"M {x} 18 q 4 6 0 10 q -4 -4 0 -10 Z", fill=SKY) for x in (20, 40, 60, 80)
    )


def i_bus():
    out = rect(8, 22, 84, 52, ORANGE, rx=8)
    out += rect(14, 30, 32, 20, SKY, rx=3) + rect(54, 30, 32, 20, SKY, rx=3)
    out += rect(14, 58, 20, 8, YELLOW, rx=2) + rect(66, 58, 20, 8, YELLOW, rx=2)
    return out + circ(26, 78, 10, INK) + circ(26, 78, 4, GREY_L) + circ(74, 78, 10, INK) + circ(74, 78, 4, GREY_L)


def i_taxi():
    return i_car(YELLOW) + rect(38, 12, 24, 10, INK, rx=3) + f'<text x="50" y="21" text-anchor="middle" font-size="9" font-weight="800" fill="{YELLOW}">TAXI</text>'


def i_train():
    out = rect(16, 16, 68, 58, BLUE, rx=10)
    out += rect(24, 26, 52, 22, SKY, rx=4)
    out += circ(34, 58, 6, YELLOW) + circ(66, 58, 6, YELLOW)
    out += rect(12, 74, 76, 8, GREY_D, rx=3)
    out += line(4, 88, 96, 88, GREY_D, 5) + line(4, 94, 96, 94, GREY_D, 5)
    return out


def i_airplane():
    return (
        path("M 6 54 L 88 40 q 8 -1 8 5 q 0 6 -8 6 L 6 62 Z", fill=WHITE, stroke=BLUE_D, sw=3)
        + poly([(40, 48), (28, 18), (40, 18), (58, 46)], BLUE)
        + poly([(40, 56), (28, 82), (40, 82), (58, 58)], BLUE_D)
        + circ(84, 48, 3, SKY)
    )


def i_boat():
    return (
        rect(0, 74, 100, 20, WATER, rx=4)
        + path("M 12 62 L 88 62 L 76 78 L 24 78 Z", fill=BROWN)
        + line(50, 20, 50, 62, BROWN_D, 4)
        + poly([(52, 24), (82, 56), (52, 56)], WHITE)
        + poly([(48, 30), (24, 56), (48, 56)], RED)
    )


def i_traffic_jam():
    return (
        rect(0, 0, 100, 100, "#dfe4e8", rx=4)
        + line(50, 0, 50, 100, WHITE, 4)
        + grp(i_car(RED), 4, 2, 0.42)
        + grp(i_car(BLUE), 4, 40, 0.42)
        + grp(i_car(GREEN), 52, 12, 0.42)
        + grp(i_car(ORANGE), 52, 52, 0.42)
    )


def i_steering_wheel():
    return (
        circ(50, 50, 36, "none", stroke=INK, sw=9)
        + circ(50, 50, 11, INK)
        + line(50, 39, 50, 16, INK, 7)
        + line(41, 57, 22, 72, INK, 7)
        + line(59, 57, 78, 72, INK, 7)
    )


def i_licence():
    return (
        rect(8, 26, 84, 54, WHITE, rx=6, stroke=BLUE_D, sw=4)
        + rect(8, 26, 84, 12, BLUE, rx=6)
        + circ(30, 56, 12, GREY_L)
        + circ(30, 51, 5, GREY_D)
        + path("M 20 66 a 10 10 0 0 1 20 0 Z", fill=GREY_D)
        + line(50, 50, 84, 50, GREY, 4)
        + line(50, 62, 76, 62, GREY, 4)
    )


def i_car_mirror():
    return (
        path("M 10 34 q 40 -18 80 0 l 0 30 q -40 16 -80 0 Z", fill=SKY, stroke=INK, sw=4)
        + rect(44, 64, 12, 16, INK, rx=3)
        + circ(38, 48, 8, SKIN)
        + path("M 30 44 a 8 8 0 0 1 16 0 Z", fill=HAIR)
        + line(58, 44, 78, 44, WHITE, 3)
    )


def i_backpacks():
    def pack(x, c):
        return (
            rect(x, 34, 30, 44, c, rx=10)
            + rect(x + 6, 24, 18, 14, c, rx=6)
            + rect(x + 6, 52, 18, 14, CREAM, rx=4)
            + line(x + 4, 40, x + 4, 72, INK, 3)
            + line(x + 26, 40, x + 26, 72, INK, 3)
        )

    return pack(6, RED) + pack(38, BLUE) + pack(66, GREEN_D)


def i_suitcase():
    return (
        rect(16, 32, 68, 52, BROWN, rx=8, stroke=BROWN_D, sw=3)
        + rect(38, 20, 24, 14, "none", stroke=INK, sw=5)
        + line(16, 52, 84, 52, BROWN_D, 4)
        + rect(44, 44, 12, 16, YELLOW, rx=2)
    )


def i_speed_camera():
    return (
        rect(30, 66, 12, 30, GREY_D, rx=3)
        + rect(14, 30, 52, 36, INK, rx=6)
        + circ(34, 48, 12, SKY, stroke=GREY_L, sw=3)
        + rect(66, 38, 16, 12, GREY_L, rx=3)
        + path("M 84 30 l 12 -10 M 84 44 l 14 0 M 84 56 l 12 10", stroke=YELLOW, sw=4)
    )


# ---- food & drink -------------------------------------------------------


def i_coffee():
    return (
        path("M 20 34 L 76 34 L 70 78 q -1 8 -9 8 L 35 86 q -8 0 -9 -8 Z", fill=WHITE, stroke=INK, sw=4)
        + path("M 24 44 L 72 44 L 68 74 q -1 6 -7 6 L 37 80 q -6 0 -7 -6 Z", fill="#7a4a2b")
        + path("M 76 44 q 16 0 16 12 q 0 12 -16 12", stroke=INK, sw=4)
        + path("M 38 24 q 4 -8 0 -14 M 52 24 q 4 -8 0 -14 M 66 24 q 4 -8 0 -14", stroke=GREY, sw=3)
    )


def i_tea():
    return (
        path("M 22 36 L 74 36 L 68 78 q -1 8 -9 8 L 33 86 q -8 0 -9 -8 Z", fill=WHITE, stroke=INK, sw=4)
        + path("M 26 46 L 70 46 L 66 74 q -1 6 -7 6 L 35 80 q -6 0 -7 -6 Z", fill="#c98a3c")
        + rect(46, 20, 20, 14, YELLOW, rx=2)
        + line(52, 34, 52, 46, GREY_D, 2)
        + path("M 74 46 q 14 0 14 12 q 0 12 -14 12", stroke=INK, sw=4)
    )


def i_beer():
    return (
        path("M 26 22 L 68 22 L 64 84 q 0 6 -6 6 L 36 90 q -6 0 -6 -6 Z", fill="#f5d27a", stroke=INK, sw=4)
        + path("M 26 22 q 8 -12 20 -6 q 10 -8 22 6 Z", fill=WHITE, stroke=INK, sw=3)
        + path("M 68 34 q 16 2 16 16 q 0 14 -16 14", stroke=INK, sw=4)
        + circ(42, 52, 4, WHITE) + circ(54, 66, 3, WHITE)
    )


def i_wine():
    return (
        path("M 30 14 L 70 14 q 0 30 -16 36 L 54 76 L 68 84 L 32 84 L 46 76 L 46 50 q -16 -6 -16 -36 Z",
             fill=WHITE, stroke=INK, sw=4)
        + path("M 31 20 L 69 20 q -2 22 -19 26 q -17 -4 -19 -26 Z", fill="#9b2f43")
    )


def i_apple():
    return (
        path("M 50 30 q 22 -10 30 12 q 8 24 -12 42 q -12 12 -18 4 q -6 8 -18 -4 q -20 -18 -12 -42 q 8 -22 30 -12 Z",
             fill=RED)
        + rect(47, 18, 5, 14, BROWN, rx=2)
        + path("M 52 24 q 14 -10 20 0 q -12 8 -20 0 Z", fill=GREEN_D)
        + path("M 38 44 q 6 -8 14 -6", stroke=WHITE, sw=3)
    )


def i_fruit_bowl():
    return (
        circ(34, 42, 15, RED)
        + circ(62, 40, 14, ORANGE)
        + ell(48, 54, 16, 9, GREEN)
        + path("M 10 58 q 40 26 80 0 q -6 30 -40 30 q -34 0 -40 -30 Z", fill=CREAM, stroke=BROWN, sw=3)
        + rect(31, 28, 4, 10, BROWN, rx=1)
    )


def i_vegetables():
    return (
        path("M 20 46 q 14 -18 28 0 q 6 30 -14 42 q -20 -12 -14 -42 Z", fill=GREEN)
        + path("M 34 42 q 0 -14 -6 -20 q 12 2 12 18 Z", fill=GREEN_D)
        + circ(70, 62, 20, RED)
        + path("M 70 42 q -8 -6 -2 -10 q 8 0 8 10 Z", fill=GREEN_D)
        + ell(54, 82, 26, 8, GREEN_D)
    )


def i_cookies():
    return (
        rect(18, 30, 64, 56, "#d99b4a", rx=8, stroke=BROWN, sw=3)
        + rect(24, 38, 52, 12, CREAM, rx=3)
        + circ(38, 64, 8, "#c98a3c") + circ(62, 64, 8, "#c98a3c")
        + circ(38, 64, 2.5, BROWN_D) + circ(62, 62, 2.5, BROWN_D) + circ(58, 70, 2.5, BROWN_D)
        + f'<text x="50" y="48" text-anchor="middle" font-size="10" font-weight="800" fill="{BROWN}">KOEK</text>'
    )


def i_sandwich():
    return (
        path("M 10 44 q 40 -22 80 0 l 0 8 l -80 0 Z", fill="#d9a05b")
        + rect(10, 52, 80, 8, GREEN)
        + rect(10, 60, 80, 8, "#e0483d")
        + path("M 10 68 l 80 0 l 0 8 q -40 18 -80 0 Z", fill="#d9a05b")
    )


def i_muesli():
    return (
        path("M 12 46 q 38 26 76 0 q -6 34 -38 34 q -32 0 -38 -34 Z", fill=WHITE, stroke=GREY, sw=3)
        + "".join(circ(x, y, 4, c) for x, y, c in (
            (32, 52, "#c98a3c"), (46, 56, RED), (60, 52, "#c98a3c"),
            (40, 64, PURPLE), (56, 66, "#c98a3c"), (68, 58, GREEN),
        ))
        + rect(72, 24, 22, 8, GREY_L, rx=4)
    )


def i_pasta():
    return (
        ell(50, 58, 42, 28, WHITE, stroke=GREY, sw=3)
        + ell(50, 58, 30, 19, "#f3e2b8")
        + "".join(path(f"M {26 + i * 10} 52 q 6 10 12 0", stroke="#e0b25c", sw=4) for i in range(5))
        + circ(44, 60, 6, RED) + circ(60, 62, 5, RED)
        + rect(38, 48, 24, 4, CREAM, rx=2)
    )


def i_plate_food():
    return (
        ell(50, 58, 42, 28, WHITE, stroke=GREY, sw=3)
        + ell(50, 58, 30, 19, GREY_L)
        + path("M 32 58 q 8 -14 20 -4 q 10 -10 18 4 q -18 12 -38 0 Z", fill="#c9773f")
        + circ(40, 52, 5, GREEN) + circ(62, 52, 5, RED)
    )


def i_cooking_pot():
    return (
        path("M 16 44 L 84 44 L 78 82 q -1 8 -9 8 L 31 90 q -8 0 -9 -8 Z", fill=GREY, stroke=INK, sw=4)
        + rect(10, 36, 80, 10, GREY_D, rx=4)
        + rect(42, 26, 16, 8, GREY_D, rx=4)
        + path("M 30 24 q 4 -10 0 -18 M 50 22 q 4 -10 0 -18 M 70 24 q 4 -10 0 -18", stroke=GREY_L, sw=3)
    )


def i_apple_pie():
    return (
        path("M 10 58 L 90 58 L 82 84 L 18 84 Z", fill="#d9a05b", stroke=BROWN, sw=3)
        + path("M 14 58 q 36 -30 72 0 Z", fill="#e8b96e")
        + "".join(line(24 + i * 12, 44, 34 + i * 12, 58, BROWN, 3) for i in range(5))
        + circ(50, 34, 6, RED) + rect(48, 26, 4, 8, BROWN, rx=1)
    )


def i_licorice():
    return (
        "".join(
            rect(18 + i * 18, 34 + (i % 2) * 16, 20, 20, INK, rx=5) for i in range(4)
        )
        + rect(20, 78, 60, 10, GREY_D, rx=4)
    )


def i_meal_tray():
    return (
        rect(10, 40, 80, 46, GREY_L, rx=6, stroke=GREY_D, sw=3)
        + circ(34, 58, 14, WHITE, stroke=GREY, sw=2)
        + circ(34, 58, 8, "#c9773f")
        + rect(56, 46, 26, 16, WHITE, rx=3, stroke=GREY, sw=2)
        + rect(56, 66, 26, 14, SKY, rx=3, stroke=GREY, sw=2)
    )


def i_dinner_table():
    return (
        ell(50, 54, 44, 20, "#d9a05b", stroke=BROWN, sw=3)
        + rect(46, 62, 8, 30, BROWN)
        + rect(30, 88, 40, 6, BROWN_D, rx=3)
        + circ(34, 50, 10, WHITE, stroke=GREY, sw=2)
        + circ(66, 50, 10, WHITE, stroke=GREY, sw=2)
        + person(20, 12, 0.62, BLUE, legs=False)
        + person(80, 12, 0.62, PINK, legs=False)
    )


def i_shopping_cart():
    return (
        path("M 8 20 L 22 20 L 34 62 L 84 62 L 92 30 L 28 30", stroke=INK, sw=6)
        + rect(36, 34, 50, 24, GREEN, rx=3)
        + circ(40, 78, 9, INK) + circ(78, 78, 9, INK)
        + circ(50, 30, 6, RED) + circ(66, 30, 6, ORANGE)
    )


def i_shopping_bags():
    def bag(x, c):
        return (
            rect(x, 40, 32, 46, c, rx=4)
            + path(f"M {x + 8} 40 q 0 -14 8 -14 q 8 0 8 14", stroke=INK, sw=3)
        )

    return bag(8, RED) + bag(46, PURPLE) + rect(20, 56, 8, 8, WHITE, rx=2) + rect(58, 56, 8, 8, WHITE, rx=2)


def i_online_shopping():
    return (
        rect(8, 20, 84, 54, INK, rx=6)
        + rect(14, 26, 72, 42, WHITE, rx=3)
        + rect(36, 78, 28, 6, GREY_D, rx=3)
        + grp(i_shopping_cart(), 26, 26, 0.46)
        + circ(72, 40, 9, RED)
        + f'<text x="72" y="45" text-anchor="middle" font-size="12" font-weight="800" fill="{WHITE}">3</text>'
    )


def i_terrace():
    return (
        poly([(6, 34), (94, 34), (86, 46), (14, 46)], RED)
        + "".join(rect(14 + i * 18, 34, 9, 12, WHITE) for i in range(4))
        + circ(34, 66, 16, WHITE, stroke=GREY, sw=3)
        + grp(i_coffee(), 22, 48, 0.34)
        + rect(66, 60, 24, 6, BROWN, rx=3)
        + rect(74, 66, 8, 26, BROWN)
    )


def i_no_alcohol():
    return grp(i_wine(), 0, 0, 0.9) + circ(50, 50, 40, "none", stroke=RED, sw=8) + line(22, 78, 78, 22, RED, 8)


# ---- tech ---------------------------------------------------------------


def i_laptop():
    return (
        rect(16, 20, 68, 46, INK, rx=4)
        + rect(21, 25, 58, 36, SKY, rx=2)
        + path("M 6 66 L 94 66 L 88 78 L 12 78 Z", fill=GREY_L, stroke=GREY_D, sw=3)
        + rect(40, 70, 20, 4, GREY_D, rx=2)
    )


def i_desktop():
    return (
        rect(10, 14, 80, 54, INK, rx=5)
        + rect(16, 20, 68, 42, SKY, rx=2)
        + rect(42, 68, 16, 14, GREY_D)
        + rect(26, 82, 48, 8, GREY_D, rx=3)
        + rect(20, 92, 44, 6, GREY_L, rx=2)
    )


def i_keyboard():
    out = rect(6, 40, 88, 40, GREY_L, rx=6, stroke=GREY_D, sw=3)
    for r in range(3):
        for c in range(8):
            out += rect(13 + c * 10, 46 + r * 10, 7, 7, WHITE, rx=1.5)
    return out


def i_keyboard_coffee():
    return (
        i_keyboard()
        + grp(i_coffee(), 44, -8, 0.5, rot=40)
        + path("M 30 60 q 14 10 30 4 q -6 12 -20 10 q -14 -2 -10 -14 Z", fill="#7a4a2b")
    )


def i_smartphone():
    return (
        rect(30, 10, 40, 80, INK, rx=8)
        + rect(34, 18, 32, 60, SKY, rx=3)
        + circ(50, 84, 4, GREY_L)
        + rect(42, 13, 16, 3, GREY_D, rx=1.5)
        + "".join(rect(38 + (i % 3) * 10, 24 + (i // 3) * 12, 8, 8, WHITE, rx=2) for i in range(6))
    )


def i_phone_call():
    return (
        path("M 22 16 q 12 -6 18 4 l 6 12 q 3 6 -3 10 l -6 4 q 6 16 20 24 l 4 -6 q 4 -6 10 -3 l 12 6 q 10 6 4 18 "
             "q -6 12 -22 8 q -22 -6 -38 -22 q -16 -16 -22 -38 q -4 -16 8 -22 Z", fill=GREEN_D)
        + path("M 66 20 q 12 4 14 16 M 62 32 q 6 2 8 8", stroke=GREEN, sw=4)
    )


def i_video_call():
    return (
        rect(8, 22, 84, 54, INK, rx=6)
        + rect(14, 28, 34, 42, SKY, rx=3)
        + rect(52, 28, 34, 42, "#b7d8f0", rx=3)
        + person(31, 34, 0.5, BLUE, legs=False)
        + person(69, 34, 0.5, PINK, legs=False)
        + rect(36, 80, 28, 6, GREY_D, rx=3)
    )


def i_email():
    return (
        rect(8, 26, 84, 54, WHITE, rx=6, stroke=BLUE_D, sw=4)
        + path("M 8 30 L 50 60 L 92 30", stroke=BLUE, sw=4)
        + circ(84, 30, 12, RED)
        + f'<text x="84" y="35" text-anchor="middle" font-size="14" font-weight="800" fill="{WHITE}">!</text>'
    )


def i_inbox_many():
    out = ""
    for i in range(3):
        y = 14 + i * 22
        out += rect(10, y, 80, 20, WHITE, rx=4, stroke=BLUE_D, sw=3)
        out += path(f"M 10 {y + 2} L 50 {y + 16} L 90 {y + 2}", stroke=BLUE, sw=3)
    return out + circ(84, 84, 13, RED) + f'<text x="84" y="90" text-anchor="middle" font-size="15" font-weight="800" fill="{WHITE}">9</text>'


def i_trash_email():
    return (
        rect(14, 20, 56, 34, WHITE, rx=4, stroke=GREY_D, sw=3)
        + path("M 14 22 L 42 40 L 70 22", stroke=GREY, sw=3)
        + path("M 44 62 L 92 62 L 86 94 L 50 94 Z", fill=GREY_D)
        + rect(40, 54, 56, 8, INK, rx=3)
        + line(60, 70, 62, 86, GREY_L, 3) + line(76, 70, 74, 86, GREY_L, 3)
    )


def i_headphones():
    return (
        path("M 16 62 L 16 48 a 34 34 0 0 1 68 0 L 84 62", stroke=INK, sw=7)
        + rect(6, 58, 20, 30, PURPLE, rx=7)
        + rect(74, 58, 20, 30, PURPLE, rx=7)
    )


def i_social_media():
    return (
        rect(12, 12, 76, 76, "#4267b2", rx=14)
        + f'<text x="50" y="76" text-anchor="middle" font-size="62" font-weight="800" fill="{WHITE}" font-family="Georgia,serif">f</text>'
        + circ(80, 22, 14, RED)
        + path("M 74 22 q 6 -8 12 0 q -6 8 -12 0 Z", fill=WHITE)
    )


def i_tv(screen="film"):
    out = rect(8, 16, 84, 58, INK, rx=6) + rect(14, 22, 72, 46, "#5fa9dd", rx=3)
    if screen == "film":
        out += poly([(36, 60), (50, 34), (64, 60)], WHITE) + circ(50, 40, 5, YELLOW)
    else:
        out += rect(18, 44, 64, 22, GREEN) + circ(50, 54, 9, WHITE, stroke=INK, sw=2)
        out += line(18, 54, 82, 54, WHITE, 2)
    out += rect(40, 74, 20, 8, GREY_D) + rect(28, 82, 44, 6, GREY_D, rx=3)
    return out


def i_tv_football():
    return i_tv("football")


def i_radio():
    return (
        rect(8, 32, 84, 52, BROWN, rx=8, stroke=BROWN_D, sw=3)
        + circ(34, 58, 16, GREY_L, stroke=INK, sw=3)
        + "".join(line(22, 50 + i * 6, 46, 50 + i * 6, GREY_D, 2) for i in range(4))
        + circ(70, 50, 7, INK) + circ(70, 70, 7, INK)
        + line(80, 32, 92, 10, GREY_D, 4)
    )


# ---- objects ------------------------------------------------------------


def i_books():
    return (
        rect(14, 30, 18, 60, RED, rx=3)
        + rect(34, 22, 18, 68, BLUE, rx=3)
        + rect(54, 34, 18, 56, GREEN_D, rx=3)
        + rect(70, 60, 24, 14, YELLOW, rx=3)
        + line(18, 44, 28, 44, WHITE, 3) + line(38, 36, 48, 36, WHITE, 3) + line(58, 48, 68, 48, WHITE, 3)
    )


def i_open_book():
    return (
        path("M 50 34 q -18 -12 -42 -6 L 8 76 q 24 -6 42 6 Z", fill=WHITE, stroke=INK, sw=3)
        + path("M 50 34 q 18 -12 42 -6 L 92 76 q -24 -6 -42 6 Z", fill=CREAM, stroke=INK, sw=3)
        + "".join(line(18, 44 + i * 8, 40, 42 + i * 8, GREY, 2) for i in range(3))
        + "".join(line(60, 42 + i * 8, 82, 44 + i * 8, GREY, 2) for i in range(3))
    )


def i_pen_paper():
    return (
        rect(16, 14, 58, 74, WHITE, rx=4, stroke=GREY_D, sw=3)
        + "".join(line(24, 30 + i * 12, 62, 30 + i * 12, GREY_L, 3) for i in range(4))
        + path("M 62 82 L 86 40 L 96 46 L 72 88 L 60 92 Z", fill=BLUE)
        + poly([(60, 92), (64, 82), (72, 88)], YELLOW)
    )


def i_gift():
    return (
        rect(12, 40, 76, 50, RED, rx=6)
        + rect(8, 28, 84, 16, "#c33a30", rx=5)
        + rect(42, 28, 16, 62, YELLOW)
        + path("M 50 28 q -20 -6 -18 -14 q 2 -8 18 14 Z", fill=YELLOW)
        + path("M 50 28 q 20 -6 18 -14 q -2 -8 -18 14 Z", fill=YELLOW)
    )


def i_flowers():
    def bloom(cx, cy, c):
        return "".join(ell(cx + dx, cy + dy, 7, 9, c) for dx, dy in ((0, -9), (9, 0), (0, 9), (-9, 0))) + circ(cx, cy, 6, YELLOW)

    return (
        line(30, 90, 34, 44, GREEN_D, 4) + line(50, 92, 50, 40, GREEN_D, 4) + line(70, 90, 66, 46, GREEN_D, 4)
        + bloom(34, 36, PINK) + bloom(50, 30, RED) + bloom(66, 38, PURPLE)
        + path("M 34 68 q -14 -6 -18 4 q 12 6 18 -4 Z", fill=GREEN)
        + path("M 66 70 q 14 -6 18 4 q -12 6 -18 -4 Z", fill=GREEN)
    )


def i_tulips():
    def tulip(cx, cy, c):
        return path(f"M {cx - 11} {cy} q 0 -16 11 -16 q 11 0 11 16 q -11 8 -22 0 Z", fill=c) + \
            line(cx, cy, cx, cy + 40, GREEN_D, 4) + \
            path(f"M {cx} {cy + 20} q -14 -4 -16 8 q 12 4 16 -8 Z", fill=GREEN)

    return tulip(24, 44, RED) + tulip(50, 36, YELLOW) + tulip(76, 46, PINK) + rect(0, 88, 100, 10, GREEN, rx=2)


def i_clog():
    return (
        path("M 12 58 q 0 -14 16 -14 L 54 44 q 26 0 32 22 q 4 16 -12 18 L 26 84 q -14 0 -14 -14 Z",
             fill=YELLOW, stroke="#d9a300", sw=3)
        + path("M 30 52 q 12 -6 22 4", stroke="#d9a300", sw=3)
        + circ(40, 62, 4, RED) + circ(56, 66, 4, RED) + circ(48, 72, 4, BLUE)
    )


def i_music():
    return (
        line(38, 24, 38, 70, INK, 5) + line(72, 16, 72, 62, INK, 5)
        + rect(38, 16, 34, 10, INK, rx=3)
        + ell(30, 72, 12, 9, PURPLE) + ell(64, 64, 12, 9, PURPLE)
    )


def i_camera():
    return (
        rect(8, 30, 84, 56, INK, rx=8)
        + rect(34, 20, 26, 12, GREY_D, rx=4)
        + circ(50, 58, 20, GREY_L, stroke=GREY_D, sw=3)
        + circ(50, 58, 12, SKY)
        + circ(45, 53, 4, WHITE)
        + circ(78, 42, 5, RED)
    )


def i_painting():
    return (
        rect(10, 14, 80, 72, "#c9a35c", rx=4)
        + rect(18, 22, 64, 56, CREAM)
        + line(38, 78, 38, 56, GREEN_D, 3) + line(50, 78, 50, 50, GREEN_D, 3) + line(62, 78, 62, 58, GREEN_D, 3)
        + circ(38, 52, 8, PINK) + circ(50, 46, 9, RED) + circ(62, 54, 8, PURPLE)
        + circ(38, 52, 3, YELLOW) + circ(50, 46, 3, YELLOW) + circ(62, 54, 3, YELLOW)
    )


def i_price_tag():
    return (
        path("M 52 12 L 92 12 L 92 52 L 48 92 L 8 52 Z", fill=ORANGE, stroke="#c96f16", sw=3)
        + circ(76, 30, 8, WHITE)
        + f'<text x="46" y="66" text-anchor="middle" font-size="26" font-weight="800" fill="{WHITE}"'
        f' transform="rotate(-45,46,60)">&#8364;</text>'
    )


def i_second_hand():
    return (
        circ(50, 50, 34, "none", stroke=GREEN_D, sw=8)
        + poly([(50, 6), (66, 18), (50, 30)], GREEN_D)
        + poly([(50, 94), (34, 82), (50, 70)], GREEN_D)
        + f'<text x="50" y="60" text-anchor="middle" font-size="26" font-weight="800" fill="{GREEN_D}">2</text>'
    )


def i_sofa():
    return (
        rect(10, 44, 80, 30, "#c9773f", rx=8)
        + rect(4, 52, 16, 26, "#a85f31", rx=6)
        + rect(80, 52, 16, 26, "#a85f31", rx=6)
        + rect(16, 36, 68, 18, "#d9884a", rx=6)
        + rect(14, 74, 8, 12, BROWN_D, rx=2) + rect(78, 74, 8, 12, BROWN_D, rx=2)
    )


def i_sweater():
    return (
        path("M 30 26 L 44 22 q 6 6 12 0 L 70 26 L 92 44 L 80 58 L 72 52 L 72 88 L 28 88 L 28 52 L 20 58 L 8 44 Z",
             fill=PURPLE, stroke="#6f4fa5", sw=3)
        + line(28, 66, 72, 66, "#6f4fa5", 3)
        + line(28, 76, 72, 76, "#6f4fa5", 3)
    )


def i_umbrella():
    return (
        path("M 8 50 q 8 -36 42 -36 q 34 0 42 36 Z", fill=RED, stroke="#b8382e", sw=3)
        + path("M 8 50 q 12 -12 21 0 q 12 -12 21 0 q 12 -12 21 0 q 12 -12 21 0", stroke="#b8382e", sw=3)
        + line(50, 50, 50, 82, GREY_D, 5)
        + path("M 50 82 q 0 10 -12 10 q -8 0 -8 -8", stroke=GREY_D, sw=5)
    )


def i_orange_shirt():
    return (
        path("M 28 24 L 42 20 q 8 8 16 0 L 72 24 L 92 42 L 80 56 L 72 50 L 72 88 L 28 88 L 28 50 L 20 56 L 8 42 Z",
             fill="#ff7a00", stroke="#d96500", sw=3)
        + f'<text x="50" y="72" text-anchor="middle" font-size="26" font-weight="800" fill="{WHITE}">NL</text>'
    )


def i_crown():
    return (
        path("M 12 70 L 20 26 L 36 46 L 50 18 L 64 46 L 80 26 L 88 70 Z", fill="#ff9d00", stroke="#d97b00", sw=3)
        + rect(12, 70, 76, 14, "#ff7a00", rx=4)
        + circ(50, 40, 6, RED) + circ(26, 46, 5, BLUE) + circ(74, 46, 5, GREEN)
    )


def i_sinterklaas():
    return (
        path("M 30 40 q 20 -30 40 0 L 74 46 L 26 46 Z", fill=RED)
        + circ(50, 58, 18, SKIN)
        + path("M 32 58 q 18 34 36 0 q -4 26 -18 26 q -14 0 -18 -26 Z", fill=WHITE, stroke=GREY, sw=3)
        + circ(43, 54, 3, INK) + circ(57, 54, 3, INK)
        + rect(24, 42, 52, 8, WHITE, rx=3)
        + circ(50, 30, 5, YELLOW)
    )


def i_globe():
    return (
        circ(50, 50, 36, SKY, stroke=BLUE_D, sw=4)
        + path("M 50 14 q -18 36 0 72 M 50 14 q 18 36 0 72", stroke=BLUE_D, sw=3)
        + line(14, 50, 86, 50, BLUE_D, 3)
        + path("M 26 32 q 14 6 10 16 q -4 10 -14 6 Z", fill=GREEN)
        + path("M 56 58 q 16 -4 18 8 q 2 12 -12 12 q -12 0 -6 -20 Z", fill=GREEN)
        + path("M 58 24 q 12 0 14 10 q -14 4 -14 -10 Z", fill=GREEN)
    )


def i_speech_bubbles():
    return (
        path("M 6 20 L 60 20 q 8 0 8 8 L 68 54 q 0 8 -8 8 L 30 62 L 16 76 L 18 62 q -12 0 -12 -8 Z",
             fill=BLUE, stroke=BLUE_D, sw=3)
        + path("M 44 44 L 94 44 q 6 0 6 6 L 100 74 q 0 6 -6 6 L 74 80 L 62 92 L 64 80 q -8 0 -8 -6 Z",
             fill=WHITE, stroke=GREY_D, sw=3)
        + line(18, 34, 54, 34, WHITE, 4) + line(18, 46, 44, 46, WHITE, 4)
        + line(64, 58, 92, 58, GREY, 3) + line(64, 68, 84, 68, GREY, 3)
    )


def i_map_pin():
    return (
        path("M 50 8 q 26 0 26 28 q 0 22 -26 56 q -26 -34 -26 -56 q 0 -28 26 -28 Z", fill=RED, stroke="#b8382e", sw=3)
        + circ(50, 36, 11, WHITE)
        + path("M 44 34 q 6 -8 12 0 q -6 8 -12 0 Z", fill=RED)
    )


def i_eiffel():
    return (
        path("M 50 8 L 58 30 L 68 60 L 84 92 L 62 92 L 50 66 L 38 92 L 16 92 L 32 60 L 42 30 Z",
             fill="#8d7a5e", stroke=BROWN_D, sw=2)
        + rect(36, 44, 28, 6, "#8d7a5e")
        + rect(30, 62, 40, 6, "#8d7a5e")
        + circ(50, 8, 4, GREY_D)
    )


def i_bigben():
    return (
        rect(32, 30, 36, 62, "#c9b18a", rx=3, stroke=BROWN, sw=3)
        + poly([(28, 32), (50, 6), (72, 32)], "#8a6b3a")
        + circ(50, 46, 13, WHITE, stroke=INK, sw=3)
        + line(50, 46, 50, 38, INK, 3) + line(50, 46, 56, 50, INK, 3)
        + rect(40, 66, 20, 26, BROWN, rx=2)
    )


def i_beach():
    return (
        rect(0, 40, 100, 26, WATER)
        + path("M 0 66 q 30 -8 50 0 q 22 8 50 0 L 100 100 L 0 100 Z", fill=SAND)
        + circ(78, 24, 14, YELLOW)
        + path("M 26 66 L 26 34", stroke=BROWN, sw=4)
        + path("M 26 34 q -18 2 -20 14 q 14 -6 20 -14 Z", fill=GREEN)
        + path("M 26 34 q 18 2 20 14 q -14 -6 -20 -14 Z", fill=GREEN_D)
        + path("M 26 34 q -4 -16 6 -20 q 2 12 -6 20 Z", fill=GREEN)
        + ell(60, 82, 16, 5, "#e8c98a")
    )


def i_sea_sun():
    return (
        circ(72, 26, 16, YELLOW)
        + rect(0, 46, 100, 54, WATER, rx=2)
        + "".join(path(f"M 0 {54 + i * 14} q 14 -8 26 0 t 26 0 t 26 0 t 26 0", stroke=WHITE, sw=3) for i in range(3))
        + poly([(14, 46), (22, 26), (30, 46)], "#f0e2c0")
    )


def i_mountains():
    return (
        poly([(4, 84), (34, 26), (62, 84)], "#7c8f9e")
        + poly([(20, 84), (34, 26), (48, 84)], "#9fb2c0")
        + poly([(24, 40), (34, 26), (44, 40)], WHITE)
        + poly([(48, 84), (72, 40), (96, 84)], "#68798a")
        + poly([(64, 52), (72, 40), (80, 52)], WHITE)
        + rect(0, 84, 100, 12, GREEN_D, rx=2)
    )


def i_waterside():
    return (
        rect(0, 52, 100, 48, WATER, rx=2)
        + "".join(path(f"M 0 {60 + i * 12} q 14 -7 26 0 t 26 0 t 26 0 t 26 0", stroke=WHITE, sw=3) for i in range(3))
        + rect(0, 40, 100, 12, GREEN, rx=2)
        + person(24, 8, 0.6, RED, legs=False)
        + person(46, 10, 0.6, BLUE, legs=False)
        + ell(78, 48, 14, 5, BROWN)
    )


def i_island():
    return (
        rect(0, 58, 100, 42, WATER, rx=2)
        + ell(50, 66, 36, 14, SAND)
        + line(50, 64, 46, 26, BROWN, 5)
        + path("M 46 26 q -22 0 -26 14 q 18 -6 26 -8 Z", fill=GREEN)
        + path("M 46 26 q 22 0 26 14 q -18 -6 -26 -8 Z", fill=GREEN_D)
        + path("M 46 26 q -6 -18 6 -22 q 4 14 -6 22 Z", fill=GREEN)
        + circ(80, 26, 12, YELLOW)
    )


def i_football():
    out = circ(50, 50, 34, WHITE, stroke=INK, sw=4)
    out += poly([(50, 32), (65, 43), (59, 61), (41, 61), (35, 43)], INK)
    for a in (0, 72, 144, 216, 288):
        out += grp(line(50, 18, 50, 30, INK, 4), rot=a, ox=50, oy=50)
    return out


def i_dumbbell():
    return (
        rect(30, 44, 40, 12, INK, rx=4)
        + rect(16, 32, 16, 36, GREY_D, rx=5)
        + rect(68, 32, 16, 36, GREY_D, rx=5)
        + rect(6, 40, 12, 20, INK, rx=4)
        + rect(82, 40, 12, 20, INK, rx=4)
    )


def i_treadmill():
    return (
        path("M 10 78 L 76 78 L 82 90 L 4 90 Z", fill=GREY_D)
        + rect(14, 70, 62, 8, INK, rx=4)
        + line(76, 74, 84, 30, GREY_D, 5)
        + rect(66, 22, 30, 10, INK, rx=4)
        + person(40, 14, 0.85, RED, legs=False)
        + line(36, 50, 26, 70, INK, 6) + line(46, 50, 56, 68, INK, 6)
    )


def i_exercise_bike():
    return (
        circ(28, 70, 18, "none", stroke=INK, sw=6)
        + line(28, 70, 62, 34, GREY_D, 6)
        + rect(54, 26, 22, 8, INK, rx=4)
        + line(48, 46, 76, 46, GREY_D, 5)
        + circ(52, 74, 9, GREY_D)
        + person(70, 6, 0.7, BLUE, legs=False)
    )


def i_shower():
    return (
        line(76, 12, 76, 30, GREY_D, 5)
        + path("M 58 30 L 94 30 L 88 40 L 64 40 Z", fill=GREY_D)
        + "".join(line(64 + i * 6, 44, 60 + i * 6, 76, SKY, 3) for i in range(5))
        + path("M 6 84 q 20 -12 40 0 q 20 12 48 0 L 94 96 L 6 96 Z", fill=SKY)
        + circ(30, 56, 12, SKIN)
        + path("M 18 52 a 12 12 0 0 1 24 0 Z", fill=HAIR)
    )


def i_ticket():
    return (
        path("M 8 30 L 92 30 L 92 46 a 8 8 0 0 0 0 16 L 92 78 L 8 78 L 8 62 a 8 8 0 0 0 0 -16 Z",
             fill=YELLOW, stroke="#d9a300", sw=3)
        + line(50, 34, 50, 74, "#d9a300", 3)
        + f'<text x="28" y="60" text-anchor="middle" font-size="18" font-weight="800" fill="{BROWN}">&#127903;</text>'
        + "".join(line(60, 44 + i * 8, 84, 44 + i * 8, "#d9a300", 3) for i in range(3))
    )


def i_online_ticket():
    return grp(i_smartphone(), 0, 0, 0.86) + grp(i_ticket(), 22, 32, 0.52)


def i_instructions():
    return (
        rect(20, 12, 60, 76, WHITE, rx=5, stroke=INK, sw=4)
        + rect(34, 6, 32, 12, GREY_D, rx=4)
        + person(50, 26, 0.5, RED, legs=False)
        + line(38, 44, 26, 56, RED, 4) + line(62, 44, 74, 56, RED, 4)
        + "".join(line(30, 66 + i * 9, 70, 66 + i * 9, GREY_L, 3) for i in range(2))
    )


def i_tire():
    return (
        circ(50, 50, 38, INK)
        + circ(50, 50, 22, GREY_L, stroke=GREY_D, sw=3)
        + circ(50, 50, 8, GREY_D)
        + "".join(grp(rect(46, 8, 8, 10, GREY_D, rx=2), rot=a, ox=50, oy=50) for a in range(0, 360, 45))
    )


def i_oil_can():
    return (
        path("M 16 46 L 62 46 L 62 84 q 0 6 -6 6 L 22 90 q -6 0 -6 -6 Z", fill=GREEN_D, stroke=INK, sw=3)
        + rect(28, 34, 22, 12, GREEN_D, rx=3)
        + path("M 62 56 L 92 34", stroke=GREY_D, sw=6)
        + path("M 34 60 q 4 8 8 0 q -4 -6 -8 0 Z", fill=YELLOW)
        + circ(90, 40, 5, "#c9a300")
    )


def i_bricks():
    out = ""
    for r in range(4):
        off = 0 if r % 2 == 0 else -12
        for c in range(4):
            x = 6 + off + c * 24
            if -20 < x < 96:
                out += rect(x, 34 + r * 15, 22, 13, "#c0553f", rx=2, stroke="#8f3d2d", sw=2)
    return out


def i_wall():
    """Half-built wall + trowel — deliberately distinct from the plain brick stack."""
    out = ""
    for r in range(3):
        off = 0 if r % 2 == 0 else -12
        cols = 4 if r < 2 else 2
        for c in range(cols):
            x = 6 + off + c * 24
            if -20 < x < 96:
                out += rect(x, 46 + r * 15, 22, 13, "#c0553f", rx=2, stroke="#8f3d2d", sw=2)
    out += rect(0, 88, 100, 10, GREY, rx=2)
    out += path("M 56 44 L 88 22 L 96 32 L 64 52 Z", fill=GREY_L, stroke=GREY_D, sw=3)
    out += rect(50, 42, 14, 8, BROWN, rx=3)
    out += rect(6, 20, 40, 10, "#e8dcc0", rx=3, stroke=GREY_D, sw=2)
    return out


def i_roof():
    return (
        poly([(6, 74), (50, 24), (94, 74)], "#b0543f")
        + "".join(line(14 + i * 12, 74, 26 + i * 12, 56, "#8f3d2d", 3) for i in range(6))
        + rect(0, 74, 100, 10, BROWN, rx=2)
        + rect(66, 30, 10, 18, GREY_D, rx=2)
    )


def i_mop_floor():
    return (
        line(64, 10, 44, 68, BROWN, 5)
        + path("M 26 68 L 62 68 L 56 88 L 32 88 Z", fill=BLUE)
        + rect(0, 88, 100, 10, GREY_L, rx=2)
        + path("M 12 78 q 8 -8 16 0", stroke=SKY, sw=3)
        + circ(80, 76, 12, YELLOW, stroke="#d9a300", sw=3)
    )


def i_toilet():
    return (
        rect(28, 12, 40, 30, WHITE, rx=4, stroke=GREY_D, sw=3)
        + path("M 22 46 L 74 46 q 4 22 -12 28 L 34 74 q -14 -6 -12 -28 Z", fill=WHITE, stroke=GREY_D, sw=3)
        + rect(30, 74, 30, 16, WHITE, stroke=GREY_D, sw=3)
        + circ(60, 20, 5, GREY)
        + path("M 78 60 q 6 8 0 14 q -6 -6 0 -14 Z", fill=SKY)
    )


def i_window_clean():
    return (
        rect(12, 12, 76, 72, SKY, rx=4, stroke=BROWN, sw=5)
        + line(50, 12, 50, 84, BROWN, 5) + line(12, 48, 88, 48, BROWN, 5)
        + path("M 22 30 l 10 10 M 30 24 l 8 8", stroke=WHITE, sw=4)
        + rect(56, 62, 26, 10, YELLOW, rx=3, stroke="#d9a300", sw=2)
        + line(62, 72, 62, 84, GREY_D, 3)
    )


def i_birthday_cake():
    return (
        rect(14, 48, 72, 34, "#f2c6d8", rx=6, stroke=PINK, sw=3)
        + rect(14, 58, 72, 8, "#c9773f")
        + "".join(line(28 + i * 16, 34, 28 + i * 16, 48, WHITE, 5) for i in range(4))
        + "".join(ell(28 + i * 16, 30, 3, 5, ORANGE) for i in range(4))
        + rect(8, 82, 84, 10, GREY_L, rx=4)
    )


def i_party():
    return (
        path("M 10 88 L 44 34 L 62 46 Z", fill=RED, stroke="#b8382e", sw=3)
        + circ(52, 26, 7, YELLOW) + circ(72, 40, 6, BLUE) + circ(84, 20, 6, GREEN)
        + circ(66, 14, 5, PURPLE) + circ(88, 52, 5, ORANGE)
        + poly([(74, 62), (82, 70), (74, 78), (66, 70)], PINK)
        + circ(30, 62, 4, YELLOW)
    )


def i_disco():
    return (
        circ(50, 34, 22, GREY_L, stroke=GREY_D, sw=3)
        + "".join(line(30, 26 + i * 8, 70, 26 + i * 8, GREY_D, 2) for i in range(3))
        + line(50, 6, 50, 12, GREY_D, 4)
        + path("M 28 56 L 10 92 M 72 56 L 90 92", stroke=YELLOW, sw=6)
        + person(26, 58, 0.55, PINK) + person(74, 58, 0.55, PURPLE)
    )


def i_cheese_wine():
    return grp(i_wine(), -14, 0, 0.8) + grp(i_pasta(), 30, 20, 0.7)


def i_bill():
    return (
        path("M 18 10 L 82 10 L 82 84 L 70 76 L 58 84 L 46 76 L 34 84 L 22 76 L 18 84 Z", fill=WHITE, stroke=GREY_D, sw=3)
        + "".join(line(28, 26 + i * 12, 72, 26 + i * 12, GREY_L, 3) for i in range(3))
        + f'<text x="50" y="70" text-anchor="middle" font-size="20" font-weight="800" fill="{RED}">&#8364;</text>'
    )


def i_euro_coins():
    return (
        ell(34, 74, 24, 9, "#e8c05a") + rect(10, 58, 48, 16, "#e8c05a") + ell(34, 58, 24, 9, "#f2d47a")
        + ell(68, 52, 22, 8, "#e8c05a") + rect(46, 38, 44, 14, "#e8c05a") + ell(68, 38, 22, 8, "#f2d47a")
        + f'<text x="68" y="44" text-anchor="middle" font-size="14" font-weight="800" fill="#a8811f">&#8364;</text>'
    )


def i_hard_drop():
    return i_licorice()


def i_dutch_flag():
    return (
        rect(10, 26, 80, 18, RED, rx=2)
        + rect(10, 44, 80, 18, WHITE)
        + rect(10, 62, 80, 18, BLUE_D, rx=2)
        + rect(10, 26, 80, 54, "none", stroke=GREY_D, sw=2)
        + line(6, 20, 6, 92, BROWN, 4)
    )


def i_city_sign():
    return (
        rect(12, 30, 76, 34, BLUE, rx=4, stroke=WHITE, sw=3)
        + f'<text x="50" y="53" text-anchor="middle" font-size="17" font-weight="800" fill="{WHITE}">STAD</text>'
        + rect(46, 64, 8, 30, GREY_D)
        + rect(30, 92, 40, 6, GREY, rx=2)
    )


def i_station():
    return (
        rect(8, 30, 84, 46, "#dfe7ef", rx=4, stroke=GREY_D, sw=3)
        + poly([(4, 32), (50, 12), (96, 32)], BLUE_D)
        + grp(i_train(), 22, 34, 0.5)
        + rect(8, 76, 84, 8, GREY_D, rx=3)
    )


def i_glasses_ogen():
    return (
        circ(28, 52, 18, "none", stroke=INK, sw=5)
        + circ(72, 52, 18, "none", stroke=INK, sw=5)
        + line(46, 52, 54, 52, INK, 5)
        + line(10, 46, 2, 38, INK, 5) + line(90, 46, 98, 38, INK, 5)
    )


ICONS = {name[2:]: fn for name, fn in list(globals().items()) if name.startswith("i_")}


# --------------------------------------------------------------------------
# per-item scenes
# --------------------------------------------------------------------------

# id -> list of 1..3 icon names (3 => numbered strip, as "gebruik alle plaatjes")
SCENES = {
    763: ["beach", "calendar"],
    764: ["globe", "speech_bubbles"],
    765: ["family"],
    766: ["alarm", "coffee"],
    767: ["row_houses", "neighbours"],
    768: ["dumbbell", "vegetables", "no_alcohol"],
    769: ["walking", "broken_car"],
    770: ["bicycle", "clock"],
    771: ["music", "cinema"],
    772: ["snackbar", "restaurant"],
    773: ["tire", "oil_can", "car_wash"],
    774: ["ticket", "instructions", "meal_tray"],
    775: ["modern_room", "classic_room"],
    776: ["city", "map_pin"],
    777: ["angry", "bill"],
    778: ["muesli", "fruit_bowl", "tea"],
    779: ["canal_houses", "museum", "crowd"],
    780: ["house_garden", "island"],
    781: ["cinema", "ticket"],
    782: ["theatre", "online_ticket"],
    783: ["bus", "taxi", "bicycle"],
    784: ["train", "beach"],
    785: ["online_shopping", "email", "video_call"],
    786: ["headphones", "books", "pen_paper"],
    787: ["gift", "flowers"],
    788: ["city_sign", "calendar"],
    789: ["open_book", "tv"],
    790: ["dutch_flag", "hourglass"],
    791: ["school", "children_class"],
    792: ["teacher", "cleaner"],
    793: ["keyboard_coffee", "keyboard"],
    794: ["inbox_many", "trash_email"],
    795: ["sleeping", "sun"],
    796: ["train", "airplane"],
    797: ["plate_food", "wine", "two_people"],
    798: ["street_musician", "dancer", "painter"],
    799: ["bus", "clock"],
    800: ["tv", "tv_football"],
    801: ["apple", "calendar"],
    802: ["rain", "sun_cloud"],
    803: ["smartphone", "phone_call"],
    804: ["alarm", "traffic_jam", "phone_call"],
    805: ["sinterklaas", "gift"],
    806: ["crown", "orange_shirt"],
    807: ["city", "village"],
    808: ["flat_building", "house_garden"],
    809: ["city", "shopping_bags", "terrace"],
    810: ["bicycle", "walking", "waterside"],
    811: ["clock", "dinner_table"],
    812: ["music", "headphones"],
    813: ["cat", "dog"],
    814: ["licence", "steering_wheel"],
    815: ["calendar_check", "clock"],
    816: ["museum", "camera"],
    817: ["villa", "price_tag"],
    818: ["floorplan"],
    819: ["teacher", "cooking_pot"],
    820: ["office_worker", "nurse"],
    821: ["sandwich", "coffee", "laptop"],
    822: ["fruit_bowl", "vegetables", "cookies"],
    823: ["city", "map_pin"],
    824: ["dinner_table", "house_garden"],
    825: ["classroom", "hourglass"],
    826: ["sweater", "umbrella"],
    827: ["sun", "rain"],
    828: ["eiffel", "camera"],
    829: ["swimmer", "calendar"],
    830: ["runner", "alone"],
    831: ["painting", "museum"],
    832: ["licorice", "apple_pie"],
    833: ["bricks", "wall", "roof"],
    834: ["mop_floor", "toilet", "window_clean"],
    835: ["bicycle", "car"],
    836: ["steering_wheel", "traffic_jam"],
    837: ["radio", "music"],
    838: ["party", "disco"],
    839: ["friends_visit", "dinner_table"],
    840: ["snow", "sun"],
    841: ["backpacks", "island"],
    842: ["camera", "bigben"],
    843: ["bicycle", "calendar"],
    844: ["football", "children_sport"],
    845: ["bikes_row", "boat", "canal_houses"],
    846: ["tulips", "windmill", "clog"],
    847: ["dog", "cat"],
    848: ["hotel", "sea_sun"],
    849: ["eiffel", "train"],
    850: ["birthday_cake", "party"],
    851: ["smartphone", "family"],
    852: ["rain", "sun"],
    853: ["pasta", "price_tag"],
    854: ["market", "mother_daughter"],
    855: ["laptop", "desktop"],
    856: ["social_media", "smartphone"],
    857: ["treadmill", "exercise_bike", "shower"],
    858: ["tv_football", "beer", "orange_shirt"],
    859: ["clothes_shop", "shopping_cart"],
    860: ["beach", "mountains", "city"],
    861: ["globe", "island"],
    862: ["second_hand", "sofa"],
    863: ["cooking_pot", "pasta"],
    864: ["runner", "swimmer"],
    865: ["butcher", "knife"],
    866: ["clothes_shop", "city"],
    867: ["supermarket", "online_shopping"],
    868: ["coffee", "tea"],
    869: ["speed_camera", "bill", "police_office"],
    870: ["tea", "car_mirror", "smartphone"],
}


def i_cat():
    return (
        ell(50, 62, 30, 26, "#9aa5b1")
        + poly([(26, 44), (30, 20), (46, 38)], "#9aa5b1")
        + poly([(74, 44), (70, 20), (54, 38)], "#9aa5b1")
        + circ(40, 58, 4, INK) + circ(60, 58, 4, INK)
        + path("M 44 70 q 6 6 12 0", stroke=INK, sw=3)
        + line(20, 66, 34, 68, INK, 2) + line(20, 74, 34, 72, INK, 2)
        + line(80, 66, 66, 68, INK, 2) + line(80, 74, 66, 72, INK, 2)
        + path("M 78 82 q 18 -4 12 -22", stroke="#9aa5b1", sw=6)
    )


def i_dog():
    return (
        ell(50, 62, 28, 24, "#c9944a")
        + ell(24, 54, 10, 18, "#a87a37") + ell(76, 54, 10, 18, "#a87a37")
        + circ(41, 58, 4, INK) + circ(59, 58, 4, INK)
        + ell(50, 70, 8, 6, INK)
        + path("M 44 78 q 6 6 12 0", stroke=INK, sw=3)
        + path("M 78 78 q 16 -6 10 -22", stroke="#c9944a", sw=6)
    )


ICONS["cat"] = i_cat
ICONS["dog"] = i_dog


# --------------------------------------------------------------------------
# render
# --------------------------------------------------------------------------

SMALL_WORDS = {"and", "in", "the", "of"}


def topic_title(topic):
    words = topic.split("-")
    out = []
    for i, w in enumerate(words):
        out.append(w if (i and w in SMALL_WORDS) else w.capitalize())
    return " ".join(out)


# panel geometry: (x, y, w, h) and (icon translate x/y, scale)
LAYOUTS = {
    1: ([(170, 86, 460, 368)], 2.6),
    2: ([(60, 96, 320, 348), (420, 96, 320, 348)], 2.2),
    3: ([(36, 110, 228, 320), (286, 110, 228, 320), (536, 110, 228, 320)], 1.7),
}


def render(item):
    topic = item["topic"]
    c0, c1, cap = TOPICS[topic]
    names = SCENES[item["id"]]
    boxes, scale = LAYOUTS[len(names)]
    uid = item["id"]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"'
        f" font-family=\"'Segoe UI',system-ui,-apple-system,sans-serif\">",
        "<defs>",
        f'<linearGradient id="bg{uid}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{c0}"/><stop offset="1" stop-color="{c1}"/></linearGradient>',
        f'<filter id="sh{uid}" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="#0b1220" flood-opacity="0.18"/></filter>',
        "</defs>",
        f'<rect width="{W}" height="{H}" rx="36" fill="url(#bg{uid})"/>',
        f'<circle cx="678" cy="120" r="150" fill="#ffffff" opacity="0.14"/>',
        f'<circle cx="120" cy="500" r="120" fill="#ffffff" opacity="0.10"/>',
    ]

    for idx, (name, (bx, by, bw, bh)) in enumerate(zip(names, boxes)):
        icon = ICONS[name]()
        parts.append(f'<g filter="url(#sh{uid})"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}"'
                     f' rx="28" fill="#ffffff"/></g>')
        cx, cy = bx + bw / 2, by + bh / 2
        side = 100 * scale
        parts.append(grp(icon, round(cx - side / 2, 1), round(cy - side / 2, 1), scale))
        if len(names) > 1:
            parts.append(circ(bx + 26, by + 26, 17, cap))
            parts.append(
                f'<text x="{bx + 26}" y="{by + 32}" text-anchor="middle" font-size="19"'
                f' font-weight="800" fill="#ffffff">{idx + 1}</text>'
            )

    parts.append(
        f'<text x="400" y="512" text-anchor="middle" font-size="34" font-weight="800"'
        f' fill="{cap}">{esc(topic_title(topic))}</text>'
    )
    parts.append(
        f'<text x="400" y="548" text-anchor="middle" font-size="17" font-weight="600"'
        f' letter-spacing="3" fill="{cap}" opacity="0.55">A2 &#183; SPREEKEXAMEN</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    items = json.load(open(DATA, encoding="utf-8"))
    os.makedirs(OUT_DIR, exist_ok=True)
    missing = sorted({n for i in items for n in SCENES.get(i["id"], []) if n not in ICONS})
    if missing:
        raise SystemExit(f"missing icons: {missing}")
    unscened = [i["id"] for i in items if i["id"] not in SCENES]
    if unscened:
        raise SystemExit(f"no scene for: {unscened}")

    for item in items:
        out = os.path.join(OUT_DIR, f"{item['id']}.svg")
        with open(out, "w", encoding="utf-8") as f:
            f.write(render(item) + "\n")
    print(f"wrote {len(items)} svg files to {OUT_DIR}")
    print(f"icons defined: {len(ICONS)}, used: {len({n for v in SCENES.values() for n in v})}")


if __name__ == "__main__":
    main()
