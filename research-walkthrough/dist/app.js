'use strict';
const R = window.RESEARCH;
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const steps = [
 {name:'Read the paper',small:'Question & experimental design',status:'SOURCE VERIFIED',title:'Start with what was actually tested.',body:'Read et al. challenged chickens with existing strains of Marek’s disease virus. Figure 2 connects survival of infected donors with infection and survival of unvaccinated contact birds.',evidence:'Read: Results, Discussion, Materials and Methods, figure captions, and supporting-information descriptions. Not every supplementary attachment or cited study was analyzed.',link:'https://doi.org/10.1371/journal.pbio.1002198',linkText:'Open the primary paper ↗'},
 {name:'Find the data',small:'Dryad DOI & archive metadata',status:'REPOSITORY LOCATED',title:'A public repository, with the right archive.',body:'Dryad lists data and R code for all four experiments. Fig2_and_S2.zip is the archive for the figure selected here. Dataset metadata was accessible and saved.',evidence:'File ID 46842 · 19,907 bytes · MD5 78419ef9559d4c5ad71de6888905bf0b. Dryad displays July 6, 2016 as its publication date.',link:'https://doi.org/10.5061/dryad.4tn48',linkText:'Inspect the Dryad record ↗'},
 {name:'Attempt access',small:'Initial 403 / 401 obstacle',status:'INITIAL ACCESS FAILED',title:'Direct requests failed. The trail records it.',body:'The first programmatic download returned HTTP 403, while the API download returned HTTP 401. An initial image transcription was documented, then superseded when the user asked us to use Firefox.',evidence:'Earlier check: '+R.download.attempted_utc+'. This is historical status; the archive has now been recovered.',link:'assets/download_attempt.json',linkText:'Inspect the earlier failures ↗',blocked:true},
 {name:'Use Firefox',small:'Archive recovered & verified',status:'ORIGINAL DATA RECOVERED',title:'The browser download succeeded.',body:'Opened the public Dryad page in the user’s Firefox browser and clicked Fig2_and_S2.zip. Automatic validation allowed the file download; Firefox showed it completed. No CAPTCHA was solved.',evidence:'19,907 bytes · MD5 verified: '+R.recovery.verified_md5+'. Original R scripts and CSVs are saved locally. No image-derived coordinates enter the current analysis.',link:'assets/browser_download.json',linkText:'Inspect the successful recovery ↗'},
 {name:'Reproduce',small:'Deposited states → Python',status:'18 CURVES REPRODUCED',title:'Translate the authors’ calculation.',body:'Read the original R table selections, including skip and nrows. For each day, compute 100 × ones / included rows. Preserve the original display offsets separately from biological percentages.',evidence:'The default explorer shows daily states with no offsets. Publication view restores straight segments and confirmed ±2-point shifts. Both use the actual deposited records.',link:'#results',linkText:'Explore the data-derived figure →'},
 {name:'Check the claim',small:'Compare, qualify & document',status:'RESULTS AND LIMITS CHECKED',title:'Computational reproduction, with remaining limits.',body:'The 595 positivity tables first reach 50% at day 25 with vaccinated donors and day 34 with unvaccinated donors: nine days. Record counts and display offsets are now inspectable.',evidence:'Still not independently reproduced: original censoring decisions and p-values. The vaccinated-595 survival block ends with 1/7 alive; denominators differ across outcomes.',link:'#meaning',linkText:'Separate findings from inferences →'}
];
function showStep(i){
 $$('#steps button').forEach((b,j)=>{b.classList.toggle('selected',i===j);b.setAttribute('aria-pressed',String(i===j));});
 const s=steps[i];const box=$('#step-detail');box.replaceChildren();
 const status=document.createElement('span');status.className='result-label'+(s.blocked?' blocked':'');status.textContent=s.status;
 const h=document.createElement('h2');h.textContent=s.title;
 const p=document.createElement('p');p.textContent=s.body;
 const e=document.createElement('div');e.className='evidence';e.textContent=s.evidence;
 const a=document.createElement('a');a.href=s.link;a.textContent=s.linkText;
 if(s.link.startsWith('https:')){a.target='_blank';a.rel='noreferrer';}
 box.append(status,h,p,e,a);
}
steps.forEach((s,i)=>{const b=document.createElement('button');b.type='button';b.innerHTML=`<span class="step-number">${String(i+1).padStart(2,'0')}</span><span><strong>${s.name}</strong><small>${s.small}</small></span>`;b.addEventListener('click',()=>showStep(i));$('#steps').append(b);});
showStep(0);
function route(){const name=location.hash.slice(1)||'process';const target=['process','results','meaning','notebook'].includes(name)?name:'process';$$('.view').forEach(s=>s.hidden=s.id!==target);$$('nav [data-view]').forEach(a=>{a.classList.toggle('active',a.dataset.view===target);if(a.dataset.view===target)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});if(target!=='results')stop();window.scrollTo(0,0);}
window.addEventListener('hashchange',route);
const colors={'595':'#228b22',Md5:'#3030ff','675A':'#ff1010'};
const titles={A:'Survival of experimentally infected donors',B:'MDV positivity in unvaccinated contacts',C:'Survival of unvaccinated contacts'};
let panel='A',timer=null;
function stop(){if(timer!==null)clearInterval(timer);timer=null;$('#play').textContent='▶';$('#play').setAttribute('aria-label','Play through recorded figure');$('#sim-play').textContent='▶';$('#sim-play').setAttribute('aria-label','Play virtual cohort');}
function selected(){const strains=$$('#strains input:checked').map(i=>i.value);const donor=$('#donors').value;return R.curves.filter(c=>c.panel===panel&&strains.includes(c.strain)&&(donor==='both'||c.donor_vaccinated===(donor==='yes')));}
function rawAt(c,t){if(t<c.day[0]||t>c.day[c.day.length-1])return null;const i=Math.floor(t)-1;return {value:c.percent[i],ones:c.records.reduce((sum,r)=>sum+r.state[i],0),n:c.n};}
function valueAt(c,t){if(t<c.day[0]||t>c.day[c.day.length-1])return null;if($('#plot-mode').value==='states')return rawAt(c,t).value;for(let i=1;i<c.day.length;i++){if(t<=c.day[i]){const f=(t-c.day[i-1])/(c.day[i]-c.day[i-1]);return c.drawn_percent[i-1]+f*(c.drawn_percent[i]-c.drawn_percent[i-1]);}}return c.drawn_percent[c.drawn_percent.length-1];}
function inspectRecords(){const c=R.curves.find(c=>c.r_object===($('#record-group').value.split('|')[1])&&c.panel===$('#record-group').value.split('|')[0]);const tbody=$('#record-rows');tbody.replaceChildren();if(!c){$('#record-source').textContent='Select a strain to inspect a record block.';return;}$('#record-source').textContent=`${c.source_file} · skip ${c.skip}, nrows ${c.n} · ${c.n} included records · days ${c.day[0]}–${c.day.at(-1)}. One means ${c.panel==='B'?'positive':'alive'}.`;for(const r of c.records){const i=r.state.findIndex(v=>v!==r.state[0]);const tr=document.createElement('tr');for(const v of [r.record_index,r.deposited_id,i<0?'None in supplied interval':'Day '+c.day[i],r.state.at(-1)]){const td=document.createElement('td');td.textContent=v;tr.append(td);}tbody.append(tr);}}
function fillRecordGroups(curves){const select=$('#record-group'),old=select.value;select.replaceChildren();for(const c of curves){const o=document.createElement('option');o.value=c.panel+'|'+c.r_object;o.textContent=`${c.panel} · ${c.strain} · ${c.donor_vaccinated?'vaccinated':'unvaccinated'} donors (n=${c.n})`;select.append(o);}if([...select.options].some(o=>o.value===old))select.value=old;inspectRecords();}
// Source checked 2026-11-06: Read et al. (2015), Onward Transmission,
// Fig 2B, strain 595. Methods: Mantel–Cox tests of Kaplan–Meier curves.
// These are curated published results, not p-values calculated from daily states.
const reportedComparisons = {
 B: {'595': {label:'p < 0.05 · reported',detail:'595 contacts became positive earlier with vaccinated donors; median shift: 9 days. Whole follow-up; test not rerun.',source:'https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.1002198#sec004'}}
};
function drawStatistics(curves,day){
 $('#statistical-day').textContent=`Day ${Math.floor(day)} · ${panel==='B'?'MDV positivity':'survival'} · differences in percentage points (pp)`;
 const tbody=$('#statistical-rows');tbody.replaceChildren();
 for(const strain of Object.keys(colors)){
  const groups=curves.filter(c=>c.strain===strain);if(!groups.length)continue;
  const tr=document.createElement('tr');
  const th=document.createElement('th');th.scope='row';th.textContent=strain;th.style.color=colors[strain];tr.append(th);
  const delta=document.createElement('td'),evidence=document.createElement('td');
  const vaccinated=groups.find(c=>c.donor_vaccinated),unvaccinated=groups.find(c=>!c.donor_vaccinated);
  const a=vaccinated?rawAt(vaccinated,day):null,b=unvaccinated?rawAt(unvaccinated,day):null;
  if(!vaccinated||!unvaccinated){
   delta.textContent='Select both donor groups';
  }else if(a===null||b===null){
   delta.textContent='Outside shared follow-up';
  }else{
   const difference=a.value-b.value;
   delta.textContent=`${difference>0?'+':''}${difference.toFixed(1)} pp`;
  }
  const result=reportedComparisons[panel]?.[strain];
  if(!vaccinated||!unvaccinated){
   evidence.textContent='Comparison hidden';
  }else if(result){
   const link=document.createElement('a');link.className='stat-badge reported';link.textContent=result.label;link.href=result.source;link.target='_blank';link.rel='noreferrer';
   const detail=document.createElement('small');detail.textContent=result.detail;
   evidence.append(link,detail);
  }else{
   const badge=document.createElement('span');badge.className='stat-badge';badge.textContent='p-value unavailable';
   const detail=document.createElement('small');detail.textContent='Descriptive comparison; significance not established here.';
   evidence.append(badge,detail);
  }
  tr.append(delta,evidence);tbody.append(tr);
 }
 if(!curves.length){const tr=document.createElement('tr'),td=document.createElement('td');td.colSpan=3;td.textContent='Select at least one strain to see its statistical context.';tr.append(td);tbody.append(tr);}
}
const NS='http://www.w3.org/2000/svg';
function el(tag,attrs,text){const e=document.createElementNS(NS,tag);Object.entries(attrs||{}).forEach(([k,v])=>e.setAttribute(k,v));if(text!==undefined)e.textContent=text;return e;}
function draw(){
 const svg=$('#chart');svg.replaceChildren(el('title',{id:'chart-access-title'},titles[panel]),el('desc',{id:'chart-access-desc'},'Deposited bird-state data. Solid lines: vaccinated donors; dotted lines: unvaccinated donors. Contact birds were unvaccinated.'));
 const x=t=>65+t/56*715,y=p=>330-(p+4)/108*290;
 const curves=selected(),day=Number($('#day').value);
 for(let p=0;p<=100;p+=20){svg.append(el('line',{x1:65,x2:780,y1:y(p),y2:y(p),stroke:'#e7ece3'}),el('text',{x:52,y:y(p)+4,'text-anchor':'end',fill:'#718076','font-size':12},p+'%'));}
 for(let t=0;t<=56;t+=7){svg.append(el('text',{x:x(t),y:352,'text-anchor':'middle',fill:'#718076','font-size':12},t),el('line',{x1:x(t),x2:x(t),y1:40,y2:330,stroke:'#f0f3ed'}));}
 svg.append(el('text',{x:420,y:380,'text-anchor':'middle',fill:'#64716b','font-size':12},'Days since experimental infection of donor birds'));
 const clip=el('clipPath',{id:'reveal-clip'});clip.append(el('rect',{x:60,y:25,width:Math.max(0,x(day)-60),height:310}));const defs=el('defs');defs.append(clip);svg.append(defs);
 for(const c of curves){const publication=$('#plot-mode').value==='publication',values=publication?c.drawn_percent:c.percent;const path=c.day.map((t,i)=>i?(publication?'L'+x(t).toFixed(2)+','+y(values[i]).toFixed(2):'H'+x(t).toFixed(2)+' V'+y(values[i]).toFixed(2)):'M'+x(t).toFixed(2)+','+y(values[i]).toFixed(2)).join(' ');const attrs={d:path,fill:'none',stroke:colors[c.strain],'stroke-width':3,'stroke-linejoin':'round','stroke-linecap':'round'};if(!c.donor_vaccinated)attrs['stroke-dasharray']='2 7';svg.append(el('path',{...attrs,opacity:.12}),el('path',{...attrs,'clip-path':'url(#reveal-clip)'}));const v=valueAt(c,day);if(v!==null){const circle=el('circle',{cx:x(day),cy:y(v),r:4,fill:colors[c.strain],stroke:'white','stroke-width':1.5});circle.append(el('title',{},`${c.strain}, ${c.donor_vaccinated?'vaccinated':'unvaccinated'} donors: ${v.toFixed(1)} drawn %`));svg.append(circle);}}
 svg.append(el('line',{x1:x(day),x2:x(day),y1:30,y2:330,stroke:'#586d60','stroke-width':1,'stroke-dasharray':'4 4'}));
 if(!curves.length)svg.append(el('text',{x:420,y:180,'text-anchor':'middle',fill:'#64716b','font-size':16},'Select at least one strain to show its traces.'));
 $('#chart-title').textContent=titles[panel];$('#day-output').textContent='Day '+day.toFixed(1);$('#reading-title').textContent='Daily record fractions · day '+Math.floor(day);
 const tbody=$('#readout');tbody.replaceChildren();
 for(const strain of Object.keys(colors)){if(!curves.some(c=>c.strain===strain))continue;const tr=document.createElement('tr');const th=document.createElement('th');th.scope='row';th.textContent=strain;th.style.color=colors[strain];tr.append(th);for(const v of [true,false]){const c=curves.find(c=>c.strain===strain&&c.donor_vaccinated===v),val=c?rawAt(c,day):null;const td=document.createElement('td');td.textContent=val===null?'—':val.value.toFixed(1)+'% ('+val.ones+'/'+val.n+')';tr.append(td);}tbody.append(tr);}
 if(!curves.length){const tr=document.createElement('tr');const td=document.createElement('td');td.colSpan=3;td.textContent='No strains selected';tr.append(td);tbody.append(tr);}
 drawStatistics(curves,day);
 drawSimulation(day);
 fillRecordGroups(curves);
}
function setPanel(p){panel=p;$$('#panel-tabs button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.panel===p)));draw();}
$$('#panel-tabs button').forEach(b=>b.addEventListener('click',()=>setPanel(b.dataset.panel)));
$$('#strains input').forEach(b=>b.addEventListener('change',draw));$('#donors').addEventListener('change',draw);$('#plot-mode').addEventListener('change',draw);$('#record-group').addEventListener('change',inspectRecords);$('#day').addEventListener('input',()=>{stop();draw();});
$('#play').addEventListener('click',()=>{if(timer!==null){stop();return;}if(Number($('#day').value)>=56)$('#day').value='0';$('#play').textContent='Ⅱ';$('#play').setAttribute('aria-label','Pause figure playback');timer=setInterval(()=>{const d=Math.min(56,Number($('#day').value)+.2);$('#day').value=String(d);draw();if(d>=56)stop();},70);draw();});
$('#reset').addEventListener('click',()=>{stop();cohortSeed=1;$('#sim-strain').value='595';$('#sim-size').value='200';$('#sim-mode').value='scaled';$$('#strains input').forEach(i=>i.checked=true);$('#donors').value='both';$('#plot-mode').value='states';$('#day').value='56';setPanel('A');});
$('#highlight').addEventListener('click',()=>{stop();$('#sim-strain').value='595';$$('#strains input').forEach(i=>i.checked=i.value==='595');$('#donors').value='both';$('#plot-mode').value='states';$('#day').value='34';setPanel('B');});
for(const id of ['sim-strain','sim-size','sim-mode'])$('#'+id).addEventListener('change',()=>drawSimulation(Number($('#day').value)));
$('#sim-resample').addEventListener('click',()=>{cohortSeed++;drawSimulation(Number($('#day').value));});
$('#sim-panel').addEventListener('change',()=>setPanel($('#sim-panel').value));
$('#sim-day').addEventListener('input',()=>{$('#day').value=$('#sim-day').value;stop();draw();});
$('#sim-play').addEventListener('click',()=>$('#play').click());
$('#sim-restart').addEventListener('click',()=>{stop();$('#day').value='1';$('#play').click();});
$('#reveal').addEventListener('click',()=>{const visible=$('#answer').hidden;$('#answer').hidden=!visible;$('#reveal').setAttribute('aria-expanded',String(visible));$('#reveal').textContent=visible?'Hide explanation ↑':'Reveal the distinction ↓';});
const limits=[
 ['The original figure calculation is reproduced, not every statistical analysis.','The original ZIP and R/CSV sources were obtained and verified. Python translates the supplied table selections and column means. It does not independently re-estimate original exclusions, censoring, risk sets, confidence intervals, or p-values. The R interpreter was unavailable; R code was inspected and translated, not executed.'],
 ['Birds within an isolator are not independent transmission replicates.','The main strain-by-treatment contact groups occupy one isolator each. Shared environment and exposure create clustering. Additional 675A donor-only groups enlarge survival data, not independent contact-transmission replication.'],
 ['Detection time is not the moment of infection.','Contacts were tested at scheduled times. First sustained qPCR positivity interval-censors infection acquisition and does not identify who infected whom. Later contact cases may result from contact-to-contact transmission. Genome detection is not infectious-particle titration.'],
 ['Challenge conditions restrict generalization.','The selected experiment used particular chicken ages, breed, maternal-antibody status, HVT vaccination, and strains. Experimental donor inoculation differs from natural acquisition. The wider paper includes maternal and commercial-bird experiments, but those figures were not numerically audited here.'],
 ['Survival endpoints and denominators require the original records.','Humane-endpoint euthanasia counted as infection-induced death, and crowding-related removals were excluded. The 675A donor survival data pool additional groups. The actual vaccinated-595 contact block ends with 1/7 alive on day 53 despite the prose describing eventual death of all infected contacts. Positivity and survival block counts differ; many IDs are placeholders. The methods describe pooled 675A donor survival, while the figure code selects 20 unvaccinated and 9 vaccinated rows.'],
 ['Transmission opportunity is not a complete evolutionary model.','These experiments use pre-existing strains. They do not observe new virulence mutations, establish historical causes, estimate a universal persistence threshold or selection coefficient, or isolate a survival-only causal mediation effect. Virulence and antigenic escape are different traits.'],
 ['Shedding proxies have their own limits.','Genome shedding is not a directly measured selection coefficient. Later 595/Md5 dust samples in Experiment 2 can include virus from contacts. Those shedding calculations were not reproduced in this work.'],
 ['This does not establish a human-vaccine effect or policy verdict.','The chicken–MDV result cannot establish an equivalent effect for human vaccines, including COVID-19 vaccines. Net population benefit or harm requires additional evidence. No independent animal replication, exhaustive subsequent-literature review, retraction audit, or policy evaluation was performed.']
];
for(const [title,body] of limits){const d=document.createElement('details');const s=document.createElement('summary');s.textContent=title;const plus=document.createElement('span');plus.textContent='+';s.append(plus);const p=document.createElement('p');p.textContent=body;d.append(s,p);$('#limits').append(d);}
function showDoc(doc){$$('#notebook-tabs button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.doc===doc)));const box=$('#notebook-content');box.replaceChildren();if(doc==='method'){box.innerHTML="<p class=\"eyebrow\">VERIFIED ARCHIVE \u2192 ORIGINAL R \u2192 CSV STATES \u2192 PYTHON</p><h2>Reproduce the calculation from actual deposited records.</h2><p>The original archive was recovered through Firefox and its MD5 matches Dryad. None of the current curves use image-derived coordinates.</p><ol><li>Verify Fig2_and_S2.zip against the repository checksum.</li><li>Read Figure2_ThreePanel.R from the archive.</li><li>Parse its skip and nrows settings for each table block.</li><li>Load the selected binary states and validate day headers and monotonicity.</li><li>Compute the included-record percentage for each day.</li><li>Reproduce the publication lines and keep \u00b12-point display shifts separate.</li></ol><p><code>percent = 100 \u00d7 number of ones / included rows</code></p><p>Panel A uses DataFor2A_v2.csv; B uses DataFor2C.csv; C uses DataFor2D_v2.csv. One means alive in A/C and positive in B. The R script\u2019s internal panel comments differ from the displayed labels.</p><p><strong>Two views:</strong> daily steps without offsets, or the original straight-line plotting conventions with selected offsets. The record table always reports actual daily fractions. Traces are never extrapolated beyond the supplied horizon.</p><p>595 first reaches at least 50% positive on day 25 (4/7) with vaccinated donors and day 34 (5/10) with unvaccinated donors. This confirms nine days without image interpolation; it does not reproduce the significance test.</p><p>The archive contains prepared state tables, not original qPCR amplification files or a complete censoring ledger. Many IDs are placeholders. Original R was inspected, not executed in an R interpreter.</p><p>Rerun from the repository root:</p><pre>reproduction/.venv/bin/python reproduction/reproduce.py\npython3 research-walkthrough/prepare_assets.py\npython3 research-walkthrough/serve.py</pre><p>The original image-only attempt is retained for history. It has been superseded in the current analysis.</p>";}else{const pre=document.createElement('pre');pre.textContent=doc==='download'?JSON.stringify({initial_attempt:R.download,browser_recovery:R.recovery},null,2):doc==='code'?R.code:doc==='rCode'?R.rCode:R.report;box.append(pre);}box.scrollTop=0;}
$$('#notebook-tabs button').forEach(b=>b.addEventListener('click',()=>showDoc(b.dataset.doc)));
draw();showDoc('method');route();
