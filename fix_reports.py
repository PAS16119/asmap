fa=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','r',encoding='utf-8').read()

# 1. Make By Class rows clickable - show payments for that class
old_class = '''document.getElementById("report-by-class").innerHTML = data.by_class.length
      ? data.by_class.map(r=><div class="report-row"><div style="flex:1"><div style="display:flex;justify-content:space-between"><span style="font-weight:500"></span><div style="text-align:right"><div class="amount" style="font-size:.92rem"></div><div style="font-size:.7rem;color:var(--text-3)"> tx</div></div></div><div class="bar-track"><div class="bar-fill" style="width:%"></div></div></div></div>).join("") : UI.empty("No data");'''

new_class = '''document.getElementById("report-by-class").innerHTML = data.by_class.length
      ? data.by_class.map(r=><div class="report-row" style="cursor:pointer" onclick="expandReport('class','',)"><div style="flex:1"><div style="display:flex;justify-content:space-between"><span style="font-weight:500"></span><div style="text-align:right"><div class="amount" style="font-size:.92rem"></div><div style="font-size:.7rem;color:var(--text-3)"> tx · click to expand</div></div></div><div class="bar-track"><div class="bar-fill" style="width:%"></div></div></div><div id="expand-class-" style="display:none;margin-top:8px"></div></div>).join("") : UI.empty("No data");'''

# 2. Make By Purpose rows clickable
old_purpose = '''document.getElementById("report-by-purpose").innerHTML = data.by_purpose.length
      ? data.by_purpose.map(r=><div class="report-row"><div style="flex:1"><div style="display:flex;justify-content:space-between"><span></span><div style="text-align:right"><div class="amount" style="font-size:.92rem"></div><div style="font-size:.7rem;color:var(--text-3)"> tx</div></div></div><div class="bar-track"><div class="bar-fill" style="width:%"></div></div></div></div>).join("") : UI.empty("No data");'''

new_purpose = '''document.getElementById("report-by-purpose").innerHTML = data.by_purpose.length
      ? data.by_purpose.map(r=><div class="report-row" style="cursor:pointer" onclick="expandReport('purpose','',0)"><div style="flex:1"><div style="display:flex;justify-content:space-between"><span></span><div style="text-align:right"><div class="amount" style="font-size:.92rem"></div><div style="font-size:.7rem;color:var(--text-3)"> tx · click to expand</div></div></div><div class="bar-track"><div class="bar-fill" style="width:%"></div></div></div><div id="expand-purpose-" style="display:none;margin-top:8px"></div></div>).join("") : UI.empty("No data");'''

if old_class in fa:
    fa=fa.replace(old_class, new_class)
    print('By Class clickable - done')
else:
    print('By Class pattern not found')

if old_purpose in fa:
    fa=fa.replace(old_purpose, new_purpose)
    print('By Purpose clickable - done')
else:
    print('By Purpose pattern not found')

# 3. Add expandReport function before loadLookupStudents
expand_fn = '''
async function expandReport(type, value, id) {
  const yp = activeYear ? "?year_id=" + activeYear.id : "";
  const elId = type==='class' ? "expand-class-"+(id||value) : "expand-purpose-"+value.replace(/\s/g,'-');
  const el = document.getElementById(elId);
  if (!el) return;
  if (el.style.display !== 'none') { el.style.display='none'; return; }
  el.style.display='block';
  el.innerHTML = '<div style="color:var(--text-3);font-size:.8rem;padding:8px">Loading...</div>';
  try {
    const param = type==='class' ? "&class_id="+id : "&purpose="+encodeURIComponent(value);
    const data = await Api.get("/admin/payments"+yp+(yp?"&":"?")+param.slice(1));
    const payments = data.payments || data;
    if(!payments.length){ el.innerHTML='<div style="color:var(--text-3);font-size:.8rem;padding:8px">No records</div>'; return; }
    el.innerHTML = '<table class="table" style="font-size:.8rem;margin-top:4px"><thead><tr><th>Student</th><th>Purpose</th><th>Amount</th><th>Date</th><th>Status</th></tr></thead><tbody>'+
      payments.map(p=><tr><td></td><td></td><td class="amount"></td><td style="color:var(--text-3)"></td><td></td></tr>).join('')+
      '</tbody></table>';
  } catch(e) { el.innerHTML='<div style="color:red;font-size:.8rem;padding:8px">Error: '+e.message+'</div>'; }
}

'''

fa=fa.replace('async function loadLookupStudents()', expand_fn+'async function loadLookupStudents()')
print('expandReport function added')

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','w',encoding='utf-8').write(fa)
print('Reports fix done!')
