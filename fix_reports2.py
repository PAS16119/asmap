# -*- coding: utf-8 -*-
fa=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','r',encoding='utf-8').read()

old_class = 'document.getElementById("report-by-class").innerHTML = data.by_class.length\n      ? data.by_class.map(r=>`<div class="report-row"><div style="flex:1"><div style="display:flex;justify-content:space-between"><span style="font-weight:500">${r.class_name}</span><div style="text-align:right"><div class="amount" style="font-size:.92rem">${UI.currency(r.total)}</div><div style="font-size:.7rem;color:var(--text-3)">${r.count} tx</div></div></div><div class="bar-track"><div class="bar-fill" style="width:${(r.total/maxC*100).toFixed(1)}%"></div></div></div></div>`).join("") : UI.empty("No data");'

new_class = 'document.getElementById("report-by-class").innerHTML = data.by_class.length\n      ? data.by_class.map(r=>`<div class="report-row" style="cursor:pointer" onclick="expandReport(\'class\',\'${r.class_name}\',${r.class_id||0})"><div style="flex:1"><div style="display:flex;justify-content:space-between"><span style="font-weight:500">${r.class_name}</span><div style="text-align:right"><div class="amount" style="font-size:.92rem">${UI.currency(r.total)}</div><div style="font-size:.7rem;color:var(--text-3)">${r.count} tx (click)</div></div></div><div class="bar-track"><div class="bar-fill" style="width:${(r.total/maxC*100).toFixed(1)}%"></div></div></div><div id="expand-class-${r.class_id||0}" style="display:none;margin-top:8px"></div></div>`).join("") : UI.empty("No data");'

old_purpose = 'document.getElementById("report-by-purpose").innerHTML = data.by_purpose.length\n      ? data.by_purpose.map(r=>`<div class="report-row"><div style="flex:1"><div style="display:flex;justify-content:space-between"><span>${r.purpose}</span><div style="text-align:right"><div class="amount" style="font-size:.92rem">${UI.currency(r.total)}</div><div style="font-size:.7rem;color:var(--text-3)">${r.count} tx</div></div></div><div class="bar-track"><div class="bar-fill" style="width:${(r.total/maxP*100).toFixed(1)}%"></div></div></div></div>`).join("") : UI.empty("No data");'

new_purpose = 'document.getElementById("report-by-purpose").innerHTML = data.by_purpose.length\n      ? data.by_purpose.map(r=>`<div class="report-row" style="cursor:pointer" onclick="expandReport(\'purpose\',\'${r.purpose}\',0)"><div style="flex:1"><div style="display:flex;justify-content:space-between"><span>${r.purpose}</span><div style="text-align:right"><div class="amount" style="font-size:.92rem">${UI.currency(r.total)}</div><div style="font-size:.7rem;color:var(--text-3)">${r.count} tx (click)</div></div></div><div class="bar-track"><div class="bar-fill" style="width:${(r.total/maxP*100).toFixed(1)}%"></div></div></div><div id="expand-purpose-${r.purpose.replace(/ /g,\'-\')}" style="display:none;margin-top:8px"></div></div>`).join("") : UI.empty("No data");'

if old_class in fa:
    fa=fa.replace(old_class,new_class)
    print('By Class clickable - done')
else:
    print('By Class not found')

if old_purpose in fa:
    fa=fa.replace(old_purpose,new_purpose)
    print('By Purpose clickable - done')
else:
    print('By Purpose not found')

expand_fn = '''
async function expandReport(type, value, id) {
  const yp = activeYear ? "?year_id=" + activeYear.id : "";
  const elId = type==="class" ? "expand-class-"+id : "expand-purpose-"+value.replace(/ /g,"-");
  const el = document.getElementById(elId);
  if (!el) return;
  if (el.style.display !== "none") { el.style.display="none"; return; }
  el.style.display="block";
  el.innerHTML = "<div style=\'color:var(--text-3);font-size:.8rem;padding:8px\'>Loading...</div>";
  try {
    let url = "/admin/payments" + (yp||"?");
    if(type==="class") url += (yp?"&":"?") + "class_id="+id;
    else url += (yp?"&":"?") + "purpose="+encodeURIComponent(value);
    const data = await Api.get(url);
    const payments = data.payments || data;
    if(!payments.length){ el.innerHTML="<div style=\'color:var(--text-3);font-size:.8rem;padding:8px\'>No records found</div>"; return; }
    el.innerHTML = "<table class=\'table\' style=\'font-size:.8rem;margin-top:4px\'><thead><tr><th>Student</th><th>Purpose</th><th>Amount</th><th>Date</th><th>Status</th></tr></thead><tbody>"+
      payments.map(p=>`<tr><td>${p.student_name}</td><td>${p.purpose}</td><td class="amount">${UI.currency(p.amount)}</td><td style="color:var(--text-3)">${UI.date(p.created_at)}</td><td>${UI.badge(p.is_confirmed?"Confirmed":"Pending",p.is_confirmed?"green":"warning")}</td></tr>`).join("")+
      "</tbody></table>";
  } catch(e) { el.innerHTML="<div style=\'color:red;font-size:.8rem;padding:8px\'>Error: "+e.message+"</div>"; }
}

'''

fa=fa.replace('async function loadLookupStudents()', expand_fn+'async function loadLookupStudents()')
print('expandReport function added')

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','w',encoding='utf-8').write(fa)
print('All reports fixes done!')
