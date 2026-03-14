# -*- coding: utf-8 -*-
fa=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','r',encoding='utf-8').read()

# FIX 1: Add periodsData rendering at end of loadSetup
# Anchor: the assignments innerHTML line ending, just before toggleTeacher
old_setup_end = '}).join("") : UI.em'
# We need a more unique anchor - use the removeAssignment line
old_anchor = '}).join("") : UI.empty("No assignments yet");\n}'
new_anchor = '}).join("") : UI.empty("No assignments yet");\n\n  // Render periods\n  const periods = periodsData ? (periodsData.periods || periodsData) : [];\n  const pContainer = document.getElementById("setup-periods");\n  if(pContainer){\n    pContainer.innerHTML = periods.length\n      ? periods.map(p=>`<div style="display:flex;align-items:center;gap:10px;padding:10px;border:1px solid var(--border);border-radius:6px;margin-bottom:8px"><div style="flex:1"><strong>${p.name}</strong><span style="color:var(--text-3);font-size:.8rem;margin-left:8px">${p.start_time||""}${p.start_time&&p.end_time?" - ":""}${p.end_time||""}</span><span style="margin-left:8px">${UI.badge(p.session_type==="Normal"?"Normal":"Extended","blue")}</span></div><button class="btn btn-ghost btn-sm" onclick="editPeriod(${p.id},\'${p.name}\',\'${p.start_time||""}\',\'${p.end_time||""}\',\'${p.session_type}\')">Edit</button><button class="btn btn-ghost btn-sm" style="color:var(--danger)" onclick="deletePeriod(${p.id})">Del</button></div>`).join("")\n      : "<p style=\'color:var(--text-3)\'>No periods yet. Add one below.</p>";\n  }\n}'

if old_anchor in fa:
    fa=fa.replace(old_anchor, new_anchor)
    print('FIX 1 done - period rendering added to loadSetup')
else:
    # Try to find what the assignments empty text actually says
    import re
    m=re.search(r'UI\.empty\("[^"]*assign[^"]*"\);\n\}', fa)
    if m:
        print('Found assignments empty at:', m.group())
    else:
        print('FIX 1 FAILED - searching for assignments area...')
        pos=fa.find('setup-assign-list')
        print(repr(fa[pos:pos+300]))

# FIX 2: Add Period Management HTML card before </div><!-- /page-content -->
old_page_end = '  </div>\n\n  </div><!-- /page-content -->'
period_card = '''
    <!-- PERIOD MANAGEMENT -->
    <div class="card" style="margin-top:20px" id="section-periods-card">
      <div class="card-header">
        <span class="card-title">Period Management</span>
        <button class="btn btn-primary btn-sm" onclick="document.getElementById('add-period-form').style.display='block'">+ Add Period</button>
      </div>
      <div id="setup-periods"><div style="color:var(--text-3);padding:12px">Loading periods...</div></div>
      <div id="add-period-form" style="display:none;margin-top:16px;padding:16px;background:var(--bg-2);border-radius:8px">
        <h4 style="margin:0 0 12px;color:var(--gold)">Add / Edit Period</h4>
        <input type="hidden" id="period-edit-id" value="">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div><label class="form-label">Period Name *</label><input class="form-control" id="period-name" placeholder="e.g. Period 1"></div>
          <div><label class="form-label">Session Type</label>
            <select class="form-select" id="period-session">
              <option value="Normal">Normal</option>
              <option value="Extended Teaching">Extended Teaching</option>
            </select>
          </div>
          <div><label class="form-label">Start Time</label><input type="time" class="form-control" id="period-start"></div>
          <div><label class="form-label">End Time</label><input type="time" class="form-control" id="period-end"></div>
        </div>
        <div style="margin-top:12px;display:flex;gap:10px">
          <button class="btn btn-primary" onclick="savePeriod()">Save Period</button>
          <button class="btn btn-ghost" onclick="document.getElementById('add-period-form').style.display='none';document.getElementById('period-edit-id').value=''">Cancel</button>
        </div>
      </div>
    </div>'''

new_page_end = period_card + '\n\n  </div><!-- /page-content -->'

if old_page_end in fa:
    fa=fa.replace(old_page_end, new_page_end)
    print('FIX 2 done - Period card HTML added to page')
else:
    print('FIX 2 FAILED - page-content end not found')

# FIX 3: Make sure loadSetup fetches periodsData
old_promise = 'async function loadSetup() {\n  const [teachers, classes, subjects, assignments, users, periodsData] = await Promise.all([\n    Api.get("/admin/teachers"), Api.get("/admin/classes"),\n    Api.get("/admin/subjects"),'
if old_promise in fa:
    print('FIX 3 - Promise.all already has periodsData, checking it fetches /admin/periods...')
    pos=fa.find(old_promise)
    print(repr(fa[pos:pos+400]))
else:
    print('FIX 3 - Promise.all missing periodsData, checking current state...')
    pos=fa.find('async function loadSetup')
    print(repr(fa[pos:pos+300]))

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','w',encoding='utf-8').write(fa)
print('DONE - file saved!')
