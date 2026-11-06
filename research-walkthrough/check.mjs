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
w.eval(['simulation.js','app.js'].map(file=>fs.readFileSync(path.join(root,file),'utf8')).join('\n'));
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
// Statistical context: keep the published full-follow-up test separate from daily effects.
const day=d=>{$('#day').value=String(d);$('#day').dispatchEvent(new w.Event('input'));};
const stats=()=>$('#statistical-rows').textContent;
$('#highlight').click();
assert.match(stats(),/\+50.0 pp/);
assert.match(stats(),/p < 0.05 · reported/);
assert.match(stats(),/Whole follow-up; test not rerun/);
assert.equal($('#statistical-rows a').getAttribute('href'),'https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1002198#sec004');
day(25);assert.match(stats(),/\+37.1 pp/);assert.match(stats(),/p < 0.05/);
day(25.9);assert.match(stats(),/\+37.1 pp/);assert.match($('#statistical-day').textContent,/Day 25/);
$('#plot-mode').value='publication';$('#plot-mode').dispatchEvent(new w.Event('change'));assert.match(stats(),/\+37.1 pp/);
day(1);assert.match(stats(),/0.0 pp/);assert.match(stats(),/p < 0.05/);
day(0);assert.match(stats(),/Outside shared follow-up/);
day(35);assert.match(stats(),/Outside shared follow-up/);assert.match(stats(),/p < 0.05/);
$('#donors').value='yes';$('#donors').dispatchEvent(new w.Event('change'));assert.match(stats(),/Select both donor groups/);assert.doesNotMatch(stats(),/p < 0.05/);
$('#donors').value='no';$('#donors').dispatchEvent(new w.Event('change'));assert.doesNotMatch(stats(),/p < 0.05/);
$('#reset').click();assert.equal($$('#statistical-rows tr').length,3);assert.equal($$('#statistical-rows .reported').length,0);assert.match(stats(),/p-value unavailable/);
for(const p of ['A','C']){$(`[data-panel="${p}"]`).click();day(9);assert.match(stats(),/p-value unavailable/);assert.doesNotMatch(stats(),/p < 0.05/);}
$('[data-panel="B"]').click();day(25);assert.equal($$('#statistical-rows .reported').length,1);assert.equal($$('#statistical-rows .stat-badge:not(.reported)').length,2);
$('#strains input[value="595"]').checked=false;$('#strains input').dispatchEvent(new w.Event('change'));assert.doesNotMatch(stats(),/p < 0.05/);
$$('#strains input').forEach(b=>b.checked=false);$('#strains input').dispatchEvent(new w.Event('change'));assert.match(stats(),/Select at least one strain/);
$('#highlight').click();$('#play').click();tick();assert.match($('#statistical-day').textContent,/Day 34/);assert.match(stats(),/p < 0.05/);$('#play').click();
assert.equal($('#day').getAttribute('aria-describedby'),'statistical-note');
// Virtual cohorts retain source horizons and persistent individual histories.
const change=(id,value)=>{$(id).value=value;$(id).dispatchEvent(new w.Event('change'));};
const nodes=id=>[...$(id).children].map(e=>e.dataset.state);
$('#reset').click();$('#highlight').click();
assert.equal($$('#sim-vax-dots .bird-dot').length,100);assert.equal($$('#sim-unvax-dots .bird-dot').length,100);
assert.match($('#sim-vax-count').textContent,/100\/100 positive/);assert.match($('#sim-unvax-count').textContent,/50\/100 positive/);
assert.match($('#sim-unvax-source').textContent,/n=10 birds/);assert.match($('#sim-vax-source').textContent,/n=7 birds/);
assert.equal($('#sim-resample').disabled,true);
day(25);assert.match($('#sim-vax-count').textContent,/57\/100 positive/);assert.match($('#sim-unvax-count').textContent,/20\/100 positive/);
const scaled=nodes('#sim-vax-dots');
change('#plot-mode','publication');assert.deepEqual(nodes('#sim-vax-dots'),scaled);
change('#sim-mode','resampled');assert.equal($('#sim-resample').disabled,false);
const draw1=nodes('#sim-vax-dots');day(26);day(25);assert.deepEqual(nodes('#sim-vax-dots'),draw1);
$('#sim-resample').click();assert.notDeepEqual(nodes('#sim-vax-dots'),draw1);assert.match($('#sim-context').textContent,/draw 2/);
for(const mode of ['scaled','resampled']){
 change('#sim-mode',mode);
 for(const outcome of ['A','B','C']){
  change('#sim-panel',outcome);assert.equal($(`[data-panel="${outcome}"]`).getAttribute('aria-pressed'),'true');
  for(const strain of ['595','Md5','675A']){
   change('#sim-strain',strain);day(1);let prev=nodes('#sim-vax-dots');
   for(let d=2;d<=30;d++){day(d);const current=nodes('#sim-vax-dots');current.forEach((v,i)=>{if(v==='unknown'||prev[i]==='unknown')return;if(outcome==='B')assert.ok(Number(v)>=Number(prev[i]));else assert.ok(Number(v)<=Number(prev[i]));});prev=current;}
  }
 }
}
$('#highlight').click();change('#sim-mode','resampled');day(0);assert.ok(nodes('#sim-vax-dots').every(s=>s==='unknown'));
day(35);assert.ok(nodes('#sim-vax-dots').every(s=>s==='unknown'));assert.ok(nodes('#sim-unvax-dots').every(s=>s!=='unknown'));assert.match($('#sim-comparison').textContent,/both observation windows/);
for(const total of ['20','50','100','200','500','1000']){change('#sim-size',total);assert.equal($$('.flock-dots .bird-dot').length,Number(total));}
change('#sim-strain','Md5');day(41);assert.ok(nodes('#sim-unvax-dots').every(s=>s==='0'));assert.ok(nodes('#sim-vax-dots').every(s=>s==='1'));
$('#sim-day').value='25';$('#sim-day').dispatchEvent(new w.Event('input'));assert.equal($('#day').value,'25');assert.equal($('#sim-day-output').textContent,'Day 25.0');
$('#sim-restart').click();assert.equal($('#day').value,'1');assert.match($('#sim-play').getAttribute('aria-label'),/Pause/);tick();assert.equal($('#sim-day').value,'1.2');$('#sim-play').click();assert.equal(tick,null);assert.match($('#sim-play').getAttribute('aria-label'),/Play/);
$('#reset').click();assert.equal($('#sim-size').value,'200');assert.equal($('#sim-mode').value,'scaled');assert.equal($('#sim-strain').value,'595');
assert.match($('#sim-assumptions').textContent,/do not become new observations/);
console.log('Passed: 200-bird virtual cohorts, exact scaled counts, persistent seeded draws, monotone trajectories across all strains/outcomes/modes, boundaries, zero-event groups, size changes, synchronized playback, reset, and source denominators.');
console.log('Passed: statistical annotations, published-result scope, day and horizon handling, both plot modes, all panel/strain/donor filters, empty state, and playback.');
console.log('Passed: navigation, 6 process steps, 3 panels, all filters, empty state, reset, time playback, 595 highlight, claim reveal, 5 notebook tabs, record inspector, daily/publication modes, local links, and artifact consistency.');
w.close();
