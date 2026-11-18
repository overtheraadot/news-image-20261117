#!/usr/bin/env python3
"""news-image-20261117 — Sum up 17 November 2026 world news in one image.

Draws a single 1024x1024 front-page PNG: masthead, hero story, a stylised
world map with markers, and a grid of 33 more real stories from Tuesday
17 November 2026 (34 stories total). Stdlib + PIL only, no network,
fully deterministic: identical input always yields byte-identical output.
"""
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BG = (248, 244, 232)
INK = (17, 17, 17)
RED = (178, 34, 34)
BLUE = (24, 62, 110)
GREY = (90, 86, 76)
LIGHT_LINE = (190, 184, 168)
MAP_BG = (214, 230, 235)
LAND = (196, 205, 170)
LAND_EDGE = (120, 130, 100)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap to pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, width, max_lines):
    """Wrap text, truncating with an ellipsis if it exceeds max_lines."""
    lines = wrap(draw, text, fnt, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "...", font=fnt) > width:
            lines[-1] = lines[-1][:-1].rstrip()
        lines[-1] = lines[-1].rstrip() + "..."
    return lines


HERO = {
    "tag": "UKRAINE  •  TOP STORY",
    "headline": "Ukraine strikes the Crimean Bridge again — a section of the road span collapses into the sea",
    "summary": ("Kyiv hailed an “unprecedented operation” weeks in the making as a second strike in "
                "under 24 hours shut the Kerch crossing; Moscow said traffic was suspended. Hours "
                "earlier, Russian missiles hit Kyiv’s Dnipro bridges, cutting heat, water and power."),
}

# (country tag, headline, one-line summary) — 33 stories, all real, 17 Nov 2026.
STORIES = [
    ("UKRAINE", "Russian missiles hit Kyiv’s Dnipro bridges",
     "North and South bridges struck; metro, heating and water disrupted."),
    ("RUSSIA", "Moscow claims 1,441 Ukrainian drones downed",
     "Largest single-day interception claim of the war, says defence ministry."),
    ("GERMANY", "Berlin to fund $300m Patriot missiles for Kyiv",
     "Norway joins the buy of PAC-2 and PAC-3 interceptors for air defence."),
    ("BAHRAIN", "Iran fires drones at US radar base in Bahrain",
     "Bahrain says the attack on Sheikh Isa base was intercepted; no casualties."),
    ("USA", "US intel: Iran plotting ‘dirty bomb’ in Washington",
     "Reports say Tehran plans to target senior Trump officials; unconfirmed."),
    ("USA", "Trump warns Iran over alleged bomb plot",
     "President says he takes the reported threat to Washington ‘very seriously’."),
    ("USA", "Vance: no ‘forever war’ with Iran",
     "Vice-president says Washington wants to limit any conflict with Tehran."),
    ("OMAN", "Tankers hit by mines near Strait of Hormuz",
     "Vessels catch fire on the key oil route; a third carrier joins the Gulf."),
    ("MIDDLE EAST", "Third US carrier reaches the Middle East",
     "USS Theodore Roosevelt joins two carriers in the region since Sunday."),
    ("CHINA", "Xi–Trump–Putin summit set for Thursday",
     "Three-way meeting confirmed for Shenzhen on the APEC sidelines, 19 Nov."),
    ("CANADA", "Canada and China agree tariff relief",
     "Deal covers about C$400m of exports; 90% of trade now gets lower tariffs."),
    ("UK", "Britain sanctions eight settlement firms",
     "UK, allies target West Bank settlement builders and an aid-blocking group."),
    ("GAZA", "West urges Israel to open Gaza aid crossings",
     "Four nations call the situation catastrophic; UN fuel convoy hit nearby."),
    ("YEMEN", "Houthis advance on Aden as army retreats",
     "Government forces pull back from the Red Sea coast to defend the port city."),
    ("SYRIA", "Nearly 4 million Syrians have returned home",
     "UN counts returns since Assad’s fall; housing and power still in ruins."),
    ("JAPAN", "Russian jets violate Japan’s airspace",
     "Tokyo scrambles fighters and protests; Taiwan also tracks Russian planes."),
    ("N. KOREA", "Kim inspects resort as Trump-meet rumours swirl",
     "Leader tours Samjiyon with his daughter; no meeting confirmed by Beijing."),
    ("MONGOLIA", "Mongolian president resigns in railway scandal",
     "Khurelsukh quits amid corruption claims; denies wrongdoing."),
    ("PHILIPPINES", "ASEAN summit opens in Manila",
     "Leaders weigh trade, sea security and a South China Sea code of conduct."),
    ("ESTONIA", "Estonia to shut Russia border from 1 December",
     "Move follows a foiled alleged Russian plot to bomb a drone plant."),
    ("PAKISTAN", "Imran Khan appeals for medical help in jail",
     "Ex-PM’s family warns his health could deteriorate in detention."),
    ("BANGLADESH", "Garment workers clash with police over pay",
     "Roads blocked in Dhaka as wage protests hit the top export industry."),
    ("SUDAN", "Drones now drive a growing share of war deaths",
     "UN-linked reports warn of a deepening humanitarian emergency."),
    ("ETHIOPIA", "Ethiopia–Eritrea border clashes flare",
     "Fighting raises fears of a wider regional war in the Horn of Africa."),
    ("SERBIA", "Student-backed MPs take seats in parliament",
     "New lawmakers sworn in after the opposition’s election win."),
    ("FRANCE", "France hit by strike; Depardieu admits assault",
     "Public-sector walkout over pay; actor drops appeal in Paris court."),
    ("USA", "Pentagon fails its ninth straight audit",
     "Auditors cannot verify accounts covering $4.8 trillion in assets."),
    ("USA", "Nvidia chief Huang resigns over affair",
     "Jensen Huang quits; signals he would return as CEO as shares slide."),
    ("USA", "Anthropic sets IPO range near $1tn value",
     "AI lab prices Nasdaq debut at $70–$78 a share amid the AI sell-off."),
    ("MARKETS", "AI sell-off deepens; bubble warnings grow",
     "Tech shares fall in Asia and the US; ex-SEC chief warns of recession risk."),
    ("SPACE", "Vulcan rocket fails, 40 satellites destroyed",
     "ULA’s first total Vulcan failure wipes out Amazon’s Leo batch."),
    ("SPACE", "Euclid maps 900 million galaxies",
     "Telescope’s first major data release also finds a record-setting quasar."),
    ("TURKIYE", "COP31 draft deal sparks tense final week",
     "Fossil-fuel wording fight escalates as climate talks enter the endgame."),
]

# Coarse continent outlines (lon, lat). Stylised, drawn from memory, no data files.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 68), (-100, 69),
     (-95, 80), (-85, 70), (-80, 73), (-75, 62), (-65, 60), (-55, 52),
     (-60, 47), (-70, 42), (-76, 35), (-80, 26), (-84, 30), (-90, 21),
     (-87, 15), (-92, 14), (-97, 16), (-105, 20), (-110, 23), (-117, 30),
     (-124, 40), (-124, 48), (-135, 58), (-150, 60), (-165, 60), (-168, 66)],
    # South America
    [(-80, 9), (-77, 4), (-72, 11), (-62, 10), (-52, 5), (-50, 0),
     (-44, -3), (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-54, -34),
     (-58, -38), (-65, -41), (-66, -47), (-69, -52), (-71, -54), (-73, -44),
     (-73, -33), (-71, -20), (-70, -18), (-77, -12), (-81, -6), (-80, 0),
     (-80, 9)],
    # Africa
    [(-17, 15), (-16, 21), (-10, 31), (-6, 35), (0, 36), (10, 37),
     (11, 34), (20, 32), (30, 31), (32, 31), (34, 28), (37, 22),
     (39, 18), (43, 12), (48, 11), (51, 12), (48, 5), (41, -2),
     (40, -10), (36, -18), (33, -26), (28, -33), (20, -35), (17, -32),
     (15, -27), (12, -18), (13, -10), (9, 4), (0, 6), (-8, 5),
     (-13, 8), (-17, 15)],
    # Eurasia
    [(-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 48), (-1, 50),
     (2, 51), (5, 53), (7, 55), (8, 57), (10, 59), (13, 56),
     (18, 56), (21, 55), (24, 58), (26, 59), (28, 61), (30, 62),
     (30, 70), (33, 68), (40, 68), (50, 69), (60, 69), (68, 73),
     (75, 72), (85, 75), (95, 76), (105, 77), (115, 73), (125, 73),
     (135, 72), (145, 72), (155, 70), (162, 66), (170, 66), (178, 65),
     (178, 62), (170, 60), (162, 58), (158, 53), (150, 59), (142, 54),
     (141, 45), (140, 40), (135, 35), (130, 33), (127, 35), (122, 31),
     (121, 28), (118, 25), (110, 21), (108, 18), (106, 10), (104, 9),
     (100, 7), (98, 10), (97, 16), (94, 17), (92, 21), (89, 22),
     (86, 20), (83, 18), (80, 13), (77, 8), (75, 11), (73, 16),
     (72, 20), (68, 23), (66, 25), (62, 25), (58, 26), (56, 27),
     (52, 28), (50, 29), (48, 30), (47, 29), (44, 29), (42, 33),
     (40, 36), (36, 36), (33, 36), (30, 36), (27, 37), (26, 38),
     (23, 36), (22, 37), (19, 40), (18, 40), (16, 41), (12, 44),
     (10, 44), (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36),
     (-9, 37), (-10, 36)],
    # Australia
    [(113, -22), (114, -28), (115, -32), (117, -35), (124, -33), (129, -32),
     (132, -32), (137, -35), (140, -38), (144, -38), (147, -39), (150, -37),
     (153, -27), (153, -24), (150, -22), (146, -19), (142, -11), (142, -15),
     (137, -12), (135, -12), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (114, -22), (113, -22)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
     (1, 51), (-2, 50), (-5, 50)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (137, 35), (139, 36), (140, 38),
     (141, 40), (141, 43), (143, 42), (145, 44), (142, 44), (140, 40),
     (137, 37), (133, 35), (131, 33), (130, 31)],
    # New Zealand
    [(167, -45), (169, -43), (172, -41), (175, -38), (177, -38), (178, -38),
     (175, -40), (173, -42), (170, -44), (167, -46), (167, -45)],
]

# (lon, lat, label, dx, dy) — label offset in px from the marker dot.
MARKERS = [
    (37.4, 45.3, "KERCH BRIDGE", 6, -14),
    (30.5, 50.4, "KYIV", -40, -14),
    (50.6, 26.2, "BAHRAIN", 6, -14),
    (56.5, 26.6, "HORMUZ", 6, 8),
    (-77.0, 38.9, "WASHINGTON", 6, -6),
    (114.1, 22.5, "SHENZHEN", 6, -14),
    (121.0, 14.6, "MANILA", 6, 2),
    (139.7, 35.7, "TOKYO", 8, -14),
    (45.0, 12.8, "ADEN", 6, 2),
    (34.5, 31.4, "GAZA", -46, 4),
]


def project(lon, lat, mx, my, mw, mh):
    """Equirectangular projection, lat cropped to -58..84."""
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (84.0 - lat) / 142.0 * mh
    return x, y


def draw_map(d, mx, my, mw, mh):
    d.rectangle([mx, my, mx + mw, my + mh], fill=MAP_BG, outline=INK, width=2)
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    f_tag = font(SANS_B, 11)
    for lon, lat, label, dx, dy in MARKERS:
        x, y = project(lon, lat, mx, my, mw, mh)
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=RED, outline=(255, 255, 255))
        lx, ly = x + dx, y + dy
        for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            d.text((lx + ox, ly + oy), label, font=f_tag, fill=MAP_BG)
        d.text((lx, ly), label, font=f_tag, fill=INK)
    d.text((mx + 8, my + 6), "WHERE THE NEWS HAPPENED", font=font(SANS_B, 11), fill=BLUE)


def draw():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # outer border
    d.rectangle([6, 6, W - 7, H - 7], outline=INK, width=2)

    # ---- masthead ----
    f_title = font(SERIF_B, 46)
    title = "THE WORLD IN ONE PAGE"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 16), title, font=f_title, fill=INK)
    f_sub = font(SANS, 15)
    sub = "TUESDAY  •  17 NOVEMBER 2026  •  34 STORIES FROM AROUND THE WORLD"
    sw = d.textlength(sub, font=f_sub)
    d.text(((W - sw) / 2, 66), sub, font=f_sub, fill=GREY)
    d.line([24, 90, W - 24, 90], fill=RED, width=3)

    # ---- hero ----
    hx, hy, hw = 24, 100, W - 48
    f_kick = font(SANS_B, 14)
    d.text((hx, hy), HERO["tag"], font=f_kick, fill=RED)
    f_head = font(SERIF_B, 29)
    lines = fit_lines(d, HERO["headline"], f_head, hw, 2)
    y = hy + 22
    for ln in lines:
        d.text((hx, y), ln, font=f_head, fill=INK)
        y += 34
    f_sum = font(SANS, 14)
    slines = fit_lines(d, HERO["summary"], f_sum, hw, 2)
    for ln in slines:
        d.text((hx, y), ln, font=f_sum, fill=(40, 40, 40))
        y += 18
    d.line([24, 258, W - 24, 258], fill=INK, width=1)

    # ---- map ----
    draw_map(d, 24, 266, W - 48, 154)

    # ---- story grid ----
    gy = 428
    f_sec = font(SANS_B, 13)
    d.text((24, gy), "THE REST OF THE DAY — 33 MORE STORIES", font=f_sec, fill=BLUE)
    d.line([24, gy + 20, W - 24, gy + 20], fill=LIGHT_LINE, width=1)
    grid_top = gy + 28
    cols, rows = 3, 11
    cw = (W - 48 - 2 * 16) / cols
    ch = (996 - grid_top) / rows
    f_tag = font(SANS_B, 9)
    f_hl = font(SANS_B, 11)
    f_sm = font(SANS, 10)
    for i, (tag, headline, summary) in enumerate(STORIES):
        r, c = divmod(i, cols)
        x0 = 24 + c * (cw + 16)
        y0 = grid_top + r * ch
        d.text((x0, y0), tag, font=f_tag, fill=RED)
        hlines = fit_lines(d, headline, f_hl, cw, 2)
        yy = y0 + 11
        for ln in hlines:
            d.text((x0, yy), ln, font=f_hl, fill=INK)
            yy += 13
        slines = fit_lines(d, summary, f_sm, cw, 1)
        for ln in slines:
            d.text((x0, yy), ln, font=f_sm, fill=(60, 58, 50))
            yy += 12
        if c < cols - 1:
            d.line([x0 + cw + 8, y0 + 2, x0 + cw + 8, y0 + ch - 6],
                   fill=LIGHT_LINE, width=1)

    # ---- footer ----
    d.line([24, 1002, W - 24, 1002], fill=INK, width=1)
    f_foot = font(SANS, 9)
    foot = ("Sources: Reuters, AP, Al Jazeera, NPR, The Guardian, Just Security, Zark News, "
            "Open Chronicle — all stories reported on 17 November 2026.")
    d.text((24, 1006), foot, font=f_foot, fill=GREY)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    img = draw()
    img.save(out_path, format="PNG", optimize=True)
    print(out_path)


if __name__ == "__main__":
    main()
