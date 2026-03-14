fc=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()

old='''  fetch(base+'/admin/subjects',{headers:h}).then(function(r){return r.json();}).then(function(d){
    var sel=document.getElementById('monSubject');if(!sel)return;
    (d.subjects||[]).forEach(function(s){var o=document.createElement('option');o.value=s.id;o.textContent=s.name;sel.appendChild(o);});
  }).catch(function(){});'''

new='''  fetch(base+'/admin/subjects',{headers:h}).then(function(r){return r.json();}).then(function(d){
    var sel=document.getElementById('monSubject');if(!sel)return;
    (d.subjects||[]).forEach(function(s){var o=document.createElement('option');o.value=s.id;o.textContent=s.name;sel.appendChild(o);});
  }).catch(function(){});
  fetch(base+'/admin/periods/active',{headers:h}).then(function(r){return r.json();}).then(function(d){
    var sel=document.getElementById('monPeriod');if(!sel)return;
    (d.periods||[]).forEach(function(p){var o=document.createElement('option');o.value=p.label;o.textContent=p.label;sel.appendChild(o);});
  }).catch(function(){});'''

if old in fc:
    fc=fc.replace(old,new)
    print('Period API load added to coordinator')
else:
    print('Pattern not found')

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','w',encoding='utf-8').write(fc)
