# Avian Influenza Outbreak Explorer

A local Python / Streamlit / Pandas / Plotly dashboard for exploring the geography and timing of US HPAI flock detection records from 2022 onward.

## Start the demo

From the repository root:

```bash
./demo2.sh
```

Open **http://localhost:8501**. Stop the server with Ctrl+C. The launcher installs the pinned dependencies in `outbreak-explorer/.venv`, then starts Streamlit. With [uv](https://docs.astral.sh/uv/), it selects Python 3.12; without uv, install Python 3.10+ first and the launcher uses `python3`. Initial installation requires internet access. Subsequent use can use the existing environment directly:

```bash
cd outbreak-explorer
.venv/bin/python -m streamlit run app.py
```

An alternative manual setup is `python3 -m venv .venv`, `.venv/bin/python -m pip install -r requirements.txt`, then the Streamlit command above. Run from this directory so Streamlit reads `.streamlit/config.toml` and serves the local map geometry.

## Demonstration workflow

1. Switch the map to **Cumulative** to see the full historical distribution. Hover over a state for flock records, known affected-bird totals, and missing bird counts.
2. Switch to **Monthly**, move the month slider, or press **Play**. Pause to inspect a month. Playback stops at the end; playing from the last month restarts at the first. Each mode uses a fixed color scale across months for the current filters and measure.
3. Select a bar in the timeline to change the map month. Box selection uses the first selected bar. Drag the lower range handles, use the 6-month / 1-year buttons, or use Plotly's zoom tool to inspect periods. Zoom changes the chart viewport; use the sidebar date range to change the analytical subset shared by all views.
4. Filter states, dates, source categories, or exact operation types. Empty multiselects mean all values. Toggle affected-bird counts to see how flock counts and flock sizes tell different descriptive stories.
5. Read the computed observations and expand the verification tables. Download the filtered underlying records for independent analysis.

Top summary cards, timeline, observations, tables, and CSV describe the full filtered date range. Only the map and adjacent ranking use the selected month and monthly/cumulative mode. Cumulative counts start at the selected date-range boundary. The first and last months can be partial. Puerto Rico is included in totals and tables but outside the US Albers map projection.

## Real data and provenance

- Official context: [USDA APHIS confirmed HPAI commercial and backyard flock detections](https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/commercial-backyard-flocks).
- Download used: [third-party APHIS-derived CSV](https://casey891.github.io/hpai-dashboard/data/poultry_detections.csv). This app does not claim the mirror is an official live APHIS feed.
- Bundled snapshot retrieved **2026-11-06 UTC**; **2,300 records**, **2022-02-08 through 2026-11-04**, **211,675,446 birds in affected flocks**, 51 state/territory labels.
- Source columns: `Date`, `State`, `County`, `Operation Type`, `Birds Impacted`. The bundled snapshot has no missing values in these columns. A SHA-256 hash and exact retrieval timestamp are saved in `data/poultry_detections.metadata.json` and displayed in the app.

The app attempts a download with timeouts and caches it for 24 hours in memory and in ignored `data/latest*` files. Downloaded data is validated before caching. If a download fails, the app uses a hash-verified last download or bundled snapshot and displays a warning. **Refresh source data** forces another download. Local Plotly USA geometry (`static/usa_110m.json`) is bundled from [plotly.js](https://github.com/plotly/plotly.js/blob/master/dist/topojson/usa_110m.json), so map rendering needs no external map service.

## Interpretation and limitations

- Each row counts as a flock detection record, not a unique farm. The source has no unique detection identifier. The 10 exactly repeated rows beyond their first occurrence are deliberately retained and disclosed because they cannot be distinguished from separate matching detections.
- Birds in affected flocks are **not confirmed infected birds or dead birds**. Totals are descriptive burden counts, not incidence rates or risk estimates.
- Commercial filtering only selects operation labels beginning with `Commercial `. Other labels (including `WOAH Poultry`, `WOAH Non-Poultry`, live bird markets, and primary breeders) remain available by their original names. The source does not explicitly identify backyard flocks, so the app does not invent that classification.
- Missing bird counts, if present in future downloads, remain missing. Aggregations show known sums and missing-count tallies; a group with only missing bird counts remains unknown. Months/states without matching detection records show zero matching records, not proof of absence of infection.
- No deduplication, population denominators, interpolation, inferred locations, or fabricated outbreaks. Wild-bird and mammal surveillance are outside this dataset. Reporting delays, revisions, uneven surveillance, and partial months limit comparisons.
- Observations use direct monthly/state sums and the commercial share of the selected measure; ties are reported. No LLM, causal inference, or statistical significance claims.

## Verification

```bash
cd outbreak-explorer
.venv/bin/python -m unittest -v
```

Checks reconcile snapshot totals, date coverage, preserved duplicate rows, state/month sums, partial date boundaries, monthly/cumulative windows, missing-count semantics, offline fallback, and Streamlit interactions including empty and single-month filters. The running server and local map endpoint were checked over HTTP; Safari rendered the map and playback was checked visually.
