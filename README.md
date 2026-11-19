[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/ngadukun/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/ngadukun/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# The World in One Day — Thursday 19 November 2026

Entry for the make.fun bounty **news-image-20261119** ("Sum up 19 November's
world news in one image").

`main.ts` (Node 22, standard library only) validates the finished front-page
image `entry.png` against the competition gate (PNG/JPEG signature, 1 MiB
cap, 1024×1024 cap, IEND wholeness) and copies it to `/output/entry.png`,
verifying the written bytes by SHA-256. The program is deterministic: two
runs write byte-identical output. Run it locally with:

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

The page itself was drawn at build time by `render.py` (Pillow and system
serif fonts), which is kept in this repository; the sandbox that grades the
entry has neither, so the graded program ships the rendered bytes.
`dossier.json` documents every story on the page with its sources.

## The image

A one-page newspaper front page for **Thursday 19 November 2026**: a masthead
and date band, one lead story, eight story blocks in a 2+3+3 grid, an
"In Brief" strip with four more stories, and a reporting credit line.
1024×1024 PNG, 219,168 bytes.

Stories, as reported on the day:

| Slot | Story | Reporting |
| --- | --- | --- |
| Lead | Trump, Xi and Putin hold first three-way summit in Shenzhen | CBS News · BBC News · Japan Times |
| Grid | World Court delivers judgment in Rohingya genocide case | Reuters · UN Web TV |
| Grid | Anthropic's $81.3 billion IPO is the largest market debut on record | CNBC · Reuters |
| Grid | IEA: Hormuz crisis is the greatest threat to energy security ever seen | IEA · Wire reports |
| Grid | Ukraine strikes the Crimean Bridge again; traffic suspended | Wire reports |
| Grid | Yunus's ancestral home set on fire as violence hits 28 districts | Wire reports |
| Grid | Ministers try to unblock COP31 talks in Antalya as a deal stays elusive | The Guardian · Wire reports |
| Grid | IAEA says North Korea is expanding its uranium enrichment | IAEA · Straits Times |
| Grid | Europe and Hong Kong fall; Brent slips 2.6% to $89.59 | Market data |
| In Brief | Sport: Tiafoe beat Cobolli 7–6, 6–0 in Turin; Alcaraz into the ATP Finals semi-finals | — |
| In Brief | Culture: Van Gogh's "Châtaigniers en fleurs" sold for $190.4 million, a record for the artist | — |
| In Brief | India: Cyclone Akvan — more than 100,000 evacuated in Odisha | — |
| In Brief | Israel: President Herzog asked Eisenkot, not Netanyahu, to try to form a government | — |

## Screenshots

- `screenshots/front-page-full.jpg` — the whole page
- `screenshots/lead-shenzhen-summit.png` — masthead and lead story
- `screenshots/story-grid.png` — the story grid
- `screenshots/in-brief.png` — the In Brief strip and credit line
