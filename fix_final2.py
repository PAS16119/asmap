# -*- coding: utf-8 -*-
fa=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','r',encoding='utf-8').read()

# FIX A: Add /admin/periods to Promise.all (currently missing)
old_promise = '    Api.get("/admin/teachers"), Api.get("/admin/classes"),\n    Api.get("/admin/subjects"), Api.get("/admin/coordinator/assignments"),\n    Api.get("/admin/users")\n  ]);'
new_promise = '    Api.get("/admin/teachers"), Api.get("/admin/classes"),\n    Api.get("/admin/subjects"), Api.get("/admin/coordinator/assignments"),\n    Api.get("/admin/users"), Api.get("/admin/periods")\n  ]);'

if old_promise in fa:
    fa=fa.replace(old_promise, new_promise)
    print('FIX A done - /admin/periods added to Promise.all')
else:
    print('FIX A FAILED')
    pos=fa.find('Api.get("/admin/users")\n  ]);')
    print(repr(fa[pos-200:pos+50]))

# FIX B: Add period rendering at end of loadSetup
# The regex found the anchor ends with };  (semicolon then newline then })
old_anchor = 'UI.empty("No assignments yet");\n}'
new_anchor = 'UI.empty("No assignments yet");\n\n  // Render periods\n  const periods = periodsData ? (periodsData.periods || periodsData) : [];\n  const pContainer = document.getElementById("setup-periods");\n  if(pContainer){\n    pContainer.innerHTML = periods.length\n      ? periods.map(p=>`<div style="display:flex;align-items:center;gap:10px;padding:10px;border:1px solid var(--border);border-radius:6px;margin-bottom:8px"><div style="flex:1"><strong>${p.name}</strong><span style="color:var(--text-3);font-size:.8rem;margin-left:8px">${p.start_time||""}${p.start_time&&p.end_time?" - ":""}${p.end_time||""}</span><span style="margin-left:8px">${UI.badge(p.session_type==="Normal"?"Normal":"Extended","blue")}</span></div><button class="btn btn-ghost btn-sm" onclick="editPeriod(${p.id},\'${p.name}\',\'${p.start_time||""}\',\'${p.end_time||""}\',\'${p.session_type}\')">Edit</button><button class="btn btn-ghost btn-sm" style="color:var(--danger)" onclick="deletePeriod(${p.id})">Del</button></div>`).join("")\n      : "<p style=\'color:var(--text-3)\'>No periods yet. Add one below.</p>";\n  }\n}'

count = fa.count(old_anchor)
print('Anchor occurrences:', count)
if count == 1:
    fa=fa.replace(old_anchor, new_anchor)
    print('FIX B done - period rendering added to loadSetup')
elif count > 1:
    print('Multiple matches - need more unique anchor, showing context...')
    import re
    for m in re.finditer(r'UI\.empty\("No assignments yet"\);\n\}', fa):
        print('At pos', m.start(), ':', repr(fa[m.start()-100:m.start()+50]))
else:
    print('FIX B FAILED - anchor not found')
    import re
    m=re.search(r'UI\.empty\("[^"]*"\);\n\}', fa)
    if m: print('Similar pattern found:', repr(m.group()))

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','w',encoding='utf-8').write(fa)
print('File saved!')
