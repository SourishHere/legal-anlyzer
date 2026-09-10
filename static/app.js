const file=document.getElementById('file');
const name=document.getElementById('name');
const eventBox=document.getElementById('event');
const button=document.getElementById('analyze');
const status=document.getElementById('status');
file.onchange=()=>{name.textContent=file.files.length?`${file.files.length} evidence file(s) selected`:'Upload photos, screenshots or PDFs — multiple files supported'};
const fill=(id,items)=>{const el=document.getElementById(id);el.innerHTML='';(items||[]).forEach(x=>{const li=document.createElement('li');li.textContent=x;el.appendChild(li)});if(!items?.length)el.innerHTML='<li>None detected</li>'};
button.onclick=async()=>{
 if(!eventBox.value.trim()){status.textContent='Describe the event first.';return}
 if(!file.files.length){status.textContent='Add at least one evidence file.';return}
 const fd=new FormData(); fd.append('event',eventBox.value.trim()); [...file.files].slice(0,8).forEach(f=>fd.append('files',f));
 button.disabled=true; status.textContent='Comparing event with evidence…';
 try{const r=await fetch('/api/analyze',{method:'POST',body:fd});const d=await r.json();if(d.error)throw Error(d.error);
 document.getElementById('score').textContent=`${d.event_match_score}/100`;
 document.getElementById('match').textContent=d.event_match_summary;
 fill('supported',d.supported_claims);fill('missing',d.missing_verification);fill('facts',d.facts_from_evidence);fill('dates',d.dates);
 const box=document.getElementById('evidence');box.innerHTML='';(d.evidence||[]).forEach(e=>{const card=document.createElement('div');card.className='evidence-card';card.innerHTML=`<h3>${escapeHtml(e.file)}</h3><p><strong>Textual support:</strong> ${e.supports_event}/100</p><ul>${(e.observations||[]).map(x=>`<li>${escapeHtml(x)}</li>`).join('')}</ul>`;box.appendChild(card)});
 document.getElementById('analysis').textContent=d.case_analysis;document.getElementById('text').textContent=d.extracted_text||'No text extracted.';document.getElementById('results').classList.remove('hidden');status.textContent=d.warnings?.join(' ')||'Analysis complete.';
 }catch(e){status.textContent='Error: '+e.message}finally{button.disabled=false}
};
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]))}
