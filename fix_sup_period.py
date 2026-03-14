import re
fs=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\supervisor.html','r',encoding='utf-8').read()

# Replace hardcoded period select with empty one loaded by API
fs=re.sub(
    r'<select[^>]*id="period"[^>]*>.*?</select>',
    '<select id="period" class="form-control"><option value="">Loading periods...</option></select>',
    fs, flags=re.DOTALL
)

# Add period loading to initForm or DOMContentLoaded
# Find where subjects are loaded in supervisor
subj_load='fetch(base+\'/admin/subjects\''
pos=fs.find(subj_load)
if pos>=0:
    # Find end of that fetch block
    end=fs.find('.catch(function(){});',pos)+len('.catch(function(){});')
    period_fetch='''\n  var base2=(typeof API_BASE!==\'undefined\')?API_BASE:\'http://localhost:5000/api\';
  var tok2=localStorage.getItem(\'asmap_token\');
  fetch(base2+\'/admin/periods/active\',{headers:{\'Authorization\':\'Bearer \'+tok2}}).then(function(r){return r.json();}).then(function(d){
    var sel=document.getElementById(\'period\');if(!sel)return;
    sel.innerHTML=\'<option value="">Select Period</option>\';
    (d.periods||[]).forEach(function(p){var o=document.createElement(\'option\');o.value=p.label;o.textContent=p.label;sel.appendChild(o);});
  }).catch(function(){});'''
    fs=fs[:end]+period_fetch+fs[end:]
    print('Supervisor period API load added')
else:
    print('Subject load not found in supervisor')

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\supervisor.html','w',encoding='utf-8').write(fs)
