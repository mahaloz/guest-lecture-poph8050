// DOM interaction checks, not a rendered-browser layout test.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {JSDOM}=require('jsdom');
const root=path.join(import.meta.dirname,'dist');
const dom=new JSDOM(fs.readFileSync(path.join(root,'index.html'),'utf8'),{url:'http://localhost/',runScripts:'outside-only'});
const {window:w}=dom;
w.scrollTo=()=>{};
let tick; w.setInterval=fn=>{tick=fn;return 1;};w.clearInterval=()=>{tick=null;};
w.eval(fs.readFileSync(path.join(root,'data.js'),'utf8'));
w.eval(fs.readFileSync(path.join(root,'app.js'),'utf8'));
const $=s=>w.document.querySelector(s), $$=s=>[...w.document.querySelectorAll(s)];
assert.equal($$('.view:not([hidden])').length,1);
assert.equal($('#process').hidden,false);
for(const b of $$('#steps button')){b.click();assert.equal(b.getAttribute('aria-pressed'),'true');assert.ok($('#step-detail h2').textContent.length>10);}
assert.match($('#step-detail').textContent,/p-values/);
for(const id of ['results','meaning','notebook','process']){w.location.hash=id;w.dispatchEvent(new w.HashChangeEvent('hashchange'));assert.equal($('#'+id).hidden,false);assert.equal($$('.view:not([hidden])').length,1);}
w.location.hash='results';w.dispatchEvent(new w.HashChangeEvent('hashchange'));
assert.equal($('#chart').querySelectorAll('path').length,12);
for(const b of $$('#panel-tabs button')){b.click();assert.equal(b.getAttribute('aria-pressed'),'true');assert.equal($('#chart').querySelectorAll('path').length,12);}
$('#highlight').click();assert.equal($('#day').value,'34');assert.equal($$('#readout tr').length,1);assert.match($('#chart-title').textContent,/positivity/);assert.match($('#readout').textContent,/595/);
$('#day').value='0';$('#day').dispatchEvent(new w.Event('input'));assert.match($('#readout').textContent,/—/);
$('#donors').value='yes';$('#donors').dispatchEvent(new w.Event('change'));assert.equal($('#chart').querySelectorAll('path').length,2);
$$('#strains input').forEach(b=>b.checked=false);$('#strains input').dispatchEvent(new w.Event('change'));assert.match($('#chart').textContent,/Select at least/);assert.match($('#readout').textContent,/No strains/);
$('#reset').click();assert.equal($('#day').value,'56');assert.equal($('#chart').querySelectorAll('path').length,12);
$('#play').click();assert.equal($('#day').value,'0');tick();assert.equal($('#day').value,'0.2');$('#play').click();assert.equal(tick,null);
$('#reveal').click();assert.equal($('#answer').hidden,false);$('#reveal').click();assert.equal($('#answer').hidden,true);
for(const b of $$('#notebook-tabs button')){b.click();assert.ok($('#notebook-content').textContent.length>300);}
$$('[src],[href]').forEach(e=>{const v=e.getAttribute('src')||e.getAttribute('href');if(!v||v.startsWith('#')||/^https?:/.test(v))return;assert.ok(fs.existsSync(path.join(root,v)),v+' exists');});
assert.equal($$('#limits details').length,8);
assert.equal(w.RESEARCH.summary.difference_days,9);
assert.equal(w.RESEARCH.recovery.download_succeeded,true);
assert.equal(w.RESEARCH.curves.length,18);
assert.equal($$('#steps button').length,6);
$('#highlight').click();
assert.match($('#readout').textContent,/100.0% \(7\/7\)/);
assert.match($('#readout').textContent,/50.0% \(5\/10\)/);
$('#day').value='25';$('#day').dispatchEvent(new w.Event('input'));
assert.match($('#readout').textContent,/57.1% \(4\/7\)/);
assert.equal($('#plot-mode').value,'states');
assert.match($('#chart path').getAttribute('d'),/H/);
$('#plot-mode').value='publication';$('#plot-mode').dispatchEvent(new w.Event('change'));
assert.ok(!$('#chart path').getAttribute('d').includes('H'));
assert.equal($('#record-rows').children.length,10);
$('#record-group').selectedIndex=1;$('#record-group').dispatchEvent(new w.Event('change'));
assert.equal($('#record-rows').children.length,7);
console.log('Passed: navigation, 6 process steps, 3 panels, all filters, empty state, reset, time playback, 595 highlight, claim reveal, 5 notebook tabs, record inspector, daily/publication modes, local links, and artifact consistency.');
w.close();
