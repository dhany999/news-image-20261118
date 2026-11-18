#!/usr/bin/env python3
"""news-image-20261118: one newspaper-style front page, 50 verified stories.

Draws a 1024x1024 PNG with Pillow only. Deterministic: no network, no
randomness, no timestamps. Reads MAKEFUN_OUTPUT_DIR (default /output) and
writes exactly one file, entry.png, into it.
"""

import hashlib
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")

NAVY = (13, 27, 62)
NAVY_LIGHT = (24, 48, 96)
GOLD = (212, 175, 55)
GOLD_LIGHT = (232, 201, 96)
WHITE = (255, 255, 255)
PAPER = (250, 248, 243)
INK = (18, 18, 18)
GREY = (92, 92, 92)
ROW_ALT = (240, 236, 228)
LEAD_BG = (255, 255, 255)
FOOTER_BG = (13, 27, 62)

REGION_COLORS = {
    "ME": (178, 34, 34),
    "EUROPE": (31, 78, 160),
    "APAC": (0, 128, 128),
    "AMERICAS": (214, 106, 24),
    "AFRICA": (34, 139, 34),
    "MARKETS": (107, 63, 160),
    "TECH": (96, 96, 96),
    "SPORT": (139, 69, 19),
    "CULTURE": (199, 84, 132),
    "HEALTH": (0, 100, 60),
    "WORLD": (176, 141, 0),
}

LEADS = [
    ("APEC OPENS IN SHENZHEN",
     "21 leaders meet; Trump, Xi, Putin set first trilateral for 19 Nov", "APAC"),
    ("U.S. STRIKES IRAN'S QESHM ISLAND",
     "Iran drones hit U.S. radar base in Bahrain, third strike in days", "ME"),
    ("UKRAINE HITS CRIMEA BRIDGE AGAIN",
     "Road span falls; Russia pounds Kyiv bridges in reply", "EUROPE"),
]

BODY = [
    ("QUAD UNVEILS MARITIME PLAN IN MANILA", "Joint patrols in 2027; $85M AI Accelerator", "APAC"),
    ("TRUMP ARRIVES IN MANILA FOR QUAD", "Meets Modi, Albanese, Takaichi, then flies to Shenzhen", "APAC"),
    ("PUTIN ARRIVES IN SHENZHEN", "Ahead of first trilateral summit with Trump and Xi", "APAC"),
    ("MODI AT EAST ASIA SUMMIT", "Free e-visas for ASEAN tourists; maritime plan", "APAC"),
    ("ASEAN CHAIR PASSES TO SINGAPORE", "Digital economy deal done; sea code 85-90% agreed", "APAC"),
    ("CHINA, SE ASIA EASE SEA TENSIONS", "South China Sea code of conduct nearly settled", "APAC"),
    ("CANADA, CHINA EXTEND TRADE DEALS", "Xi meets Carney ahead of APEC", "APAC"),
    ("JAPAN PROTESTS RUSSIAN JETS", "Two aircraft entered airspace; Tokyo lodges protest", "APAC"),
    ("U.S. PRESSES UN OVER TAIWAN FLIGHTS", "Taiwan seeks $14B in U.S. arms", "APAC"),
    ("TRUMP BACKS HUANG AS NVIDIA CEO", "Chip fight rages before China trip", "TECH"),
    ("U.S. TIGHTENS CHIP ACCESS FOR CHINA", "New export curbs hit AI chip flows", "TECH"),
    ("NVIDIA Q3 REVENUE $115.8 BILLION", "Beats forecasts; guides Q4 near $130B", "MARKETS"),
    ("ANTHROPIC IPO PRICES TODAY", "AI lab set to list on Nasdaq on 19 Nov", "TECH"),
    ("APPLE, ZOOM, BBC, IKEA HIT BY CYBER ATTACK", "200 sites hit in attack on Apple devices", "TECH"),
    ("DEUTSCHE BANK SHARES SLIP AFTER LEAK", "Shares fall after leak reports", "MARKETS"),
    ("GLOBAL STOCKS FALL ON GULF TENSIONS", "Euro Stoxx -2.15%; ASX -2.38%", "MARKETS"),
    ("WALL STREET SLIDES AGAIN", "Dow -1.6%, S&P -1.0%, fourth straight drop", "MARKETS"),
    ("U.S. RETAIL, HOUSING DATA IN FOCUS", "Fed minutes due; December hike odds near 95%", "MARKETS"),
    ("UK INFLATION, JOBS DATA DUE", "Bank of England's next move in balance", "EUROPE"),
    ("BRITAIN SANCTIONS ISRAELI SETTLEMENT FIRMS", "Allies urge Israel to open Gaza aid before winter", "EUROPE"),
    ("UKRAINE PEACE TALKS \"NOT EASY\"", "Zelenskyy after talks with U.S., European envoys", "EUROPE"),
    ("FRANCE DENIES TROOPS IN UKRAINE", "Rejects Russia's claim as false", "EUROPE"),
    ("EU-RWANDA RETURN HUB TALKS GO ON", "Rwanda delegation in Vienna; start eyed 2027", "EUROPE"),
    ("SPAIN TO RAISE MINIMUM WAGE 5.3%", "To 1,286 euros a month; election set 29 Nov", "EUROPE"),
    ("SERBIA MiG-29 CRASH KILLS PILOT", "Jet down near Belgrade; inquiry opens", "EUROPE"),
    ("RUSSIAN AN-12 CRASH KILLS 13", "Military plane down in Siberia", "EUROPE"),
    ("IRAN REFUSES UN NUCLEAR INSPECTION", "Until Middle East war ends, Tehran says", "ME"),
    ("HOUTHIS ADVANCE IN YEMEN", "Seize coast west of Aden; government pulls back", "ME"),
    ("NIGERIA: U.S. INTEL AIDS MILITANT HUNT", "Support targets militants; 2027 vote security", "AFRICA"),
    ("ZAMFARA POLICE FREE 20 ABDUCTED", "Women and children freed in northwest Nigeria", "AFRICA"),
    ("SOUTH AFRICA PROBES 17 SHOT DEAD", "Two weekend shootings under investigation", "AFRICA"),
    ("EGYPT, INDIA PLAN TRADE DEAL", "Working group on pharma, farming, tech", "AFRICA"),
    ("AFRICAN UNION PUSHES SUDAN, CONGO PEACE", "Regional solutions urged", "AFRICA"),
    ("CHINA BUYS MORE WEST AFRICAN CRUDE", "Energy trade shifts east as Gulf simmers", "AFRICA"),
    ("SOUTH SUDAN VOTE DELAY DRAGS ON", "AU, UN press for a clear timeline", "AFRICA"),
    ("FIJI DECLARES DISASTER OVER DROUGHT", "El Nino dries islands; national emergency", "WORLD"),
    ("WHO WARNS ON DRUG-RESISTANT GERMS", "Antimicrobial resistance threat grows", "HEALTH"),
    ("NASA LAUNCHES NUCLEAR-POWER CONTEST", "Students to design space power systems", "WORLD"),
    ("CYCLONE AKVAN BEARS DOWN ON ANDHRA", "Landfall 20 Nov; winds to 145 km/h", "APAC"),
    ("MS DHONI RETIRES FROM IPL", "CSK great, 45, becomes team mentor", "SPORT"),
    ("IPL 2027 RETENTION LIST OUT", "Auction set 16 Dec in Goa", "SPORT"),
    ("INDIA RE-ELECTED TO ITU COUNCIL", "Digital India wins 2027-2030 term", "APAC"),
    ("AMAZON TO INVEST $7B IN INDIA", "Renewable energy push by 2030", "MARKETS"),
    ("INDIA'S FIRST SAF PLANT READY", "Panipat unit turns cooking oil into jet fuel", "WORLD"),
    ("IIT DELHI RANKED 194 IN QS LIST", "India's top green university", "WORLD"),
    ("CRICKET AUSTRALIA OPENS SANDPAPERGATE FORUM", "Players to air views on 2018 scandal", "SPORT"),
    ("ZVEREV REACHES ATP FINALS LAST EIGHT", "German through to knockout stage in Turin", "SPORT"),
]


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_text(draw, text, fnt, max_w):
    """Truncate with an ellipsis so text fits max_w; returns fitted text."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    ell = "..."
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if draw.textlength(text[:mid] + ell, font=fnt) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo].rstrip() + ell


def wrap_text(draw, text, fnt, max_w, max_lines):
    """Greedy word wrap, at most max_lines; last line gets an ellipsis if cut."""
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if len(lines) < max_lines and cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    # If words remain beyond the last line, ellipsize it.
    used = sum(len(l.split()) for l in lines)
    if used < len(words):
        lines[-1] = fit_text(draw, lines[-1], fnt, max_w)
    return lines


def main():
    assert len(LEADS) == 3, f"expected 3 leads, got {len(LEADS)}"
    assert len(BODY) == 47, f"expected 47 body stories, got {len(BODY)}"
    all_heads = [h for h, _, _ in LEADS] + [h for h, _, _ in BODY]
    assert len(all_heads) == 50
    assert len(set(all_heads)) == 50, "headlines must be unique"

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- Masthead ----------
    d.rectangle([0, 0, W, 148], fill=NAVY)
    d.rectangle([0, 148, W, 152], fill=GOLD)
    f_kicker = font(BOLD, 20)
    f_date = font(BOLD, 52)
    f_sub = font(REG, 19)
    kicker = "THE WORLD IN ONE IMAGE"
    d.text(((W - d.textlength(kicker, font=f_kicker)) / 2, 14),
           kicker, font=f_kicker, fill=GOLD_LIGHT)
    date = "18 NOVEMBER 2026"
    d.text(((W - d.textlength(date, font=f_date)) / 2, 40),
           date, font=f_date, fill=WHITE)
    sub = "WEDNESDAY  •  50 STORIES FROM SIX CONTINENTS"
    d.text(((W - d.textlength(sub, font=f_sub)) / 2, 106),
           sub, font=f_sub, fill=GOLD_LIGHT)

    # ---------- Lead cards ----------
    lead_y, lead_h = 160, 158
    margin = 28
    gap = 16
    card_w = (W - 2 * margin - 2 * gap) // 3
    f_lead_head = font(BOLD, 19)
    f_lead_det = font(REG, 12)
    for i, (head, det, tag) in enumerate(LEADS):
        x0 = margin + i * (card_w + gap)
        x1 = x0 + card_w
        color = REGION_COLORS[tag]
        d.rectangle([x0, lead_y, x1, lead_y + lead_h], fill=LEAD_BG,
                    outline=(200, 196, 186), width=1)
        d.rectangle([x0, lead_y, x1, lead_y + 8], fill=color)
        lines = wrap_text(d, head, f_lead_head, card_w - 28, 2)
        y = lead_y + 20
        for ln in lines:
            d.text((x0 + 14, y), ln, font=f_lead_head, fill=INK)
            y += 24
        det_lines = wrap_text(d, det, f_lead_det, card_w - 28, 2)
        dy = lead_y + lead_h - 16 * len(det_lines) - 10
        for ln in det_lines:
            d.text((x0 + 14, dy), ln, font=f_lead_det, fill=GREY)
            dy += 16

    # ---------- Body: 2 columns ----------
    body_y = 332
    body_bottom = 984
    col_gap = 24
    col_w = (W - 2 * margin - col_gap) // 2
    left = BODY[:24]
    right = BODY[24:]
    rows = max(len(left), len(right))
    row_h = (body_bottom - body_y) // rows
    f_head = font(BOLD, 14)
    f_det = font(REG, 11)
    for col_i, stories in enumerate((left, right)):
        x0 = margin + col_i * (col_w + col_gap)
        for r, (head, det, tag) in enumerate(stories):
            y0 = body_y + r * row_h
            if r % 2 == 1:
                d.rectangle([x0 - 6, y0, x0 + col_w + 6, y0 + row_h],
                            fill=ROW_ALT)
            color = REGION_COLORS[tag]
            chip = 9
            d.rectangle([x0, y0 + 4, x0 + chip, y0 + 4 + chip], fill=color)
            tx = x0 + chip + 7
            tw = col_w - chip - 7
            head_fitted = fit_text(d, head, f_head, tw)
            d.text((tx, y0 + 2), head_fitted, font=f_head, fill=INK)
            det_fitted = fit_text(d, det, f_det, tw)
            d.text((tx, y0 + 16), det_fitted, font=f_det, fill=GREY)

    # ---------- Footer ----------
    d.rectangle([0, 986, W, H], fill=FOOTER_BG)
    d.rectangle([0, 986, W, 988], fill=GOLD)
    f_foot = font(REG, 14)
    foot = "Reported 18 November 2026  •  Reuters  •  AP  •  NDTV  •  Al Jazeera  •  Xinhua"
    d.text(((W - d.textlength(foot, font=f_foot)) / 2, 999),
           foot, font=f_foot, fill=WHITE)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "entry.png")
    img.save(out_path, format="PNG")
    data = open(out_path, "rb").read()
    print(f"stories: {len(all_heads)} (3 leads + 47 body)")
    print(f"output: {out_path}")
    print(f"size: {img.size[0]}x{img.size[1]} {len(data)} bytes")
    print(f"sha256: {hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
