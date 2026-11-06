"""Download source snapshots. Explicit refresh only; analysis uses frozen files."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, requests
ROOT=Path(__file__).resolve().parents[1]
def fetch(url,name):
    r=requests.get(url,timeout=60); r.raise_for_status()
    dest=ROOT/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(r.content)
    return {'url':url,'path':name,'retrieved_at':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(r.content).hexdigest(),'bytes':len(r.content)}
if __name__=='__main__':
    urls=[('https://www.aphis.usda.gov/sites/default/files/hpai-wild-birds.csv','data/raw/wild_birds.csv'),('https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_20m.zip','data/raw/states.zip'),('https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/commercial-backyard-flocks','sources/aphis_poultry.html'),('https://www.aphis.usda.gov/livestock-poultry-disease/avian/avian-influenza/hpai-detections/wild-birds','sources/aphis_wild.html')]
    manifest=[fetch(*x) for x in urls]
    (ROOT/'sources/download_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))
