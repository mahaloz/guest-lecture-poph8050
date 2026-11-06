#!/usr/bin/env python3
"""Attempt the official public download; record failure without inventing data."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent
URLS = ['https://datadryad.org/downloads/file_stream/46842',
        'https://datadryad.org/api/v2/files/46842/download']
EXPECTED_MD5 = '78419ef9559d4c5ad71de6888905bf0b'
archive = ROOT/'data/Fig2_and_S2.zip'
if archive.exists() and hashlib.md5(archive.read_bytes()).hexdigest() == EXPECTED_MD5:
    print('Using existing checksum-verified Fig2_and_S2.zip. No download needed.')
    raise SystemExit(0)
log = {'attempted_utc':datetime.now(timezone.utc).isoformat(),
       'doi':'10.5061/dryad.4tn48','file':'Fig2_and_S2.zip',
       'expected_bytes':19907,'expected_md5':EXPECTED_MD5,'requests':[]}
for url in URLS:
    try:
        r = requests.get(url, timeout=30)
        record = {'url':url,'status':r.status_code,'bytes':len(r.content),
                  'content_type':r.headers.get('Content-Type')}
        if r.ok and r.content[:2] == b'PK':
            digest = hashlib.md5(r.content).hexdigest()
            assert digest == EXPECTED_MD5, f'Unexpected archive digest: {digest}'
            (ROOT/'data/Fig2_and_S2.zip').write_bytes(r.content)
            record['verified_md5'] = digest
            log['download_succeeded'] = True
        log['requests'].append(record)
    except requests.RequestException as e:
        log['requests'].append({'url':url,'error':str(e)})
log.setdefault('download_succeeded',False)
(ROOT/'sources/download_attempt.json').write_text(json.dumps(log,indent=2))
print(json.dumps(log,indent=2))
if not log['download_succeeded']:
    print('No archive downloaded. Try the public link in Firefox; reproduce.py requires the verified ZIP and does not fall back to digitization.')
