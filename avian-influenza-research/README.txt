UNDERSTANDING U.S. BIRD FLU
Official APHIS public data retrieved 6 November 2026.

START HERE
From the repository root, run ./demo3.sh to serve this project and open the
report in your browser. No dependency installation or analysis rerun is needed.
Use ./demo3.sh --port 0 for a free port; press Ctrl+C to stop the server.
Open REPORT.html in a browser. It contains the scientific report, references,
eight figures, limitations, and three follow-up questions.
Open investigation.ipynb in Jupyter for the executed step-by-step investigation.
The notebook embeds outputs and all eight figures.

REPRODUCE THE FROZEN ANALYSIS (no data downloads)
Tested with Python 3.9.6 on macOS arm64. Python 3.9–3.12 recommended.
From this directory:
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
  .venv/bin/python scripts/analyze.py
  .venv/bin/python scripts/build_report.py
  .venv/bin/python scripts/build_notebook.py

The analyze.py command runs validation, hypothesis tests, sensitivities and figures.
The notebook builder executes the same analysis in a fresh Python kernel, then
saves the executed notebook. It can take a minute. To inspect interactively,
install JupyterLab separately and select the environment's kernel, or use an
editor's notebook support. Notebook execution itself needs no JupyterLab.
requirements-lock.txt records the exact full environment used for delivery;
requirements.txt pins the direct dependencies used by the code.

SOURCE REFRESH (explicit; changes the dataset and analysis inputs)
  .venv/bin/python scripts/acquire.py
  .venv/bin/python -m pip install playwright==1.60.0
  .venv/bin/python -m playwright install chromium
  .venv/bin/python scripts/download_poultry.py
Then inspect coverage and change CUTOFF in scripts/analyze.py and the dated
analysis/report text before rerunning. This is a frozen investigation, not a
live dashboard. The current cutoff excludes November 2026. Report prose is tied
to this snapshot: rebuilding after a source update requires scientific review,
not only rerunning code. APHIS may change worksheet names and export formats.
A successful file hash check verifies the supplied snapshot, not completeness
of APHIS surveillance.

DIRECTORY
  analysis-plan.txt       Hypotheses and planned tests written before summaries
  REPORT.html            Scientific report with embedded relative figure links
  investigation.ipynb    Executed research notebook with embedded figures
  data/raw/              Original official poultry/wildlife bytes and Census map
  data/processed/        Cleaned event and surveillance tables
  sources/               URLs, retrieval dates, SHA256 manifests, archived pages
  scripts/               Download, cleaning, analysis and report/notebook code
  results/               Validation, model summaries, CSV tables and JSON results
  figures/               Eight 300-dpi PNG and eight vector SVG visualizations

UNITS AND SCOPE
2,300 domestic-bird detection events; primary poultry subset excludes 874 WOAH
Non-Poultry records, leaving 1,426 poultry events. Main tests use 1,417 poultry
events in 56 complete months (March 2022–October 2026).
Affected birds are reported flock-size burden, not confirmed individual
infections or natural deaths. “Special ID” labels are not validated stable farm
identifiers. Wild-bird positive rows do not include negative-test denominators.
No infection rates, causal transmission claims or intervention guidance.

KNOWN LIMITATIONS
Backyard poultry is inferred from APHIS's unqualified “WOAH Poultry” label.
Calendar-year edge coverage differs; full-year sensitivities are reported.
Recent months may be incomplete even before the retrieval month. Wildlife
confirmation dates can lag collection by months; unknown and invalid collection
dates are flagged. Repeated signatures are retained because IDs are absent or
event-specific. P-values depend on model/exchangeability assumptions; spatial
and temporal clustering can make them optimistic. Read the report before
interpreting the figures as evidence for a mechanism.
