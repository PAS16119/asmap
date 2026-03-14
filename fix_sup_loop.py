fs=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\routes\supervisor.py','r',encoding='utf-8').read()

old='''        q = MonitoringRecord.query.filter_by(teacher_id=t.id)
        records = q.all()'''

new='''        q = MonitoringRecord.query.filter_by(teacher_id=t.id)
        all_records = q.all()
        # Deduplicate: same teacher + date + period = one attendance
        seen = set()
        records = []
        for r in all_records:
            key = (r.teacher_id, str(r.attendance_date), r.period or str(r.id), r.session_type)
            if key not in seen:
                seen.add(key)
                records.append(r)'''

if old in fs:
    fs=fs.replace(old,new)
    print('Fixed!')
else:
    print('Not found')

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\routes\supervisor.py','w',encoding='utf-8').write(fs)
