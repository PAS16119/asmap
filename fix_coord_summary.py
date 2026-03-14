# Fix coordinator teacher-summary to deduplicate
fc=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\routes\coordinator.py','r',encoding='utf-8').read()

old_coord='''    for t in teachers:
        records = MonitoringRecord.query.filter_by(teacher_id=t.id).all()'''

new_coord='''    for t in teachers:
        all_records = MonitoringRecord.query.filter_by(teacher_id=t.id).all()
        # Deduplicate: same teacher + date + period = one attendance (even if recorded by both sup and coord)
        seen = set()
        records = []
        for r in all_records:
            key = (r.teacher_id, str(r.attendance_date), r.period or str(r.id), r.session_type)
            if key not in seen:
                seen.add(key)
                records.append(r)'''

if old_coord in fc:
    fc=fc.replace(old_coord, new_coord)
    print('Coordinator summary fixed')
else:
    print('Coordinator pattern not found')

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\routes\coordinator.py','w',encoding='utf-8').write(fc)
