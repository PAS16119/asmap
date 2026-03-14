f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\app.py','r',encoding='utf-8').read()

migration_code = '''
        # Create periods table and seed defaults
        db.session.execute(db.text("""
            CREATE TABLE IF NOT EXISTS periods (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                start_time VARCHAR(10),
                end_time VARCHAR(10),
                session_type VARCHAR(20) DEFAULT 'Normal',
                is_active BOOLEAN DEFAULT TRUE,
                order_num INTEGER DEFAULT 0
            )
        """))
        db.session.commit()
        from models import Period
        if Period.query.count() == 0:
            defaults = [
                Period(name="Period 1", start_time="07:00", end_time="08:50", session_type="Normal", order_num=1),
                Period(name="Period 2", start_time="09:00", end_time="09:50", session_type="Normal", order_num=2),
                Period(name="Period 3", start_time="09:50", end_time="10:40", session_type="Normal", order_num=3),
                Period(name="Period 4", start_time="10:40", end_time="11:30", session_type="Normal", order_num=4),
                Period(name="Period 5", start_time="11:30", end_time="12:20", session_type="Normal", order_num=5),
                Period(name="Period 6", start_time="12:20", end_time="13:10", session_type="Normal", order_num=6),
                Period(name="Period 7", start_time="13:10", end_time="14:00", session_type="Normal", order_num=7),
                Period(name="Extended Teaching", start_time=None, end_time=None, session_type="Extended Teaching", order_num=8),
            ]
            db.session.add_all(defaults)
            db.session.commit()
            print("Seeded default periods")
'''

# Insert before the closing of migrate_v11
f=f.replace(
    "        print('migrate-v11 complete')",
    migration_code + "        print('migrate-v11 complete')"
)
open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\app.py','w',encoding='utf-8').write(f)
print('Done!')
