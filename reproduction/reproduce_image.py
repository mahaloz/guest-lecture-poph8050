#!/usr/bin/env python3
"""Reconstruct Figure 2 graphics from documented pixels, not inaccessible raw data."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)
d = json.loads((ROOT/'data/digitized_figure2.json').read_text())
cal = d['calibration']
colors = {'595':'#228b22','Md5':'#3030ff','675A':'#ff1010'}
labels = {'A':'Experimentally infected birds alive (%)',
          'B':'Contact birds MDV positive (%)', 'C':'Contact birds alive (%)'}
fig, axes = plt.subplots(3,1, figsize=(10,10.5), sharex=True)
converted = []
for c in d['curves']:
    xy = np.array(c['pixels'], dtype=float)
    t = (xy[:,0]-cal['x_day0'])*56/(cal['x_day56']-cal['x_day0'])
    cc = cal[c['panel']]
    y = (cc['y_0']-xy[:,1])*100/(cc['y_0']-cc['y_100'])
    assert np.all(np.diff(t)>=0) and np.isfinite(y).all()
    ax = axes['ABC'.index(c['panel'])]
    ax.plot(t,y,color=colors[c['strain']],lw=2.4,
            ls='-' if c['donor_vaccinated'] else (0,(1.3,2.1)))
    converted.append({k:v for k,v in c.items() if k!='pixels'} |
                     {'day':t.tolist(),'drawn_percent':y.tolist()})
for p,ax in zip('ABC',axes):
    ax.set(title=p+'  '+labels[p],xlim=(-1,57),ylim=(-4,104),
           yticks=np.arange(0,101,20),xticks=np.arange(0,57,7))
    ax.grid(alpha=.18); ax.spines[['top','right']].set_visible(False)
    ax.set_ylabel('Percent')
axes[-1].set_xlabel('Days since experimental infection of donor birds')
handles=[Line2D([],[],color=colors[s],lw=3,label=s) for s in colors]
handles += [Line2D([],[],color='black',lw=2,label='HVT-vaccinated donors'),
            Line2D([],[],color='black',lw=2,ls=':',label='Unvaccinated donors')]
fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.945),ncol=3,frameon=False)
fig.suptitle('Figure 2 — reconstruction from published image',fontsize=17,y=.99)
fig.text(.5,.01,'DIGITIZED GRAPHICS ONLY • not a raw-data reanalysis\nRead et al., PLOS Biology (2015), doi:10.1371/journal.pbio.1002198; source: CC BY',ha='center',fontsize=10)
fig.tight_layout(rect=(0,.045,1,.89))
fig.savefig(OUT/'figure2_reconstructed.png',dpi=180)
fig.savefig(OUT/'figure2_reconstructed.svg')
(OUT/'digitized_coordinates.json').write_text(json.dumps(converted,indent=2))
plt.close(fig)
# First crossing, rather than np.interp on the whole curve: plateaus have
# duplicate y values and would otherwise return the plateau's LAST time.
summary = {}
for c in converted:
    if c['panel'] == 'B' and c['strain'] == '595':
        y, t = np.array(c['drawn_percent']), np.array(c['day'])
        i = int(np.flatnonzero(y >= 50)[0])
        crossing = t[i-1] + (50-y[i-1])*(t[i]-t[i-1])/(y[i]-y[i-1])
        summary['vaccinated_donors' if c['donor_vaccinated'] else 'unvaccinated_donors'] = float(crossing)
summary['difference_days'] = summary['unvaccinated_donors'] - summary['vaccinated_donors']
summary['meaning'] = 'Approximate first 50% crossing of drawn 595 curves; not an independent survival analysis.'
(OUT/'graphical_summary.json').write_text(json.dumps(summary,indent=2))
# Original plus reconstruction for visual audit; no resampling-based fit statistic.
fig,ax=plt.subplots(1,2,figsize=(14,10))
for a,path,title in zip(ax,[ROOT/'sources/published_figure2.png',OUT/'figure2_reconstructed.png'],
                        ['Published Figure 2 (Read et al., CC BY)','Python reconstruction (digitized graphics)']):
    a.imshow(Image.open(path)); a.set_title(title,fontsize=12); a.axis('off')
fig.tight_layout(); fig.savefig(OUT/'comparison.png',dpi=160); plt.close(fig)
print('Wrote reconstructed PNG/SVG, comparison PNG, and digitized coordinates.')
