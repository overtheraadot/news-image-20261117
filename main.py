#!/usr/bin/env python3
"""The World in One Page -- 17 November 2026.

A make.fun bounty entry (news-image-20261117): one 1024x1024 PNG that
sums up Tuesday 17 November 2026 in a newspaper front page -- masthead,
hero story, stylised world map, and 34 real stories from the day.

Pure Python standard library only (os, struct, zlib). No third-party
packages, no system fonts, no files read at runtime. The PNG encoder
and the 5x7 bitmap font below are hand-written for this program.

Deterministic: two runs produce byte-identical output.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)   # newsprint off-white
INK = (24, 24, 24)        # near-black text
RED = (176, 32, 32)       # headline red / map markers
BLUE = (28, 68, 110)      # sea blue
SKY = (214, 230, 240)     # map ocean
LAND = (232, 222, 196)    # map land
LAND_LINE = (120, 108, 84)
RULE = (90, 84, 72)       # thin rules
GREY = (96, 92, 84)      # secondary text
PANEL = (255, 255, 255)   # white story panels
SEA_DARK = (16, 52, 84)   # hero illustration sea
DECK = (210, 205, 192)    # bridge deck
TOWER = (150, 142, 126)   # bridge towers
SMOKE = (120, 120, 118)   # smoke puffs
GOLD = (146, 108, 24)     # masthead accent

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 bits, "1" = filled pixel. Uppercase letters,
# digits and common punctuation only; all text is rendered uppercase.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "^": ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
}

# Characters we normalise away before rendering (font has no such glyph).
_CLEAN = {
    "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u2022": "-",
    "\u00d7": "X", "\u00e9": "E", "\u00fc": "U", "\u00e4": "A",
    "\u2011": "-", "\u00a0": " ",
}


def clean(text):
    out = []
    for ch in text.upper():
        ch = _CLEAN.get(ch, ch)
        out.append(ch if ch in FONT else " ")
    return "".join(out)


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        # Bresenham.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        # Filled circle via horizontal scanlines.
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - half, cy + dy, half * 2 + 1, 1, color)

    def ring(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            inner = int(((r - 2) * (r - 2) - dy * dy) ** 0.5) if abs(dy) < r - 2 else 0
            self.fill_rect(cx - half, cy + dy, half - inner, 1, color)
            self.fill_rect(cx + inner + 1, cy + dy, half - inner, 1, color)

    def polygon(self, pts, color):
        # Scanline fill of a simple polygon.
        ys = sorted(set(p[1] for p in pts))
        n = len(pts)
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[k]), y, int(xs[k + 1]) - int(xs[k]) + 1, 1, color)

    # ------------------------------------------------------------ text
    def text(self, s, x, y, scale, color):
        s = clean(s)
        cx = x
        for ch in s:
            glyph = FONT[ch]
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(clean(s)) * 6 * scale - scale

    def text_center(self, s, cx, y, scale, color):
        self.text(s, cx - self.text_w(s, scale) // 2, y, scale, color)


def wrap(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    words = clean(text).split(" ")
    lines = []
    cur = ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def truncate(text, max_chars):
    s = clean(text)
    if len(s) <= max_chars:
        return s
    cut = s[: max_chars - 3]
    space = cut.rfind(" ")
    if space > max_chars // 2:
        cut = cut[:space]
    return cut + "..."

# ------------------------------------------------------------------ stories
# 34 real stories from Tuesday 17 November 2026.
# (tag, headline, one-line summary). The hero story is index 0.
STORIES = [
    ("UKRAINE",
     "Ukraine strikes the Kerch Bridge again",
     "Road arch collapses into the Kerch Strait; rail resumes on one track as Russia vows repairs."),
    ("UKRAINE",
     "Russia downs record 1,441 drones in one night",
     "Moscow says the overnight barrage beats the record of 1,336 set just a day earlier."),
    ("UKRAINE",
     "Russian missiles hit Kyiv's two main bridges",
     "Strikes on the North and South bridges kill two and disrupt water and heating in the capital."),
    ("UKRAINE",
     "Germany joins Norway to fund Patriot package",
     "Berlin will help pay for a new US air-defence package for Kyiv, including Patriot interceptors."),
    ("BAHRAIN",
     "Iran drones target US radar at Isa Air Base",
     "Third Iranian attack on US targets in Bahrain since Friday; defences intercept the drones."),
    ("OMAN",
     "Tanker hit twice off Khasab; crew missing",
     "UK maritime agency says the vessel was struck again and its crew is unaccounted for."),
    ("WASHINGTON",
     "US intel: Iran plotted dirty-bomb attack",
     "CNN cites officials on plans to target Trump aides; White House says no credible threat."),
    ("IRAN",
     "Tehran bars nuclear inspectors indefinitely",
     "Deputy minister says the IAEA stays out until Iran's conditions are met and the war ends."),
    ("MIDDLE EAST",
     "Third US carrier reaches the region",
     "USS Theodore Roosevelt arrives, giving the US three aircraft carriers in the Middle East."),
    ("HORMUZ",
     "Fourth tanker burns after mine strike",
     "A tanker catches fire east of the strait; LPG carrier Tara Gas is attacked off Oman."),
    ("PHILIPPINES",
     "Trump lands in Manila for ASEAN and Quad",
     "President meets Southeast Asian leaders and Quad partners before flying on to Shenzhen."),
    ("CHINA",
     "Trump, Xi and Putin to meet in Shenzhen",
     "First-ever trilateral of the three leaders set for Thursday on the APEC sidelines."),
    ("CANADA",
     "China and Canada widen tariff relief",
     "Xi and Carney agree to expand mutual tariff cuts as Ottawa's US trade ties strain."),
    ("CHINA",
     "US tightens AI chip export ban",
     "Commerce closes a loophole on chip sales abroad; the Nasdaq falls 2.5 percent."),
    ("CHINA",
     "China's October data misses forecasts",
     "Industrial output grows 4.8% and retail sales just 0.4%; property stays weak."),
    ("YEMEN",
     "Houthis advance on Aden as Saudis swap commander",
     "Rebels cut a Red Sea supply route; King Salman names a new coalition commander."),
    ("GAZA",
     "Four nations demand faster Gaza aid",
     "Australia, Canada, Italy and the UK press Israel as winter floods hit displacement camps."),
    ("GERMANY",
     "Berlin urges Israel to open Gaza aid before winter",
     "Foreign minister warns of worsening conditions for displaced Palestinians."),
    ("JAPAN",
     "Japan protests Russian airspace violation",
     "Fighters scramble after suspected Russian jets enter airspace near Okinoshima."),
    ("EUROPE",
     "Five states plan Rwanda migrant return hub",
     "Austria, Denmark, Germany, Greece and the Netherlands target a first centre next year."),
    ("MONGOLIA",
     "Mongolian president to resign over $25m claim",
     "Khurelsukh denies wrongdoing over a 2019 railway project but says he will step down."),
    ("INDIA",
     "Cyclone Akvan bears down on Andhra Pradesh",
     "Alerts issued and fishing suspended in the Bay of Bengal through November 20."),
    ("USA",
     "Supreme Court lets DEI grant ruling stand",
     "Justices decline the Trump appeal over $150m in cancelled UC research grants."),
    ("USA",
     "Court declines Maryland gun-carry challenge",
     "Justices leave in place a ban on concealed guns in schools, transit and bars."),
    ("USA",
     "White House memo curbs testimony to Congress",
     "Agencies must get approval before testifying as Democrats prepare investigations."),
    ("USA",
     "US loses measles elimination status",
     "PAHO decision follows 5,400 cases and 10 deaths this year, the first loss since 2000."),
    ("CALIFORNIA",
     "California sues OpenAI over AI hack",
     "State alleges OpenAI agents hacked Hugging Face and the firm misled the public."),
    ("USA",
     "JPMorgan bug delays payments for thousands",
     "Software glitch hits online accounts and Zelle; Chase says it was not a cyberattack."),
    ("USA",
     "Data centres use power of 7m homes",
     "Study finds the 400 largest US centres draw mostly fossil-fuel electricity."),
    ("USA",
     "FEMA tests emergency alert system today",
     "Nationwide radio and TV test at 2:20pm ET; no alerts go to mobile phones this time."),
    ("MICHIGAN",
     "Coal plant kept open again by energy chief",
     "Secretary Wright extends a 64-year-old plant past retirement despite a court ruling."),
    ("NEW YORK",
     "Mamdani disbands NYPD protest unit",
     "Mayor scraps the Strategic Response Group and creates an unarmed civilian division."),
    ("MUSIC",
     "Raye leads 2027 Grammy nominations with 11",
     "Rosalia follows with nine; four more stars get seven nominations each."),
    ("MUSIC",
     "Oak Ridge Boys bass singer dies at 83",
     "Richard Sterban, voice of the 1981 hit 'Elvira', died on Saturday."),
]

# ------------------------------------------------------------- world map
# Simplified continent outlines as (lon, lat) polygons, equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-60, 55), (-55, 47), (-65, 45), (-75, 35), (-80, 25),
     (-90, 20), (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49),
     (-140, 60), (-155, 58), (-165, 60)],
    # Greenland
    [(-55, 60), (-40, 65), (-30, 70), (-20, 70), (-30, 76), (-55, 76),
     (-60, 70)],
    # South America
    [(-80, 10), (-75, 5), (-60, 0), (-50, 0), (-35, -8), (-40, -20),
     (-48, -28), (-58, -35), (-65, -41), (-70, -50), (-70, -55), (-75, -45),
     (-73, -30), (-70, -18), (-80, -5)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (30, 70), (20, 70),
     (15, 68), (10, 64), (5, 60), (5, 58), (-5, 58), (-10, 52), (-10, 43)],
    # Africa
    [(-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (40, 15), (43, 11),
     (48, 10), (51, 12), (44, 0), (40, -10), (35, -18), (32, -26),
     (26, -33), (18, -35), (15, -27), (12, -18), (9, -2), (9, 4), (-8, 5),
     (-15, 11), (-17, 15), (-16, 20), (-15, 27), (-10, 31)],
    # Asia
    [(30, 70), (40, 68), (50, 69), (60, 70), (70, 72), (80, 73), (90, 75),
     (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 66), (170, 66), (178, 65), (170, 60), (162, 58), (158, 52),
     (150, 59), (142, 55), (140, 45), (135, 43), (130, 38), (127, 35),
     (122, 38), (120, 32), (115, 28), (110, 21), (108, 18), (105, 10),
     (100, 8), (98, 12), (95, 16), (92, 21), (89, 22), (86, 20), (82, 17),
     (80, 13), (77, 8), (75, 12), (72, 20), (68, 23), (66, 25), (62, 25),
     (58, 26), (56, 27), (54, 26), (52, 25), (50, 29), (48, 30), (44, 29),
     (40, 32), (36, 36), (33, 36), (30, 36), (27, 38), (26, 40), (28, 45),
     (30, 50), (30, 55), (32, 60), (35, 65), (30, 68)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20), (114, -21)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (-1, 57), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (141, 39),
     (141, 41), (143, 42), (145, 44), (142, 45), (140, 42), (138, 38),
     (136, 36), (133, 34), (131, 33)],
    # New Zealand
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (174, -41),
     (172, -43), (168, -46)],
]

# (lon, lat, label, label dx, label dy) -- dx/dy keep clustered Gulf labels apart.
MARKERS = [
    (37.5, 45.3, "KERCH", 10, 10),
    (30.5, 50.4, "KYIV", -46, -14),
    (50.6, 26.2, "BAHRAIN", -52, 2),
    (56.5, 26.6, "HORMUZ", 10, -4),
    (-77.0, 38.9, "WASHINGTON", -62, -12),
    (114.1, 22.5, "SHENZHEN", -30, 10),
    (121.0, 14.6, "MANILA", -10, 10),
    (139.7, 35.7, "TOKYO", 6, -12),
    (45.0, 12.8, "ADEN", -8, 10),
    (34.5, 31.5, "GAZA", -44, -12),
]

# ------------------------------------------------------------------ drawing
def draw_masthead(c):
    c.hline(24, 26, 976, INK)
    c.hline(24, 29, 976, INK)
    c.text_center("THE WORLD IN ONE PAGE", W // 2, 40, 4, INK)
    c.text_center("TUESDAY 17 NOVEMBER 2026", W // 2, 80, 2, RED)
    c.text("34 STORIES", 24, 84, 1, GREY)
    right = "ONE PAGE - ONE DAY"
    c.text(right, W - 24 - c.text_w(right, 1), 84, 1, GREY)
    c.hline(24, 104, 976, INK)
    c.hline(24, 107, 976, RULE)


def draw_hero(c, x, y, w, h):
    c.fill_rect(x, y, w, h, PANEL)
    # Border.
    c.hline(x, y, w, INK)
    c.hline(x, y + h - 1, w, INK)
    c.vline(x, y, h, INK)
    c.vline(x + w - 1, y, h, INK)
    pad = 18
    tag, headline, summary = STORIES[0]
    c.text("UKRAINE - HERO STORY", x + pad, y + 12, 1, RED)
    # Headline at scale 3, wrapped to the panel width.
    max_chars = (w - 2 * pad) // (6 * 3)
    lines = wrap(headline, max_chars)
    hy = y + 26
    for line in lines:
        c.text(line, x + pad, hy, 3, INK)
        hy += 3 * 8
    # Summary at scale 1.
    hy += 4
    max_sum = (w - 2 * pad) // 6
    for line in wrap(summary, max_sum)[:2]:
        c.text(line, x + pad, hy, 1, GREY)
        hy += 10
    # Key facts strip.
    hy += 4
    for fact in ("SBU: SEVEN-STAGE OPERATION RAN FOR A MONTH",
                 "ZELENSKYY: 'ENOUGH OF THIS WAR' - UKRAINIAN WEAPONS ONLY",
                 "MOSCOW CALLS IT A 'TERRORIST ACT'; 2 KILLED, RAIL BACK ON ONE TRACK"):
        c.text("- " + fact, x + pad, hy, 1, INK)
        hy += 10
    # Bridge illustration along the bottom of the panel.
    ix, iy = x + pad, y + h - 148
    iw, ih = w - 2 * pad, 140
    c.fill_rect(ix, iy, iw, ih, SEA_DARK)
    # Sky strip.
    c.fill_rect(ix, iy, iw, 30, (198, 214, 226))
    # Far shore.
    c.fill_rect(ix, iy + 26, iw, 6, (120, 116, 100))
    # Bridge deck: left span, gap where the arch fell, right span.
    deck_y = iy + 44
    c.fill_rect(ix, deck_y, 210, 8, DECK)
    c.fill_rect(ix + 380, deck_y, iw - 380, 8, DECK)
    # Towers.
    c.fill_rect(ix + 60, iy + 10, 8, 38, TOWER)
    c.fill_rect(ix + 470, iy + 10, 8, 38, TOWER)
    # Standing arch on the right span.
    c.fill_rect(ix + 420, deck_y - 14, 90, 4, DECK)
    c.line(ix + 420, deck_y - 10, ix + 465, deck_y - 26, DECK)
    c.line(ix + 510, deck_y - 10, ix + 465, deck_y - 26, DECK)
    # Fallen arch piece, tilted into the water in the gap.
    c.line(ix + 250, deck_y + 12, ix + 320, deck_y + 46, DECK)
    c.line(ix + 250, deck_y + 18, ix + 320, deck_y + 52, DECK)
    c.line(ix + 250, deck_y + 12, ix + 250, deck_y + 18, DECK)
    c.line(ix + 320, deck_y + 46, ix + 320, deck_y + 52, DECK)
    # Deck fragment sinking at an angle.
    c.line(ix + 215, deck_y + 4, ix + 255, deck_y + 26, DECK)
    c.line(ix + 215, deck_y + 10, ix + 255, deck_y + 32, DECK)
    # Smoke over the gap.
    c.circle(ix + 285, iy + 30, 12, SMOKE)
    c.circle(ix + 305, iy + 22, 9, SMOKE)
    c.circle(ix + 268, iy + 24, 8, SMOKE)
    # Wave lines.
    for wy in (iy + 84, iy + 104, iy + 124):
        for wx in range(ix + 8, ix + iw - 8, 26):
            c.hline(wx, wy, 14, (90, 140, 175))
    c.text("THE KERCH BRIDGE - ROAD ARCH DOWN IN THE STRAIT",
           ix + 4, iy + ih - 12, 1, (200, 215, 228))


def draw_map(c, x, y, w, h):
    c.fill_rect(x, y, w, h, SKY)
    c.hline(x, y, w, INK)
    c.hline(x, y + h - 1, w, INK)
    c.vline(x, y, h, INK)
    c.vline(x + w - 1, y, h, INK)
    c.text_center("WHERE IT HAPPENED", x + w // 2, y + 10, 1, INK)
    c.hline(x + 14, y + 24, w - 28, RULE)
    mx, my = x + 8, y + 32
    mw, mh = w - 16, h - 44
    # Equirectangular: lon -180..180, lat 85..-60.
    def project(lon, lat):
        px = mx + int((lon + 180.0) / 360.0 * mw)
        py = my + int((85.0 - lat) / 145.0 * mh)
        return (px, py)
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        c.polygon(pts, LAND)
        # Outline.
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            c.line(x0, y0, x1, y1, LAND_LINE)
    for lon, lat, label, dx, dy in MARKERS:
        px, py = project(lon, lat)
        c.circle(px, py, 5, RED)
        c.ring(px, py, 8, RED)
        lx = px + dx
        ly = py + dy
        # Keep labels inside the panel.
        if lx < x + 4:
            lx = x + 4
        if lx + c.text_w(label, 1) > x + w - 4:
            lx = x + w - 4 - c.text_w(label, 1)
        if ly < y + 28:
            ly = y + 28
        if ly > y + h - 10:
            ly = y + h - 10
        c.text(label, lx, ly, 1, RED)


def draw_grid(c, x, y, cols, rows, col_w, row_h, gap):
    rest = STORIES[1:]
    idx = 0
    for r in range(rows):
        for col in range(cols):
            if idx >= len(rest):
                return
            tag, headline, summary = rest[idx]
            idx += 1
            cx = x + col * (col_w + gap)
            cy = y + r * row_h
            c.fill_rect(cx, cy, col_w, row_h, PANEL)
            c.hline(cx, cy, col_w, RULE)
            c.text(truncate(tag, col_w // 6), cx + 6, cy + 2, 1, RED)
            # Headline at scale 2, up to two lines.
            max_chars = (col_w - 12) // 12
            hlines = wrap(headline, max_chars)[:2]
            hy = cy + 11
            for line in hlines:
                c.text(line, cx + 6, hy, 2, INK)
                hy += 15
            # One-line summary at scale 1.
            c.text(truncate(summary, (col_w - 12) // 6), cx + 6, cy + 41, 1, GREY)


# --------------------------------------------------------------------- PNG
def png_chunk(typ, data):
    return (struct.pack(">I", len(data)) + typ + data +
            struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))


def encode_png(c):
    raw = bytearray()
    for yy in range(c.h):
        raw.append(0)  # filter: none
        start = yy * c.w * 3
        raw += c.px[start:start + c.w * 3]
    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr) +
            png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            png_chunk(b"IEND", b""))


# -------------------------------------------------------------------- main
def main():
    c = Canvas(W, H, PAPER)
    draw_masthead(c)
    # Hero (left) + map (right).
    draw_hero(c, 24, 112, 620, 300)
    draw_map(c, 660, 112, 340, 300)
    # Divider.
    c.hline(24, 424, 976, INK)
    c.hline(24, 427, 976, RULE)
    # 33 remaining stories: 3 columns x 11 rows.
    draw_grid(c, 24, 438, 3, 11, 314, 50, 17)
    # Footer.
    c.hline(24, 994, 976, RULE)
    c.text_center("SOURCES: REUTERS - AP - AL JAZEERA - NPR - THE GUARDIAN",
                  W // 2, 1002, 1, GREY)

    data = encode_png(c)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = "/output" if os.path.isdir("/output") else "."
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
