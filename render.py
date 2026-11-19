#!/usr/bin/env python3
"""Render the news-image-20261119 entry: one front page that sums up the
world news of Thursday 19 November 2026.

The page is drawn with PIL on a 2048x2048 canvas (twice the final size) and
downscaled to 1024x1024, which keeps the type crisp. Everything the entry
ships is produced here:

    entry.png                        the judged image (1024x1024 PNG)
    screenshots/front-page-full.jpg  the same page as a JPEG
    screenshots/lead-shenzhen-summit.png  crop of the lead story
    screenshots/story-grid.png       crop of the three story bands
    screenshots/in-brief.png         crop of the In Brief strip
    dossier.json                     manifest: files, hashes, story list

Usage: python3 render.py [target-dir]   (default: the directory of this file)
Deterministic: no clocks, no randomness, fixed fonts -- two runs write the
same bytes.
"""

import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Page geometry (final-image pixels; the canvas is drawn at SS x this size)
# --------------------------------------------------------------------------
SS = 2                      # supersample factor
PAGE = 1024                 # final width and height
MARGIN = 44                 # side margin
CW = PAGE - 2 * MARGIN      # content width

PAPER = (247, 243, 234)
INK = (18, 20, 26)
SOFT = (84, 88, 98)         # credits, straps
RULE = (18, 20, 26)
HAIR = (196, 190, 174)      # light hairlines between columns
RED = (163, 32, 40)
BLUE = (30, 58, 122)
GREEN = (16, 96, 62)
WHITE = (250, 248, 243)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BODY = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
BODY_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

_font_cache = {}


def F(path, size):
    """Font at a final-image size (scaled up for the supersampled canvas)."""
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, int(size * SS))
    return _font_cache[key]


# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------
def wrap(draw, text, font, width):
    """Greedy word wrap; width in final-image pixels."""
    limit = width * SS
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= limit or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def tracked(draw, xy, text, font, tracking, fill, anchor_left=True):
    """Draw letter-spaced text (for kickers and straps). Returns its width."""
    x, y = xy[0] * SS, xy[1] * SS
    step = tracking * SS
    total = sum(draw.textlength(ch, font=font) for ch in text) + step * (len(text) - 1)
    if not anchor_left:
        x -= total
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + step
    return total / SS


def centered(draw, y, text, font, fill, tracking=0):
    if tracking:
        w = sum(draw.textlength(c, font=font) for c in text) + tracking * SS * (len(text) - 1)
        x = (PAGE * SS - w) / 2
        for ch in text:
            draw.text((x, y * SS), ch, font=font, fill=fill)
            x += draw.textlength(ch, font=font) + tracking * SS
    else:
        w = draw.textlength(text, font=font)
        draw.text(((PAGE * SS - w) / 2, y * SS), text, font=font, fill=fill)


# --------------------------------------------------------------------------
# The stories of Thursday 19 November 2026 (kicker, headline, body, credit)
# --------------------------------------------------------------------------
LEAD = {
    "kicker": "SHENZHEN SUMMIT · APEC",
    "color": RED,
    "headline": "Trump, Xi and Putin hold first three-way summit in Shenzhen",
    "body": ("The presidents of the United States, China and Russia sat down "
             "together for the first time, meeting on the sidelines of the "
             "APEC summit. Trump also held a one-to-one with Putin lasting "
             "some 40 minutes and dominated by Ukraine, and saw Xi, who "
             "called U.S.–China relations stable and improving."),
    "credit": "CBS News · BBC News · Japan Times",
}

BAND_A = [
    {
        "kicker": "THE HAGUE · WORLD COURT",
        "color": BLUE,
        "headline": "World Court delivers judgment in Rohingya genocide case",
        "body": ("The International Court of Justice gave its final judgment "
                 "in The Gambia’s case over Myanmar’s 2017 crackdown, which "
                 "drove 730,000 Rohingya into Bangladesh. No state had ever "
                 "been found responsible for genocide by the court, and the "
                 "ruling cannot be appealed."),
        "credit": "Reuters · UN Web TV",
    },
    {
        "kicker": "BUSINESS · ARTIFICIAL INTELLIGENCE",
        "color": RED,
        "headline": "Anthropic’s $81.3 billion IPO is the largest market debut on record",
        "body": ("The maker of the Claude chatbot priced its shares at $83, "
                 "above its range, raising $81.3 billion for a valuation "
                 "near $1.5 trillion. Trading starts Thursday on the Nasdaq "
                 "under the ticker ANT."),
        "credit": "CNBC · Reuters",
    },
]

BAND_B = [
    {
        "kicker": "ENERGY · HORMUZ",
        "color": RED,
        "headline": "IEA: Hormuz crisis is the greatest threat to energy security ever seen",
        "body": ("The agency’s annual report said consumers now absorb the "
                 "shock as other buffers run down. An ADNOC tanker crew "
                 "member is missing and 11 were hurt after a strike in the "
                 "strait."),
        "credit": "IEA · Wire reports",
    },
    {
        "kicker": "UKRAINE WAR",
        "color": BLUE,
        "headline": "Ukraine strikes the Crimean Bridge again; traffic suspended",
        "body": ("Crimean authorities halted traffic after the latest attack "
                 "on the bridge linking Russia to the annexed peninsula — "
                 "Ukraine’s third strike on it in a week."),
        "credit": "Wire reports",
    },
    {
        "kicker": "BANGLADESH",
        "color": GREEN,
        "headline": "Yunus’s ancestral home set on fire as violence hits 28 districts",
        "body": ("Protests by supporters of Sheikh Hasina, sentenced to "
                 "death, spread across Bangladesh; police recorded bomb "
                 "blasts and burned vehicles in 28 districts in ten days."),
        "credit": "Wire reports",
    },
]

BAND_C = [
    {
        "kicker": "CLIMATE · COP31",
        "color": GREEN,
        "headline": "Ministers try to unblock COP31 talks in Antalya as a deal stays elusive",
        "body": ("Ministers met in informal session to break the deadlock "
                 "over the climate summit’s final text, with a new draft "
                 "under discussion."),
        "credit": "The Guardian · Wire reports",
    },
    {
        "kicker": "NORTH KOREA",
        "color": RED,
        "headline": "IAEA says North Korea is expanding its uranium enrichment",
        "body": ("The UN nuclear agency reported further expansion at the "
                 "North’s enrichment facilities. In Seoul, President Lee "
                 "renewed his call for dialogue with Pyongyang."),
        "credit": "IAEA · Straits Times",
    },
    {
        "kicker": "MARKETS",
        "color": BLUE,
        "headline": "Europe and Hong Kong fall; Brent slips 2.6% to $89.59",
        "body": ("The FTSE 100 lost 1.30% and the Hang Seng 1.90%; the "
                 "S&P 500 eased 0.23% while the Nasdaq rose 0.42%; the VIX "
                 "stood at 24.56."),
        "credit": "Market data",
    },
]

BRIEFS = [
    ("Sport", "Tiafoe beat Cobolli 7–6, 6–0 at the ATP Finals in Turin, "
              "sending Alcaraz into the semi-finals."),
    ("Culture", "Van Gogh’s “Châtaigniers en fleurs” sold at Sotheby’s New "
                "York for $190.4 million, a record for the artist."),
    ("India", "Cyclone Akvan — more than 100,000 people evacuated in Odisha "
              "as landfall nears Gopalpur."),
    ("Israel", "President Herzog asked former army chief Gadi Eisenkot, not "
               "Netanyahu, to try to form a government."),
]

FOOTER = ("Reporting: Reuters · AFP · Associated Press · Al Jazeera · "
          "CBS News · BBC News — the news of Thursday 19 November 2026, "
          "as reported that day")


# --------------------------------------------------------------------------
# Drawing blocks
# --------------------------------------------------------------------------
def story(draw, x, y, w, item, headline_size, body_size, headline_font=SERIF_B):
    """One story: kicker, headline, body, credit. Returns the y below it."""
    # kicker with a small colour block
    draw.rectangle([x * SS, (y + 2) * SS, (x + 22) * SS, (y + 9) * SS],
                   fill=item["color"])
    tracked(draw, (x + 30, y - 3), item["kicker"], F(SANS_B, 12.5), 0.6,
            item["color"])
    y += 17
    hf = F(headline_font, headline_size)
    for line in wrap(draw, item["headline"], hf, w):
        draw.text((x * SS, y * SS), line, font=hf, fill=INK)
        y += headline_size * 1.14
    y += 3
    bf = F(BODY, body_size)
    for line in wrap(draw, item["body"], bf, w):
        draw.text((x * SS, y * SS), line, font=bf, fill=INK)
        y += body_size * 1.32
    y += 2
    draw.text((x * SS, y * SS), item["credit"], font=F(BODY_I, 10.5), fill=SOFT)
    return y + 15


def band(draw, y, items, cols, headline_size, body_size):
    """A row of stories in `cols` columns with hairlines between them."""
    gutter = 28 if cols == 2 else 24
    colw = (CW - gutter * (cols - 1)) / cols
    bottom = y
    for i, item in enumerate(items):
        x = MARGIN + i * (colw + gutter)
        end = story(draw, x, y, colw, item, headline_size, body_size)
        bottom = max(bottom, end)
        if i:
            lx = x - gutter / 2
            draw.line([lx * SS, y * SS, lx * SS, (bottom - 8) * SS],
                      fill=HAIR, width=SS)
    return bottom


def header(draw):
    """Masthead, date band. Returns the y below the date band."""
    y = 24
    f = F(SANS_B, 12)
    tracked(draw, (MARGIN, y), "THE WORLD’S NEWS, ON ONE PAGE", f, 1.6, SOFT)
    tracked(draw, (PAGE - MARGIN, y), "WORLD EDITION", f, 1.6, SOFT,
            anchor_left=False)
    y += 22
    draw.rectangle([MARGIN * SS, y * SS, (PAGE - MARGIN) * SS, (y + 3) * SS],
                   fill=RULE)
    y += 10
    centered(draw, y, "THE WORLD ON ONE PAGE", F(SERIF_B, 52), INK, tracking=0.4)
    y += 62
    draw.rectangle([MARGIN * SS, y * SS, (PAGE - MARGIN) * SS, (y + 3) * SS],
                   fill=RULE)
    draw.rectangle([MARGIN * SS, (y + 5) * SS, (PAGE - MARGIN) * SS,
                    (y + 6) * SS], fill=RULE)
    y += 14
    draw.rectangle([MARGIN * SS, y * SS, (PAGE - MARGIN) * SS, (y + 34) * SS],
                   fill=INK)
    centered(draw, y + 6, "THURSDAY · 19 NOVEMBER 2026", F(SANS_B, 19),
             WHITE, tracking=2.2)
    return y + 34


def briefs(draw, y):
    """The In Brief strip: a dark band, a label row, then the four short
    items in a 2x2 grid, each led by a gold section name."""
    height = 106
    draw.rectangle([MARGIN * SS, y * SS, (PAGE - MARGIN) * SS,
                    (y + height) * SS], fill=INK)
    pad = 16
    tracked(draw, (MARGIN + pad, y + 9), "IN BRIEF", F(SANS_B, 13), 1.8, WHITE)
    draw.line([(MARGIN + pad) * SS, (y + 32) * SS, (PAGE - MARGIN - pad) * SS,
               (y + 32) * SS], fill=(90, 94, 104), width=SS)
    colw = (CW - 2 * pad - 24) / 2
    positions = [(0, 0), (1, 0), (0, 1), (1, 1)]
    for (label, text), (cx, cy) in zip(BRIEFS, positions):
        x = MARGIN + pad + cx * (colw + 24)
        ty = y + 40 + cy * 33
        lab = F(SANS_B, 11.5)
        draw.text((x * SS, ty * SS), label, font=lab, fill=(240, 200, 120))
        lw = draw.textlength(label, font=lab) / SS + 7
        bf = F(SANS, 11)
        lines = wrap(draw, text, bf, colw - lw)
        for i, line in enumerate(lines[:2]):
            draw.text(((x + lw) * SS, (ty + i * 15) * SS), line, font=bf,
                      fill=WHITE)
    return y + height


def build_page():
    img = Image.new("RGB", (PAGE * SS, PAGE * SS), PAPER)
    draw = ImageDraw.Draw(img)
    marks = {}

    y = header(draw)

    # Lead story, full width; the red accent bar is drawn after the text so
    # it spans the block's true height (the text starts 18px to its right).
    y += 14
    marks["lead_top"] = y
    lead_end = story(draw, MARGIN + 18, y, CW - 18, LEAD, 37, 15)
    draw.rectangle([MARGIN * SS, y * SS, (MARGIN + 5) * SS,
                    (lead_end - 12) * SS], fill=RED)
    y = lead_end + 2
    marks["lead_bottom"] = y
    draw.line([MARGIN * SS, y * SS, (PAGE - MARGIN) * SS, y * SS],
              fill=RULE, width=2 * SS)

    y += 12
    marks["grid_top"] = y
    y = band(draw, y, BAND_A, 2, 20, 13)
    draw.line([MARGIN * SS, y * SS, (PAGE - MARGIN) * SS, y * SS],
              fill=HAIR, width=SS)
    y += 10
    y = band(draw, y, BAND_B, 3, 18.5, 12.5)
    draw.line([MARGIN * SS, y * SS, (PAGE - MARGIN) * SS, y * SS],
              fill=HAIR, width=SS)
    y += 10
    y = band(draw, y, BAND_C, 3, 18.5, 12.5)
    marks["grid_bottom"] = y

    y += 4
    marks["brief_top"] = y
    y = briefs(draw, y)
    marks["brief_bottom"] = y

    y += 8
    centered(draw, y, FOOTER, F(BODY_I, 11), SOFT)
    marks["end"] = y + 16

    page = img.resize((PAGE, PAGE), Image.LANCZOS)
    return page, marks


# --------------------------------------------------------------------------
# Outputs
# --------------------------------------------------------------------------
def sha256(data):
    return hashlib.sha256(data).hexdigest()


def save_all(target):
    os.makedirs(os.path.join(target, "screenshots"), exist_ok=True)
    page, marks = build_page()

    files = {}

    def record(relpath, data):
        path = os.path.join(target, relpath)
        with open(path, "wb") as fh:
            fh.write(data)
        files[relpath] = {"sha256": sha256(data), "bytes": len(data)}

    import io
    buf = io.BytesIO()
    page.save(buf, "PNG")
    record("entry.png", buf.getvalue())

    buf = io.BytesIO()
    page.save(buf, "JPEG", quality=88)
    record("screenshots/front-page-full.jpg", buf.getvalue())

    crops = {
        "screenshots/lead-shenzhen-summit.png":
            (0, int(marks["lead_top"]) - 8, PAGE, int(marks["lead_bottom"]) + 6),
        "screenshots/story-grid.png":
            (0, int(marks["grid_top"]) - 8, PAGE, int(marks["grid_bottom"]) + 4),
        "screenshots/in-brief.png":
            (0, int(marks["brief_top"]) - 6, PAGE, int(marks["brief_bottom"]) + 6),
    }
    for relpath, box in crops.items():
        buf = io.BytesIO()
        page.crop(box).save(buf, "PNG")
        record(relpath, buf.getvalue())

    stories = ([{"section": "Lead", "headline": LEAD["headline"]}] +
               [{"section": s["kicker"], "headline": s["headline"]}
                for s in BAND_A + BAND_B + BAND_C] +
               [{"section": "In Brief · " + label, "headline": text}
                for label, text in BRIEFS])
    dossier = {
        "competition": "news-image-20261119",
        "date": "2026-11-19",
        "day": "Thursday",
        "title": "The World on One Page — Thursday 19 November 2026",
        "renderer": "render.py (PIL, supersampled x2)",
        "image": "entry.png",
        "limits": {"max_bytes": 1048576, "max_width": 1024, "max_height": 1024},
        "stories": stories,
        "files": files,
    }
    data = (json.dumps(dossier, indent=2, ensure_ascii=False) + "\n").encode()
    record("dossier.json", data)
    return marks, files


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
        os.path.abspath(__file__))
    marks, files = save_all(target)
    print("render.py: wrote", ", ".join(sorted(files)))
    print("render.py: page content ends at y=%d of %d" % (marks["end"], PAGE))
    entry = files["entry.png"]
    print("render.py: entry.png %d bytes sha256 %s"
          % (entry["bytes"], entry["sha256"]))


if __name__ == "__main__":
    main()
