"""Export the official APHIS detail worksheet through its public Tableau UI.
Requires `playwright install chromium`. No credentials required.
Worksheet-selection approach independently implemented after inspecting
https://github.com/casey891/hpai-dashboard/blob/main/tableau_export.py .
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
URL='https://publicdashboards.dl.usda.gov/t/MRP_PUB/views/VS_Avian_HPAIConfirmedDetections2022/HPAI2022ConfirmedDetections?:embed=y&:isGuestRedirectFromVizportal=y&:refresh=yes'
SHEET='X - Table by Confirmation Date'
if __name__=='__main__':
    target=ROOT/'data/raw/A Table by Confirmation Date.csv'
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        page=browser.new_page(accept_downloads=True,viewport={'width':1600,'height':1200})
        page.goto(URL,wait_until='domcontentloaded',timeout=90000)
        page.get_by_role('button',name='Download Crosstab').click(timeout=90000)
        option=page.get_by_role('option',name=SHEET,exact=True)
        option.scroll_into_view_if_needed();option.click(force=True)
        assert option.get_attribute('aria-selected')=='true'
        page.get_by_role('radio',name='csv').click(force=True)
        with page.expect_download(timeout=90000) as event:
            page.get_by_role('dialog',name='Download Crosstab').get_by_role('button',name='Download',exact=True).click(force=True)
        temp=target.with_suffix('.tmp');event.value.save_as(temp)
        text=temp.read_text(encoding='utf-16')
        assert 'Confirmed Diagnosis' in text and 'Special ID' in text and len(text.splitlines())>100
        temp.replace(target);browser.close()
    meta={'url':URL,'worksheet':SHEET,'path':str(target.relative_to(ROOT)),'retrieved_at':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size}
    (ROOT/'sources/poultry_manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
