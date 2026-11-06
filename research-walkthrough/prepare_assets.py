"""Bundle the data-derived reproduction and audit history for the local app."""
import json
import shutil
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent
src = root.parent / 'reproduction'
a = root / 'dist/assets'
a.mkdir(parents=True, exist_ok=True)
for rel in ['sources/published_figure2.png', 'outputs/figure2_from_data.png',
            'outputs/figure2_states.png', 'outputs/data_comparison.png',
            'outputs/data_curves.json', 'REPORT.md', 'reproduce.py',
            'download_data.py', 'requirements.txt', 'data/Fig2_and_S2.zip',
            'sources/download_attempt.json', 'sources/browser_download.json',
            'REPORT_image_attempt.md']:
    shutil.copy2(src / rel, a / Path(rel).name)
(a / 'REPORT.md').write_text((src / 'REPORT.md').read_text().replace('outputs/data_comparison.png', 'data_comparison.png'))
with zipfile.ZipFile(src / 'data/Fig2_and_S2.zip') as archive:
    for name in ['DataFor2A_v2.csv', 'DataFor2C.csv', 'DataFor2D_v2.csv', 'Figure2_ThreePanel.R']:
        (a / name).write_bytes(archive.read('Fig2_and_S2/' + name))
    r_code = archive.read('Fig2_and_S2/Figure2_ThreePanel.R').decode('utf-8-sig')
data = {'curves': json.loads((src / 'outputs/data_curves.json').read_text()),
        'summary': json.loads((src / 'outputs/data_summary.json').read_text()),
        'download': json.loads((src / 'sources/download_attempt.json').read_text()),
        'recovery': json.loads((src / 'sources/browser_download.json').read_text()),
        'code': (src / 'reproduce.py').read_text(), 'rCode': r_code,
        'report': (src / 'REPORT.md').read_text(),
        'downloader': (src / 'download_data.py').read_text()}
(root / 'dist/data.js').write_text('window.RESEARCH = ' + json.dumps(data) + ';\n')
print('Bundled data-derived curves, selected bird records, original archive/R/CSVs, and recovery record.')
