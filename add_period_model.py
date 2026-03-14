f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\models.py','r',encoding='utf-8').read()

# Add Period model before MonitoringRecord
period_model = '''
class Period(db.Model):
    __tablename__ = 'periods'
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(50), nullable=False)   # e.g. "Period 1"
    start_time   = db.Column(db.String(10), nullable=True)    # e.g. "07:00"
    end_time     = db.Column(db.String(10), nullable=True)    # e.g. "08:50"
    session_type = db.Column(db.String(20), default='Normal') # Normal | Extended Teaching
    is_active    = db.Column(db.Boolean, default=True)
    order_num    = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'session_type': self.session_type,
            'is_active': self.is_active,
            'order_num': self.order_num,
            'label': f"{self.name} ({self.start_time}-{self.end_time})" if self.start_time else self.name
        }

'''

f=f.replace('class MonitoringRecord(db.Model):', period_model+'class MonitoringRecord(db.Model):')
open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\models.py','w',encoding='utf-8').write(f)
print('Done!')
