import re
fs=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\supervisor.html','r',encoding='utf-8').read()

# 1. Replace hardcoded rec-period select with empty one
fs=re.sub(
    r'<select class="form-select" id="rec-period">.*?</select>',
    '<select class="form-select" id="rec-period"><option value="">Select Period</option></select>',
    fs, flags=re.DOTALL
)

# 2. Add periods to Promise.all in initRecordForm
old='''  const [subjects, classes, teachers] = await Promise.all([
    Api.get("/admin/subjects"), Api.get("/admin/classes"), Api.get("/admin/teachers")
  ]);
  UI.populateSelect("rec-subject", subjects, "id", "subject_name", "Select subject\u2026");
  UI.populateSelect("rec-class",   classes,  "id", "class_name",   "Select class\u2026");'''

new='''  const [subjects, classes, teachers, periodsData] = await Promise.all([
    Api.get("/admin/subjects"), Api.get("/admin/classes"), Api.get("/admin/teachers"), Api.get("/admin/periods/active")
  ]);
  UI.populateSelect("rec-subject", subjects, "id", "subject_name", "Select subject\u2026");
  UI.populateSelect("rec-class",   classes,  "id", "class_name",   "Select class\u2026");
  const periods = periodsData.periods || [];
  const pSel = document.getElementById("rec-period");
  if(pSel){ pSel.innerHTML=\'<option value="">Select Period</option>\'+periods.map(p=><option value=""></option>).join(""); }'''

if old in fs:
    fs=fs.replace(old,new)
    print('Supervisor period API load fixed!')
else:
    print('Pattern not found')

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\supervisor.html','w',encoding='utf-8').write(fs)
