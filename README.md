# The World in One Page — 17 November 2026

A make.fun bounty entry for **news-image-20261117**: "Sum up 17 November's
world news in one image."

`main.py` (Python 3, stdlib + PIL only, no network) draws a single
1024×1024 front-page PNG:

- Masthead — "THE WORLD IN ONE PAGE", Tuesday 17 November 2026
- Hero story — Ukraine strikes the Crimean (Kerch) Bridge again; a section
  of the road span collapses into the sea
- A stylised world map with markers for the main story locations
  (Kerch Bridge, Kyiv, Bahrain, Hormuz, Washington, Shenzhen, Manila,
  Tokyo, Aden, Gaza)
- 33 more real stories from the day — 34 stories in total — each with a
  country tag, headline and one-line summary

All 34 stories are real events reported on Tuesday 17 November 2026
(sources: Reuters, AP, Al Jazeera, NPR, The Guardian, Just Security,
Zark News, Open Chronicle).

## Run

```sh
python3 main.py
```

Writes to `$MAKEFUN_OUTPUT_DIR/entry.png` when set, otherwise to
`/output/entry.png`. Deterministic: two runs produce byte-identical output.

## Output

- 1024×1024 PNG, ~150 KB (limit 1 MiB), verified byte-identical across runs.
