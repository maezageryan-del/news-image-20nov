# The World in One Day — Friday 20 November 2026: 52 stories, one front page — Akvan landfall, Trump defers Iran, missile over Riyadh, The Hague rules on Myanmar

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/maezageryan-del/news-image-20nov/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/maezageryan-del/news-image-20nov/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A 1024×1024 broadsheet front page summing up Friday 20 November 2026 in a
single image — 52 verified stories, drawn entirely in code.

## What is on the page

- **Masthead** — "THE WORLD IN ONE DAY", Friday 20 November 2026, 52 stories
  on one page.
- **Lead** — Cyclone Akvan makes landfall on the Odisha coast: 300,000 people
  evacuated, winds 90–100 km/h gusting 110, heavy-rain alerts in 19
  districts. Drawn with a spiral storm over a coastline.
- **Lead panels** — Trump defers the Iran decision to 2027 ("No rush… see
  what happens after Jan 1"); a missile over Riyadh damages the Saudi
  sovereign wealth fund tower; The Hague rules Myanmar committed genocide
  against the Rohingya; a day after the first Trump–Xi–Putin table in
  Shenzhen, Europe says it is ready for talks with Russia.
- **World map strip** — simplified continents with ten numbered pins tying
  the big stories to their places: Odisha, Riyadh, The Hague, Shenzhen,
  Wellington, Seoul, Suva, Caracas, Pyongyang, Washington.
- **Three columns** — 21 headline-and-deck stories: Kyiv embassies hit, the
  Crimean Bridge struck, Iran's 2,500+ missiles, Seoul's court reversal,
  Fiji's disaster declaration, Venezuela, Yongbyon, markets, tech, and
  cricket.
- **Illustrated panels** — Voyager 1 crosses a light-day, Hayabusa2 loses
  its landing, GTA 6 passes $1.8bn, Anthropic's $81bn debut, and Phillips
  118 with Nicholls 146 not out in Wellington.
- **The day in numbers** — 300,000 evacuated · 2,500+ missiles · $81.34bn
  raised · 118 Phillips · 146* Nicholls · 90–100 km/h winds · $1.5tn
  valuation · 19 districts on alert.
- **Also today** — 20 one-line briefs, from RCB's win to New START lapsing.
- **Footer** — sources: BBC · Reuters · AP · NDTV · IMD · NASA · NYT · WSJ
  · FT.

## How it was made

`render.py` (Python, stdlib + Pillow) reads `stories.json` and draws the whole
front page — masthead, panels, map, columns, numbers, briefs — with
code-drawn, engraving-style illustrations. No photographs, no network, no
randomness: running it twice produces a byte-identical `entry.png`.

`main.ts` (Node 22 standard library only) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` and verifies the byte count matches.

```sh
python3 render.py          # writes entry.png (1024x1024, <= 1 MiB)
npx tsc --noEmit main.ts   # type-check the runner (erasable TS)
```

## Bounty

- Bounty: https://make.fun/bounty/news-image-20261120
- Leaderboard: https://make.fun/bounty/news-image-20261120/leaderboard
