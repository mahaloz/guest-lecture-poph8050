# From paper to evidence — local webapp

The complete site source is saved in this directory. Running it needs only Python 3; no npm install, build, account, or hosted service is required.

From the `POPH8050_lecture` repository root:

```bash
python3 research-walkthrough/serve.py
```

Open **http://localhost:8080**. Stop the server with **Ctrl+C**. If that port is in use:

```bash
python3 research-walkthrough/serve.py --port 8081
```

The launcher works from any working directory when given its path. It serves only `dist/` and listens on this computer's loopback interface.

## Source and artifacts

- `dist/index.html`: page structure and research narrative.
- `dist/style.css`: layout, colors, and responsive styles.
- `dist/app.js`: navigation, interactive charts, filters, playback, and notebook views.
- `dist/simulation.js`: scaled and resampled virtual-cohort dot display.
- `dist/data.js`: data-derived curves, included binary records, report, code, and recovery record.
- `dist/assets/`: original/reproduced figures and downloadable research files.
- `prepare_assets.py`: refresh the bundle from the sibling `../reproduction` directory.

Edit HTML, CSS, or JavaScript and refresh the browser; there is no build step. To refresh research artifacts:

```bash
python3 research-walkthrough/prepare_assets.py
```

All charts and research artifacts are bundled locally. The optional Google Fonts stylesheet and external source links require internet; system fonts provide an offline fallback. You can also open `dist/index.html` directly without a server.

## Verification

Optional DOM interaction checks require Node.js and development dependencies:

```bash
cd research-walkthrough
npm ci
npm test
```

Node.js is not needed to run the site. These checks exercise interactions, not rendered-browser layout.

## Scientific scope

The app now uses the actual checksum-verified Dryad archive, recovered through Firefox, and a Python translation of the original R table selections and column means. The default chart shows daily states without display offsets; publication view restores the R line segments and selected ±2-point shifts. Numerators, denominators, source files, and included record summaries are inspectable in the app. It never extrapolates beyond a source block’s horizon.

This reproduces Figure 2 from deposited prepared state tables, not a new animal experiment, a new Kaplan–Meier fit, or all original hypothesis tests. The prior image-only attempt is retained as history and has been superseded. Full methods and remaining discrepancies are in the open notebook.

Recalculate the figure and refresh the bundle from the repository root:

```bash
reproduction/.venv/bin/python reproduction/reproduce.py
python3 research-walkthrough/prepare_assets.py
```

The original archive is at `../reproduction/data/Fig2_and_S2.zip`. Python plotting dependencies are listed in `../reproduction/requirements.txt`; they are not needed just to serve the already bundled app.

## Statistical annotations

The figure explorer shows the vaccinated-minus-unvaccinated daily difference in percentage points beside the slider. This uses unshifted deposited fractions and requires both groups to have observations at the selected day; it never extrapolates. Filters and playback update the annotations in both presentation modes.

A separate badge identifies **published whole-curve evidence**, currently the Figure 2B strain-595 comparison reported as **p < 0.05**, with a nine-day earlier median positivity time. Source: Read et al., [Onward Transmission and Statistical Analyses](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1002198#sec004), checked November 6, 2026. The paper specifies Mantel–Cox comparisons of Kaplan–Meier curves. The badge stays constant across days: it is not a pointwise test, an exact p-value, or an independently reproduced significance analysis. The curated mapping is in `dist/app.js` (`reportedComparisons`).

Other panel/strain combinations explicitly say “p-value unavailable”; this must not be interpreted as nonsignificance. No additional hypothesis tests or confidence intervals are inferred from the prepared plotting tables. The expandable explanation covers the statistical scope and shared-isolator clustering. Statistical significance alone does not establish that a claim is true or generalizable.

## Virtual cohort simulation

Below the figure, the live dot display defaults to **N = 200 total virtual birds**, split evenly between vaccinated-donor and unvaccinated-donor groups. Total N can be changed from 20 to 1,000. The simulation has its own strain selector and always compares both groups, independently of the chart’s visibility filters. It shares the chart’s outcome and day; its local scrubber, play/pause, and replay controls also update the chart.

- **Scale observed proportions:** round `(N/2) × original ones / original n` to whole virtual birds. A stable shuffled rank preserves monotone state changes as time advances.
- **Resample bird histories:** sample N/2 complete deposited records with replacement within each strain/endpoint/donor group. A deterministic pseudorandom draw is held fixed across days; “Draw another cohort” changes it. This assumes independent draws from the empirical distribution of included histories. Dot locations have no spatial or contact meaning.

Source counts and follow-up horizons stay visible; states outside a group’s source horizon become unknown, without extrapolation. Display offsets never enter the simulation. Positivity and survival are simulated separately because their original denominators and identifiers do not permit reliable individual linkage.

This is a conditional teaching simulation, not an expanded dataset, a prediction of a 200-bird experiment, a transmission-network model, or a power analysis. It cannot estimate between-isolator variation or unobserved outcomes. Resampling a zero-event block always yields zero events, which does not establish zero risk. No new p-values or confidence intervals are computed. Implementation: `dist/simulation.js`.
