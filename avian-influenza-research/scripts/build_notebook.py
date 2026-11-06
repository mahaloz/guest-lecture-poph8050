"""Create and execute the research notebook with this Python environment."""
from pathlib import Path
import sys
import nbformat as nbf
from nbclient import NotebookClient
from jupyter_client import KernelManager
ROOT=Path(__file__).resolve().parents[1]
def main():
 md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
 cells=[md('''# Understanding U.S. bird flu outbreak patterns
Executed observational investigation using frozen official APHIS data, retrieved **6 November 2026**.

The question is what patterns appear in poultry detections and what might explain them. Detection records, affected flocks and affected birds are distinct units. This notebook executes the analysis in `scripts/analyze.py`; the complete methods and critical interpretation are in `REPORT.html`.

## 1. Hypotheses and provenance
The analysis plan was written before computing summaries; it was informed by source schemas and literature, not registered publicly. H1 tests spring/autumn versus summer, H2 production-group seasonal composition, H3 state/year composition, and H4 an exploratory wild-bird lead. Raw snapshots are never silently refreshed.'''),
 code("from pathlib import Path\nimport sys, json\nimport pandas as pd\nfrom IPython.display import display, Image, HTML\nROOT = Path.cwd()\nassert (ROOT / 'analysis-plan.txt').exists()\nsys.path.insert(0, str(ROOT / 'scripts'))\nimport analyze\nprint((ROOT / 'analysis-plan.txt').read_text())\ndisplay(pd.DataFrame(analyze.verify_sources())[['path', 'retrieved_at', 'sha256']])"),
 md('''## 2. Clean and validate
The poultry export is UTF-16 and tab-delimited. Control-area release dates are column headings; confirmation dates are row fields. We validate one bird-count cell per event and fill repeated Tableau row headings. We preserve repeated public signatures because they may represent distinct flocks or wild birds.

The primary poultry outcome excludes WOAH Non-Poultry. The unqualified WOAH Poultry production label serves as a backyard-poultry proxy, supported by APHIS reporting conventions. It is not an independent backyard flag.'''),
 code("p, w, validation = analyze.clean()\ndisplay(pd.Series(validation, name='Validation'))\ndisplay(p.head())\ndisplay(p.groupby('group').agg(events=('date','size'), affected_birds=('birds_affected','sum')))"),
 md('''## 3. Explore the calendar and choose comparable months
Zero reported rows are zero detections in this snapshot, not proof of zero infections. We exclude February 2022 and November 2026 from inference. All records remain in full-window descriptive summaries. Seasonal contrasts use a calendar-day offset, never a susceptible-flock denominator.'''),
 code("m = analyze.monthly(p, w)\ncomplete = m.loc['2022-03-01':'2026-10-01']\nprint('Complete analysis months:', len(complete))\ndisplay(complete.groupby(['year','season'], observed=True).agg(events=('poultry','sum'), days=('days','sum')))"),
 md('''## 4. Execute the hypothesis tests
Poisson seasonal models use year effects and HAC(3) covariance. A negative-binomial sensitivity addresses overdispersion. Seasonal-type tests permute type within year, and the geographic test permutes year across events; outbreak clustering limits exchangeability. Holm adjustment covers the two planned H1 contrasts plus H2/H3. All sensitivities and H4 are exploratory.'''),
 code("h = analyze.hypotheses(p, w, m)\ndisplay(pd.DataFrame(h['H1']))\nprint('Holm adjusted primary p:', h['holm_p'])\nprint('Poisson dispersion:', h['H1_dispersion'])\ndisplay(pd.DataFrame(h['H1_negative_binomial']))\ndisplay(pd.DataFrame({k:h[k] for k in ['H2','H2_full_years','H2_including_nonpoultry','H3','H3_full_years']}).T)\nprint('Exploratory wild-bird lag:', json.dumps(h['H4_exploratory'], indent=2))"),
 md('''## 5. Investigate results that complicate the initial story
Winter has a high seasonal estimate: the important pattern is broader than spring and autumn. The commercial/backyard comparison changes when edge years are removed; a universal group difference would be misleading. Bird totals can be dominated by a few large egg-layer events.

Confirmation delays may exceed the proposed one-month wildlife warning interval. Missing collection dates and impossible negative intervals are flagged, rather than repaired by guessing. Collection-date sensitivities exclude impossible intervals and remain subject to retrospective availability bias.'''),
 code("display(pd.read_csv(ROOT/'results/h2_by_year.csv'))\ndisplay(pd.read_csv(ROOT/'results/season_by_year.csv'))\ndisplay(pd.read_csv(ROOT/'results/production_totals.csv').head(8))\nprint('Collection delay percentiles:', validation['wild_delay_quantiles_days'])\nprint('Collection delays over 30 days:', validation['wild_delay_over_30_days'])\nprint('Invalid collection-date tokens:', validation['wild_invalid_collection_tokens'])\nprint('Negative intervals:', validation['wild_negative_delay'])\nprint('Burden summary:', (ROOT/'results/descriptive.json').read_text())"),
 md('''## 6. Generate and inspect the figures
Publication assets are saved as 300-dpi PNG and editable vector SVG. State maps include Alaska, Hawaii and Puerto Rico insets. Geographic colors represent counts, not risks. All figures below are generated by the executed code.'''),
 code("analyze.figures(p, w, m, h)\nfor path in sorted((ROOT/'figures').glob('*.png')):\n    print(path.name)\n    display(Image(filename=str(path), width=1000))"),
 md('''## 7. Interpretation and comparison with primary research
The evidence supports a summer lull and changing geographic composition. Pooled production-group differences are not robust to the choice of years. The adjusted one-month wildlife lead is not established by these national monthly records. A null association at this resolution does not negate wildlife transmission.

[Damodaran et al., Nature](https://www.nature.com/articles/s41586-025-09737-x) reconstructed repeated wildlife introductions with sequence data; that is a different estimand from national count correlations. [Ssematimba et al., PLoS ONE](https://pmc.ncbi.nlm.nih.gov/articles/PMC11642945/) inferred infection-to-detection intervals using within-flock observations unavailable here. [Harrington et al., Nature Medicine](https://www.nature.com/articles/s41591-026-04300-1) documented D1.1 spread during autumn 2024; our event table cannot assign genotype-specific causes. The [APHIS September 2025 report](https://www.aphis.usda.gov/sites/default/files/hpai-epi-report-fy25-q4.pdf) also documents common-source/lateral and dairy-associated pathways.

Confounding by geography, production, husbandry, weather and surveillance prevents causal attribution. No infection rates or individual-bird mortality estimates are computed.

### Three follow-up questions
1. Can timely county-week wildlife data predict held-out poultry outbreaks beyond a seasonal baseline?
2. Do geographic differences persist with compatible production-specific susceptible-flock denominators?
3. Do winter peaks reflect weather, genotype introductions, dairy-associated transmission or local farm clusters?

The report expands these questions into data requirements and discusses NASS and NOAA sources.'''),
 code("import build_report\nbuild_report.main()\nprint('Report generated:', (ROOT/'REPORT.html').exists())\nprint('Figure pairs:', len(list((ROOT/'figures').glob('*.png'))), len(list((ROOT/'figures').glob('*.svg'))))")]
 nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python (HPAI research)','language':'python','name':'python3'},'language_info':{'name':'python','version':sys.version.split()[0]}})
 km=KernelManager(kernel_name='python3');km.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
 client=NotebookClient(nb,km=km,timeout=180,resources={'metadata':{'path':str(ROOT)}})
 client.execute();nbf.write(nb,ROOT/'investigation.ipynb')
 km.shutdown_kernel(now=True)
 print('Executed notebook saved:',ROOT/'investigation.ipynb')
if __name__=='__main__':main()
