"""Independent artifact and accounting audit for the delivered investigation."""
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime, timezone
import json, hashlib
import pandas as pd
import nbformat
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]

def main():
    checks=[]
    def check(label,condition):
        assert condition,label
        checks.append({'requirement':label,'status':'verified'})
    manifest=json.loads((ROOT/'sources/download_manifest.json').read_text())+[json.loads((ROOT/'sources/poultry_manifest.json').read_text())]
    check('Source URLs, retrieval dates and snapshot SHA256 hashes',all(m.get('url') and m.get('retrieved_at') and hashlib.sha256((ROOT/m['path']).read_bytes()).hexdigest()==m['sha256'] for m in manifest))
    # Independent pandas read of the original wide Tableau crosstab.
    raw=pd.read_csv(ROOT/'data/raw/A Table by Confirmation Date.csv',encoding='utf-16',sep='\t',skiprows=1,dtype=str)
    birdcells=raw.iloc[:,5:].replace(',','',regex=True).apply(pd.to_numeric,errors='raise')
    p=pd.read_csv(ROOT/'data/processed/poultry.csv',parse_dates=['date'])
    check('No poultry rows lost and one affected-bird cell per source event',len(raw)==len(p) and birdcells.notna().sum(axis=1).eq(1).all())
    check('Affected-bird accounting agrees independently with raw export',int(birdcells.sum().sum())==int(p.birds_affected.sum()))
    check('Source confirmation dates retained instead of release dates',pd.to_datetime(raw.iloc[:,0].ffill(),format='%d-%b-%Y').reset_index(drop=True).equals(p.date))
    check('WOAH Non-Poultry separated from primary poultry outcome',p.is_poultry.equals(~p.production.eq('WOAH Non-Poultry')))
    m=pd.read_csv(ROOT/'results/monthly.csv',parse_dates=['date']);inf=p[p.is_poultry&p.date.ge('2022-03-01')&p.date.lt('2026-11-01')]
    check('Complete-month primary counts reconcile to event records',int(m.loc[m.date.ge('2022-03-01')&m.date.lt('2026-11-01'),'poultry'].sum())==len(inf)==1417)
    annual=pd.read_csv(ROOT/'results/annual_by_group.csv')
    check('Annual descriptive event/bird totals reconcile',annual.events.sum()==len(p) and annual.birds.sum()==p.birds_affected.sum())
    h=json.loads((ROOT/'results/hypotheses.json').read_text())
    check('Four hypotheses and sensitivities have executed results',all(k in h for k in ['H1','H2','H3','H4_exploratory','H1_negative_binomial','H1_full_years','H2_full_years','H3_full_years','holm_p']))
    for k in ['H2','H3']:
        t=pd.read_csv(ROOT/('results/h2_season_type.csv' if k=='H2' else 'results/h3_state_year.csv'),index_col=0)
        check(k+' table matches inferential sample size',int(t.to_numpy().sum())==h[k]['n'])
    png=sorted((ROOT/'figures').glob('*.png'));svg=sorted((ROOT/'figures').glob('*.svg'))
    check('At least five high-resolution figures plus geographic visualization',len(png)==len(svg)==8 and (ROOT/'figures/04_geography.svg').exists() and all(Image.open(f).width>=2000 for f in png))
    nb=nbformat.read(ROOT/'investigation.ipynb',as_version=4);nbformat.validate(nb)
    code=[c for c in nb.cells if c.cell_type=='code']
    check('Notebook code executed with no error outputs',all(c.execution_count is not None for c in code) and not any(o.output_type=='error' for c in code for o in c.outputs))
    check('Notebook contains all eight embedded figures',sum('image/png' in o.get('data',{}) for c in code for o in c.outputs)==8)
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.targets=[];self.ids=[]
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if 'id' in a:self.ids.append(a['id'])
            for k in ['href','src']:
                if k in a:self.targets.append(a[k])
    report=(ROOT/'REPORT.html').read_text();parser=Links();parser.feed(report)
    local=[u for u in parser.targets if not u.startswith(('http:','https:','#'))]
    check('Report relative figure, source, code and notebook links resolve',all((ROOT/u).is_file() for u in local))
    check('Report reference anchors resolve',all(u[1:] in parser.ids for u in parser.targets if u.startswith('#')))
    check('Scientific report includes required sections and follow-up questions',all(x in report for x in ['Abstract','Background','Hypotheses','methodology','Results','Discussion','Limitations','References','Three follow-up questions']))
    check('Reproduction instructions and dependency files present',all((ROOT/f).is_file() for f in ['README.txt','requirements.txt','requirements-lock.txt','scripts/acquire.py','scripts/download_poultry.py','scripts/analyze.py','scripts/build_notebook.py']))
    check('Hypothesis plan saved before processed analysis outputs',(ROOT/'analysis-plan.txt').stat().st_mtime<(ROOT/'data/processed/poultry.csv').stat().st_mtime)
    result={'audited_at':datetime.now(timezone.utc).isoformat(),'status':'passed','checks':checks,'evidence_note':'These checks verify artifacts and internal accounting, not surveillance completeness or causal validity. Visual review was also performed on all eight figures and the rendered report.'}
    (ROOT/'results/completion_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'Passed {len(checks)} artifact and accounting checks.')
if __name__=='__main__':main()
