'use strict';
let cohortSeed=1;
// A deterministic draw per record block, reused at every time point.
function cohortRandom(key){
 let seed=2166136261;
 for(const ch of key)seed=Math.imul(seed^ch.charCodeAt(0),16777619);
 return ()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
}
function virtualStates(curve,n,day,mode,seed){
 const raw=rawAt(curve,day);
 if(raw===null)return Array(n).fill(null);
 const random=cohortRandom(`${curve.panel}|${curve.strain}|${curve.donor_vaccinated}|${seed}`);
 if(mode==='resampled'){
  return Array.from({length:n},()=>curve.records[Math.floor(random()*curve.n)].state[Math.floor(day)-1]);
 }
 // A stable shuffled rank gives round(n*p) active dots and monotone histories.
 const ranks=Array.from({length:n},(_,i)=>i);
 for(let i=n-1;i>0;i--){const j=Math.floor(random()*(i+1));[ranks[i],ranks[j]]=[ranks[j],ranks[i]];}
 const count=Math.round(n*raw.ones/raw.n);
 return ranks.map(rank=>Number(rank<count));
}
function drawSimulation(day){
 const strain=$('#sim-strain').value,total=Number($('#sim-size').value),n=total/2,mode=$('#sim-mode').value;
 const positive=panel==='B',on=positive?'positive':'alive',off=positive?'not detected positive':'dead';
 $('#flock-title').textContent=`What would ${total} birds look like?`;
 $('#sim-evidence-count').textContent=String(total);
 $('#sim-context').textContent=`${total} virtual ${panel==='A'?'donor':'contact'} birds total · ${n} per group · strain ${strain} · ${mode==='scaled'?'scaled observed proportions':`resampled histories · draw ${cohortSeed}`} · shares the chart’s outcome and day. Strain and group visibility here are independent of chart filters.`;
 $('#sim-panel').value=panel;$('#sim-day').value=String(day);$('#sim-day-output').textContent=`Day ${day.toFixed(1)}`;
 $('#sim-play').textContent=timer===null?'▶':'Ⅱ';$('#sim-play').setAttribute('aria-label',timer===null?'Play virtual cohort':'Pause virtual cohort');
 $('#sim-resample').disabled=mode!=='resampled';
 $('#sim-on-label').textContent=positive?'Detected positive':'Alive';$('#sim-off-label').textContent=positive?'Not detected positive':'Dead (×)';
 const counts=[];
 for(const [id,vaccinated] of [['vax',true],['unvax',false]]){
  const c=R.curves.find(c=>c.panel===panel&&c.strain===strain&&c.donor_vaccinated===vaccinated);
  const states=virtualStates(c,n,day,mode,cohortSeed),raw=rawAt(c,day),active=states.filter(v=>v===1).length;
  const name=vaccinated?'Vaccinated donors':'Unvaccinated donors';
  $(`#sim-${id}-label`).textContent=panel==='A'?name:`Contacts of ${name.toLowerCase()}`;
  $(`#sim-${id}-count`).textContent=raw===null?`${n} virtual birds · state unknown`:`${active}/${n} ${on} · ${n-active} ${off}`;
  $(`#sim-${id}-source`).textContent=`Original block: n=${c.n} birds · days ${c.day[0]}–${c.day.at(-1)}${raw===null?' · no source state on this day':` · observed ${raw.ones}/${raw.n} ${on} (${raw.value.toFixed(1)}%)`}`;
  const grid=$(`#sim-${id}-dots`);
  if(grid.children.length!==n){grid.replaceChildren(...Array.from({length:n},()=>{const dot=document.createElement('span');dot.setAttribute('aria-hidden','true');return dot;}));}
  states.forEach((state,i)=>{
   const status=state===null?'unknown':state===1?'on':'off',dot=grid.children[i];
   dot.className=`bird-dot ${status}${!positive&&state===0?' mortality':''}`;
   dot.dataset.state=state===null?'unknown':String(state);
   dot.textContent=!positive&&state===0?'×':'';
  });
  counts.push(raw===null?null:active);
 }
 $('#sim-comparison').textContent=counts.some(v=>v===null)?'Move within both observation windows to compare groups. Replay from day 1 to watch the histories unfold.':`${mode==='scaled'?'Scaled':'Resampled'} difference: ${counts[0]-counts[1]>0?'+':''}${counts[0]-counts[1]} ${on} birds with vaccinated donors. This is an illustration, not a significance test.`;
}
