# -*- coding: utf-8 -*-
fa=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','r',encoding='utf-8').read()

# Add periods section to loadSetup
old_setup = 'async function loadSetup() {\n  const [teachers, classes, subjects, assignments, users] = await Promise.all([\n    Api.get("/admin/teachers"), Api.get("/admin/classes"),\n    Api.get("/admin/subjects"),'

new_setup = 'async function loadSetup() {\n  const [teachers, classes, subjects, assignments, users, periodsData] = await Promise.all([\n    Api.get("/admin/teachers"), Api.get("/admin/classes"),\n    Api.get("/admin/subjects"),'

if old_setup in fa:
    fa=fa.replace(old_setup, new_setup)
    print('loadSetup Promise.all updated')
else:
    print('loadSetup pattern not found - trying alternative')
    pos=fa.find('async function loadSetup')
    print(repr(fa[pos:pos+200]))

# Add period rendering after subjects rendering - find a good insert point
insert_after = 'sectionLoaded["setup"] = true;'
period_ui = '''
  // ── Periods ──────────────────────────────────────────────────────────
  const periods = periodsData.periods || [];
  const pContainer = document.getElementById("setup-periods");
  if(pContainer){
    pContainer.innerHTML = periods.length
      ? periods.map(p=>`
          <div style="display:flex;align-items:center;gap:10px;padding:10px;border:1px solid var(--border);border-radius:6px;margin-bottom:8px">
            <div style="flex:1">
              <strong>${p.name}</strong>
              <span style="color:var(--text-3);font-size:.8rem;margin-left:8px">${p.start_time||""}${p.start_time&&p.end_time?" - ":""}${p.end_time||""}</span>
              <span style="margin-left:8px">${UI.badge(p.session_type==="Normal"?"Normal":"Extended","blue")}</span>
            </div>
            <button class="btn btn-ghost btn-sm" onclick="editPeriod(${p.id},\'${p.name}\',\'${p.start_time||""}\',\'${p.end_time||""}\',\'${p.session_type}\')">Edit</button>
            <button class="btn btn-ghost btn-sm" style="color:var(--danger)" onclick="deletePeriod(${p.id})">Del</button>
          </div>`).join("")
      : "<p style=\'color:var(--text-3)\'>No periods yet. Add one below.</p>";
  }
'''

if insert_after in fa:
    fa=fa.replace(insert_after, insert_after+period_ui)
    print('Period rendering added to loadSetup')
else:
    print('insert_after not found')

# Add period management HTML to section-setup
period_html = '''
    <!-- PERIOD MANAGEMENT -->
    <div class="card" style="margin-top:20px">
      <div class="card-header">
        <span class="card-title">Period Management</span>
        <button class="btn btn-primary btn-sm" onclick="document.getElementById(\'add-period-form\').style.display=\'block\'">+ Add Period</button>
      </div>
      <div id="setup-periods"><div class="loading-overlay"><div class="spinner"></div></div></div>
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
          <button class="btn btn-ghost" onclick="document.getElementById(\'add-period-form\').style.display=\'none\'">Cancel</button>
        </div>
      </div>
    </div>
'''

# Insert before end of section-setup
setup_end = '  </div><!-- end section-setup -->'
if setup_end in fa:
    fa=fa.replace(setup_end, period_html+'\n'+setup_end)
    print('Period HTML added to section-setup')
else:
    # Try alternative
    setup_end2 = 'id="section-setup"'
    pos=fa.find(setup_end2)
    print('section-setup found at:',pos,'- need to find its closing div')

# Add period JS functions
period_js = '''
async function savePeriod() {
  const id = document.getElementById("period-edit-id").value;
  const body = {
    name: document.getElementById("period-name").value.trim(),
    start_time: document.getElementById("period-start").value||null,
    end_time: document.getElementById("period-end").value||null,
    session_type: document.getElementById("period-session").value
  };
  if(!body.name){ Toast.error("Period name required"); return; }
  try {
    if(id) await Api.put("/admin/periods/"+id, body);
    else await Api.post("/admin/periods", body);
    Toast.success("Period saved!");
    document.getElementById("add-period-form").style.display="none";
    document.getElementById("period-edit-id").value="";
    delete sectionLoaded["setup"]; loadSetup();
  } catch(e){ Toast.error(e.message); }
}

function editPeriod(id,name,start,end,session){
  document.getElementById("period-edit-id").value=id;
  document.getElementById("period-name").value=name;
  document.getElementById("period-start").value=start;
  document.getElementById("period-end").value=end;
  document.getElementById("period-session").value=session;
  document.getElementById("add-period-form").style.display="block";
}

async function deletePeriod(id){
  if(!confirm("Delete this period?")) return;
  try {
    await Api.delete("/admin/periods/"+id);
    Toast.success("Period deleted");
    delete sectionLoaded["setup"]; loadSetup();
  } catch(e){ Toast.error(e.message); }
}

'''

fa=fa.replace('async function savePeriod()', '// period already defined')
fa=fa.replace('async function loadLookupStudents()', period_js+'async function loadLookupStudents()')
print('Period JS functions added')

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','w',encoding='utf-8').write(fa)
print('Period management done!')
