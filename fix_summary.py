# Fix supervisor teacher-summary to deduplicate same teacher/date/period
fs=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\routes\supervisor.py','r',encoding='utf-8').read()

old_sup='''    teachers = Teacher.query.filter_by(is_active=True).all()
    result = []
    for t in teachers:
        records = MonitoringRecord.query.filter_by(teacher_id=t.id)
        if year_id:
            records = records.filter_by(academic_year_id=int(year_id))
        records = records.all()'''

new_sup='''    teachers = Teacher.query.filter_by(is_active=True).all()
    result = []
    for t in teachers:
        all_records = MonitoringRecord.query.filter_by(teacher_id=t.id)
        if year_id:
            all_records = all_records.filter_by(academic_year_id=int(year_id))
        all_records = all_records.all()
        # Deduplicate: same teacher + date + period = one attendance
        seen = set()
        records = []
        for r in all_records:
            key = (r.teacher_id, str(r.attendance_date), r.period or str(r.id), r.session_type)
            if key not in seen:
                seen.add(key)
                records.append(r)'''

if old_sup in fs:
    fs=fs.replace(old_sup, new_sup)
    print('Supervisor summary fixed')
else:
    print('Supervisor pattern not found - checking...')
    ts=fs.find('teacher-summary')
    print(fs[ts:ts+600])

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\routes\supervisor.py','w',encoding='utf-8').write(fs)
