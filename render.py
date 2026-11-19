#!/usr/bin/env python3
"""Build-time renderer for the news-image-20261119 entry.

Draws the one-page newspaper front page for Thursday 19 November 2026 and
writes entry.png (1024x1024). This script is a build tool only: it runs on
the author's machine with Pillow and system serif fonts. The graded program
is main.ts (Node 22, standard library only), which copies entry.png to
/output/entry.png in the sandbox, where no fonts or Pillow exist.

Every headline and fact below is the news of Thursday 19 November 2026 as
reported that day; see dossier.json for story-by-story sources.
"""

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 40
CW = W - 2 * MARGIN  # content width

PAPER = (248, 244, 235)
INK = (20, 19, 16)
GRAY = (96, 92, 84)
RED = (142, 31, 31)
NAVY = (31, 58, 110)
GREEN = (30, 91, 58)

F = "/usr/share/fonts/truetype"
SERIF_BLACK = f"{F}/noto/NotoSerifDisplay-Black.ttf"
SERIF_BOLD = f"{F}/noto/NotoSerif-Bold.ttf"
SANS = f"{F}/noto/NotoSans-Regular.ttf"
SANS_BOLD = f"{F}/noto/NotoSans-Bold.ttf"
SANS_OBL = f"{F}/noto/NotoSans-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)


def text_w(s, fnt):
    return d.textlength(s, font=fnt)


def wrap(text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = f"{cur} {w_}".strip()
        if text_w(trial, fnt) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def centered(text, y, fnt, fill=INK, spacing=0):
    if spacing:
        total = sum(text_w(ch, fnt) for ch in text) + spacing * (len(text) - 1)
        x = (W - total) / 2
        for ch in text:
            d.text((x, y), ch, font=fnt, fill=fill)
            x += text_w(ch, fnt) + spacing
    else:
        d.text(((W - text_w(text, fnt)) / 2, y), text, font=fnt, fill=fill)


def rule(y, thickness=2, x0=MARGIN, x1=W - MARGIN):
    d.rectangle([x0, y, x1, y + thickness - 1], fill=INK)


def block(x, y, width, color, kicker, headline, body, credit,
          head_size, body_size=16, head_lh=1.04, body_lh=1.18):
    """Draw one story block; return the y just below its credit line."""
    kf = font(SANS_BOLD, 15)
    d.rectangle([x, y + 3, x + 26, y + 9], fill=color)
    d.text((x + 34, y), kicker, font=kf, fill=color)
    y += 22
    hf = font(SERIF_BOLD, head_size)
    for line in wrap(headline, hf, width):
        d.text((x, y), line, font=hf, fill=INK)
        y += int(head_size * head_lh)
    y += 4
    bf = font(SANS, body_size)
    for line in wrap(body, bf, width):
        d.text((x, y), line, font=bf, fill=INK)
        y += int(body_size * body_lh)
    y += 3
    d.text((x, y), credit, font=font(SANS_OBL, 13), fill=GRAY)
    return y + 12


# ---- masthead -------------------------------------------------------------
centered("ONE DAY · ONE IMAGE · THE WORLD'S NEWS", 28, font(SANS, 15),
         fill=GRAY, spacing=3)
rule(60, 3)

mast = "THE WORLD IN ONE DAY"
size = 66
while text_w(mast, font(SERIF_BLACK, size)) > CW:
    size -= 1
centered(mast, 74, font(SERIF_BLACK, size))

band_y = 150
d.rectangle([MARGIN, band_y, W - MARGIN, band_y + 50], fill=INK)
date = "THURSDAY · 19 NOVEMBER 2026"
df = font(SANS_BOLD, 29)
d.text(((W - text_w(date, df)) / 2, band_y + 10), date, font=df,
       fill=(255, 255, 255))
rule(band_y + 58, 2)

# ---- lead -----------------------------------------------------------------
y = block(
    MARGIN, band_y + 62, CW, RED,
    "SHENZHEN SUMMIT · APEC",
    "Trump, Xi and Putin hold first three-way summit in Shenzhen",
    "The presidents of the United States, China and Russia met together "
    "for the first time, on the sidelines of the APEC summit. Trump also "
    "met Putin alone — some 40 minutes, dominated by Ukraine — and Xi, "
    "who called U.S.–China relations stable and improving.",
    "CBS News · BBC News · Japan Times",
    head_size=33,
)
rule(y + 2, 2)
y += 6

# ---- grid row A: two columns ----------------------------------------------
col2 = (CW - 16) // 2
ya = block(
    MARGIN, y, col2, NAVY,
    "THE HAGUE · WORLD COURT",
    "World Court delivers judgment in Rohingya genocide case",
    "The International Court of Justice gave its final judgment in The "
    "Gambia's case over Myanmar's 2017 crackdown, which drove 730,000 "
    "Rohingya into Bangladesh. No state had ever been found responsible "
    "for genocide by the court; the ruling cannot be appealed.",
    "Reuters · UN Web TV",
    head_size=21,
)
yb = block(
    MARGIN + col2 + 16, y, col2, RED,
    "BUSINESS · ARTIFICIAL INTELLIGENCE",
    "Anthropic's $81.3 billion IPO is the largest market debut on record",
    "The maker of the Claude chatbot priced its shares at $83, above its "
    "range, raising $81.3 billion and a valuation near $1.5 trillion. "
    "Trading starts Thursday on the Nasdaq under the ticker ANT.",
    "CNBC · Reuters",
    head_size=21,
)
y = max(ya, yb)
rule(y + 2, 1)
y += 6

# ---- grid rows B and C: three columns --------------------------------------
col3 = (CW - 32) // 3


def row3(y, stories):
    ends = []
    for i, s in enumerate(stories):
        ends.append(block(MARGIN + i * (col3 + 16), y, col3, *s,
                          head_size=18, body_size=14))
    return max(ends)


y = row3(y, [
    (RED, "ENERGY · HORMUZ",
     "IEA: Hormuz crisis is the greatest threat to energy security ever seen",
     "The agency's annual report said consumers now absorb the shock as "
     "other buffers run down. An ADNOC tanker crew member is missing and "
     "11 were hurt after a strike in the strait.",
     "IEA · Wire reports"),
    (NAVY, "UKRAINE WAR",
     "Ukraine strikes the Crimean Bridge again; traffic suspended",
     "Crimea's authorities halted traffic after the latest attack on the "
     "bridge linking Russia to the annexed peninsula — Ukraine's third "
     "strike on it in a week.",
     "Wire reports"),
    (GREEN, "BANGLADESH",
     "Yunus's ancestral home set on fire as violence hits 28 districts",
     "Protests by supporters of Sheikh Hasina, sentenced to death, "
     "spread across Bangladesh; police recorded bomb blasts and burned "
     "vehicles in 28 districts in ten days.",
     "Wire reports"),
])
rule(y + 2, 1)
y += 6

y = row3(y, [
    (GREEN, "CLIMATE · COP31",
     "Ministers try to unblock COP31 talks in Antalya as a deal stays elusive",
     "Ministers met in informal session to break the deadlock over the "
     "climate summit's final text, with a new draft under discussion.",
     "The Guardian · Wire reports"),
    (RED, "NORTH KOREA",
     "IAEA says North Korea is expanding its uranium enrichment",
     "The UN nuclear agency reported further expansion at the North's "
     "enrichment facilities. In Seoul, President Lee renewed his call "
     "for dialogue with Pyongyang.",
     "IAEA · Straits Times"),
    (NAVY, "MARKETS",
     "Europe and Hong Kong fall; Brent slips 2.6% to $89.59",
     "The FTSE 100 lost 1.30% and the Hang Seng 1.90%; the S&P 500 eased "
     "0.23% while the Nasdaq rose 0.42%; the VIX stood at 24.56.",
     "Market data"),
])
rule(y + 2, 2)
y += 6

# ---- in brief ---------------------------------------------------------------
briefs = [
    ("Sport:", " Tiafoe beat Cobolli 7–6, 6–0 at the ATP Finals in Turin, "
     "sending Alcaraz into the semi-finals."),
    ("Culture:", " Van Gogh's “Châtaigniers en fleurs” sold at Sotheby's "
     "New York for $190.4 million, a record for the artist."),
    ("India:", " Cyclone Akvan — more than 100,000 people evacuated in "
     "Odisha as landfall nears Gopalpur."),
    ("Israel:", " President Herzog asked former army chief Gadi Eisenkot, "
     "not Netanyahu, to try to form a government."),
]
bf, bb = font(SANS, 15), font(SANS_BOLD, 15)
x = MARGIN
d.text((x, y), "IN BRIEF", font=bb, fill=INK)
x += text_w("IN BRIEF ", bb)
for lead, rest in briefs:
    for txt, fnt in ((lead, bb), (rest, bf)):
        for word in txt.split(" "):
            if not word:
                continue
            wpx = text_w(word + " ", fnt)
            if x + wpx > W - MARGIN:
                x = MARGIN
                y += 19
            d.text((x, y), word, font=fnt, fill=INK)
            x += wpx
y += 16
rule(y, 2)

# ---- footer -------------------------------------------------------------------
centered(
    "Reporting: Reuters · AFP · Associated Press · Al Jazeera · CBS News "
    "· BBC News — the news of Thursday 19 November 2026, as reported "
    "that day",
    y + 8, font(SANS_OBL, 13), fill=GRAY)

img.save("entry.png", optimize=True)
print("entry.png written; content bottom at y =", y + 40)
