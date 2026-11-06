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
