#!/usr/bin/env python3
"""Reproduce Read et al. Figure 2 from checksum-verified deposited bird-state data.

Translate Figure2_ThreePanel.R's table selections and 100*colMeans calculation.
No image-derived coordinates enter this analysis. The comparison image is QA only.
"""
import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
ARCHIVE = ROOT / 'data/Fig2_and_S2.zip'
MD5 = '78419ef9559d4c5ad71de6888905bf0b'
COLORS = {'595': '#228b22', 'Md5': '#3030ff', '675A': '#ff1010'}
FILES = {'A': 'DataFor2A_v2.csv', 'B': 'DataFor2C.csv', 'C': 'DataFor2D_v2.csv'}
LABELS = {'A': 'Experimentally infected donors alive (%)',
          'B': 'Unvaccinated contacts MDV positive (%)',
          'C': 'Unvaccinated contacts alive (%)'}


def load_curves():
    """Read original archive, parse table slices named in the original R script."""
    if not ARCHIVE.exists():
        raise FileNotFoundError(f'{ARCHIVE}: obtain Fig2_and_S2.zip from Dryad first.')
    assert hashlib.md5(ARCHIVE.read_bytes()).hexdigest() == MD5, 'Archive checksum mismatch'
    curves = []
    with zipfile.ZipFile(ARCHIVE) as archive:
        prefix = 'Fig2_and_S2/'
        script = archive.read(prefix + 'Figure2_ThreePanel.R').decode('utf-8-sig')
        for panel, filename in FILES.items():
            lines = archive.read(prefix + filename).decode('utf-8-sig').splitlines()
            pattern = (r'(SOK_(NonVax|HVT)_(675A|Md5|595))\s*=read.table\("' +
                       re.escape(filename) + r'", sep=",", skip=(\d+), header=TRUE, nrows=(\d+)\)')
            selections = list(re.finditer(pattern, script))
            assert len(selections) == 6, (panel, len(selections))
            for match in selections:
                r_name, vaccine, strain = match.group(1, 2, 3)
                skip, n = int(match.group(4)), int(match.group(5))
                header = next(csv.reader([lines[skip]]))
                rows = list(csv.reader(lines[skip+1:skip+1+n]))
                days = [int(v) for v in header[3:]]
                states = np.array([[int(v) for v in row[3:]] for row in rows], dtype=int)
                assert states.shape == (n, len(days)), (r_name, states.shape)
                assert np.isin(states, [0, 1]).all()
                assert days == list(range(1, len(days)+1)), 'R lines(y) uses implicit x=1..N'
                change = np.diff(states, axis=1)
                assert (change >= 0).all() if panel == 'B' else (change <= 0).all()
                percent = 100 * states.mean(axis=0)
                # Reproduce intentional R JitterSize=2, separately from biological values.
                offset = 2 if panel == 'A' and vaccine == 'HVT' and strain == 'Md5' else 0
                if panel == 'B' and vaccine == 'NonVax' and strain == 'Md5': offset = -2
                if panel == 'C' and vaccine == 'NonVax' and strain == 'Md5': offset = 2
                curves.append({'panel': panel, 'strain': strain,
                               'donor_vaccinated': vaccine == 'HVT',
                               'day': days, 'percent': percent.tolist(),
                               'drawn_percent': (percent + offset).tolist(),
                               'display_offset': offset, 'n': n,
                               'source_file': filename, 'skip': skip, 'r_object': r_name,
                               'records': [{'record_index': i+1,
                                            'deposited_id': row[2],
                                            'state': states[i].tolist()}
                                           for i, row in enumerate(rows)]})
    return curves


def make_summary(curves):
    selected = [c for c in curves if c['panel'] == 'B' and c['strain'] == '595']
    crossings = {}
    for c in selected:
        crossings['vaccinated_donors' if c['donor_vaccinated'] else 'unvaccinated_donors'] = next(
            day for day, value in zip(c['day'], c['percent']) if value >= 50)
    crossings['difference_days'] = crossings['unvaccinated_donors'] - crossings['vaccinated_donors']
    crossings['meaning'] = 'First deposited day at >=50% positive; no interpolation, no new significance test.'
    crossings['groups'] = [{k: c[k] for k in ['panel', 'strain', 'donor_vaccinated', 'n', 'source_file']} |
                           {'last_day': c['day'][-1], 'final_ones': sum(r['state'][-1] for r in c['records']),
                            'final_percent': c['percent'][-1]} for c in curves]
    return crossings


def plot(curves, publication=True):
    fig, axes = plt.subplots(3, 1, figsize=(10, 10.5), sharex=True)
    for c in curves:
        ax = axes['ABC'.index(c['panel'])]
        values = c['drawn_percent'] if publication else c['percent']
        ax.plot(c['day'], values, color=COLORS[c['strain']], lw=2.4,
                ls='-' if c['donor_vaccinated'] else (0, (1.3, 2.1)),
                drawstyle='default' if publication else 'steps-post')
    for panel, ax in zip('ABC', axes):
        ax.set(title=f'{panel}  {LABELS[panel]}', xlim=(-1, 57),
               ylim=(-4, 104), yticks=np.arange(0, 101, 20), xticks=np.arange(0, 57, 7))
        ax.grid(alpha=.18); ax.spines[['top', 'right']].set_visible(False)
        ax.set_ylabel('Percent')
    axes[-1].set_xlabel('Days since experimental infection of donor birds')
    handles = [Line2D([], [], color=COLORS[s], lw=3, label=s) for s in COLORS]
    handles += [Line2D([], [], color='black', lw=2, label='HVT-vaccinated donors'),
                Line2D([], [], color='black', lw=2, ls=':', label='Unvaccinated donors')]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, .945), ncol=3, frameon=False)
    fig.suptitle('Figure 2 — Python reproduction from deposited data', fontsize=17, y=.99)
    note = 'Original R plotting conventions: straight segments and selected ±2 point offsets.' if publication else 'Daily recorded states: step view, no display offsets. Not a new Kaplan–Meier fit.'
    fig.text(.5, .01, note+'\nRead et al., PLOS Biology (2015), doi:10.1371/journal.pbio.1002198; Dryad: 10.5061/dryad.4tn48', ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .045, 1, .89))
    name = 'figure2_from_data' if publication else 'figure2_states'
    fig.savefig(OUT/f'{name}.png', dpi=180)
    fig.savefig(OUT/f'{name}.svg')
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    curves = load_curves()
    (OUT/'data_curves.json').write_text(json.dumps(curves, indent=2))
    summary = make_summary(curves)
    (OUT/'data_summary.json').write_text(json.dumps(summary, indent=2))
    for publication in [True, False]: plot(curves, publication)
    fig, axes = plt.subplots(1, 2, figsize=(14, 10))
    for ax, filename, title in zip(axes,
            [ROOT/'sources/published_figure2.png', OUT/'figure2_from_data.png'],
            ['Published Figure 2 (Read et al., CC BY)', 'Python: deposited CSVs + original R conventions']):
        ax.imshow(Image.open(filename)); ax.set_title(title, fontsize=12); ax.axis('off')
    fig.tight_layout(); fig.savefig(OUT/'data_comparison.png', dpi=160); plt.close(fig)
    # Independent count-based check of column means, including exact numerator/denominator.
    for c in curves:
        counts = [sum(r['state'][j] for r in c['records']) for j in range(len(c['day']))]
        assert np.allclose(c['percent'], [100*k/c['n'] for k in counts], atol=1e-12)
    assert len(curves) == 18
    print(f'18 data-derived curves verified. 595: day {summary["vaccinated_donors"]} versus {summary["unvaccinated_donors"]}; difference {summary["difference_days"]} days.')


if __name__ == '__main__':
    main()
