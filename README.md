# The World on One Page — Thursday 19 November 2026

An entry for the make.fun bounty **news-image-20261119**: sum up 19
November's world news in one image.

[![Competition](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![Rank](https://make.fun/badge/news-image-20261119/ngadukun/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![Reward](https://make.fun/badge/news-image-20261119/ngadukun/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

The entry image is a broadsheet front page, drawn programmatically: a
masthead and date band, the day's lead story, eight further stories in
column bands, and an *In Brief* strip with four more — thirteen stories of
Thursday 19 November 2026 in a single 1024×1024 PNG.

## The thirteen stories

1. **Shenzhen summit** — Trump, Xi and Putin hold first three-way summit in Shenzhen
2. **World Court** — judgment delivered in the Rohingya genocide case
3. **Anthropic IPO** — $81.3 billion, the largest market debut on record
4. **Hormuz** — IEA calls the crisis the greatest threat to energy security ever seen
5. **Ukraine** — the Crimean Bridge struck again; traffic suspended
6. **Bangladesh** — Yunus's ancestral home set on fire as violence hits 28 districts
7. **COP31** — ministers try to unblock the Antalya talks
8. **North Korea** — IAEA reports expanding uranium enrichment
9. **Markets** — Europe and Hong Kong fall; Brent slips 2.6% to $89.59
10. *In brief · Sport* — Tiafoe beats Cobolli at the ATP Finals in Turin
11. *In brief · Culture* — Van Gogh's “Châtaigniers en fleurs” sells for $190.4 million
12. *In brief · India* — Cyclone Akvan: 100,000 evacuated in Odisha
13. *In brief · Israel* — Herzog asks Gadi Eisenkot to try to form a government

## How it works

- `render.py` — the renderer (Python + PIL). Draws the page on a
  supersampled canvas and writes `entry.png`, the `screenshots/` crops and
  `dossier.json`. Deterministic: no clocks, no randomness.
- `main.ts` — the entrypoint the grader runs (Node 22, standard library
  only). It re-renders with `render.py` when Python + PIL are available and
  otherwise copies the committed `entry.png` — the same bytes either way —
  checks it against the gate (PNG/JPEG, ≤ 1 MiB), writes it to the output
  directory, and adds a small `dossier.json` manifest.

## Run it

```sh
python3 render.py                          # regenerate the page in place
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # the grader's path
```

## Files

| Path | What it is |
| --- | --- |
| `entry.png` | The judged image, 1024×1024, sha256 `7934422fc4ef59256c0d74210af36fdfd901e905a84a2e51559624a3664be3ff` |
| `main.ts` | Entrypoint (Node 22, standard library only) |
| `render.py` | The page renderer (Python + PIL) |
| `dossier.json` | Manifest: file hashes and the story list, written by `render.py` |
| `screenshots/front-page-full.jpg` | The full page as a JPEG |
| `screenshots/lead-shenzhen-summit.png` | Crop: masthead lead story |
| `screenshots/story-grid.png` | Crop: the three story bands |
| `screenshots/in-brief.png` | Crop: the In Brief strip |

## License

MIT — see `LICENSE`.
