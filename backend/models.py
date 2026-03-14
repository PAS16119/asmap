from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import bcrypt

db = SQLAlchemy()

# ── Many-to-many: Teacher ↔ Subject ─────────────────────────────────────────
teacher_subjects = db.Table(
    'teacher_subjects',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id'), primary_key=True),
)

# ── SchoolSettings ────────────────────────────────────────────────────────────
class SchoolSettings(db.Model):
    __tablename__ = 'school_settings'
    id             = db.Column(db.Integer, primary_key=True)
    school_name    = db.Column(db.String(200), default='My School')
    school_short   = db.Column(db.String(50),  default='SCH')
    school_motto   = db.Column(db.String(300),  default='')
    school_logo    = db.Column(db.Text, nullable=True)      # base64
    normal_start   = db.Column(db.String(10),  default='07:00')
    extended_start = db.Column(db.String(10),  default='15:30')

    def to_dict(self):
        return {
            'id':             self.id,
            'school_name':    self.school_name,
            'school_short':   self.school_short,
            'school_motto':   self.school_motto,
            'has_logo':       bool(self.school_logo),
            'school_logo':    self.school_logo,
            'normal_start':   self.normal_start,
            'extended_start': self.extended_start,
        }


# ── AcademicYear ──────────────────────────────────────────────────────────────
class AcademicYear(db.Model):
    __tablename__ = 'academic_years'
    id         = db.Column(db.Integer, primary_key=True)
    label      = db.Column(db.String(20), unique=True, nullable=False)  # e.g. "2024/2025"
    is_active  = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'label': self.label, 'is_active': self.is_active}


# ── User ──────────────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80),  unique=True, nullable=False)
    email        = db.Column(db.String(120), unique=True, nullable=True)
    password_hash= db.Column(db.String(200), nullable=False)
    role         = db.Column(db.String(20),  nullable=False)   # admin|coordinator|supervisor
    full_name    = db.Column(db.String(150), nullable=True)
    is_active    = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw):
        self.password_hash = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()

    def check_password(self, raw):
        return bcrypt.checkpw(raw.encode(), self.password_hash.encode())

    def to_dict(self):
        return {
            'id': self.id, 'username': self.username, 'email': self.email,
            'role': self.role, 'full_name': self.full_name, 'is_active': self.is_active,
        }


# ── Teacher ───────────────────────────────────────────────────────────────────
class Teacher(db.Model):
    __tablename__ = 'teachers'
    id         = db.Column(db.Integer, primary_key=True)
    full_name  = db.Column(db.String(150), nullable=False)
    staff_id   = db.Column(db.String(50),  nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)  # primary/main subject
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subject  = db.relationship('Subject', backref='primary_teachers', foreign_keys=[subject_id])
    # Many-to-many: all subjects this teacher can teach
    subjects = db.relationship('Subject', secondary=teacher_subjects, backref='teachers',
                               lazy='select')

    def to_dict(self):
        return {
            'id':          self.id,
            'full_name':   self.full_name,
            'staff_id':    self.staff_id,
            'subject_id':  self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'subjects':    [{'id': s.id, 'name': s.name} for s in self.subjects],
            'is_active':   self.is_active,
        }


# ── Subject ───────────────────────────────────────────────────────────────────
class Subject(db.Model):
    __tablename__ = 'subjects'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


# ── Class ─────────────────────────────────────────────────────────────────────
class Class(db.Model):
    __tablename__ = 'classes'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(50), nullable=False)
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        student_count = Student.query.filter_by(class_id=self.id).count()
        return {'id': self.id, 'name': self.name, 'is_active': self.is_active,
                'student_count': student_count}


# ── Student ───────────────────────────────────────────────────────────────────
class Student(db.Model):
    __tablename__ = 'students'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(150), nullable=False)
    class_id   = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    year_id    = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=True)
    is_active  = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    school_class = db.relationship('Class', backref='students')
    year         = db.relationship('AcademicYear', backref='students')

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name,
            'class_id': self.class_id,
            'class_name': self.school_class.name if self.school_class else None,
            'year_id': self.year_id, 'is_active': self.is_active,
        }


# ── CoordinatorClassAssignment ────────────────────────────────────────────────
class CoordinatorClassAssignment(db.Model):
    __tablename__ = 'coordinator_class_assignments'
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)

    user         = db.relationship('User', backref='class_assignments')
    school_class = db.relationship('Class', backref='coordinators')

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id, 'class_id': self.class_id,
            'coordinator_name': self.user.full_name or self.user.username if self.user else None,
            'class_name': self.school_class.name if self.school_class else None,
        }


# ── Payment ───────────────────────────────────────────────────────────────────
class Payment(db.Model):
    __tablename__ = 'payments'
    id             = db.Column(db.Integer, primary_key=True)
    student_id     = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    recorded_by    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    amount         = db.Column(db.Float, nullable=False)
    purpose        = db.Column(db.String(100), default='Extended Teaching Fees')
    receipt_number = db.Column(db.String(50), unique=True, nullable=True)
    is_confirmed   = db.Column(db.Boolean, default=False)
    confirmed_by   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    confirmed_at   = db.Column(db.DateTime, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    student   = db.relationship('Student', backref='payments')
    recorder  = db.relationship('User', foreign_keys=[recorded_by], backref='recorded_payments')
    confirmer = db.relationship('User', foreign_keys=[confirmed_by], backref='confirmed_payments')

    def to_dict(self):
        return {
            'id': self.id, 'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'class_name': self.student.school_class.name if self.student and self.student.school_class else None,
            'amount': self.amount, 'purpose': self.purpose,
            'receipt_number': self.receipt_number,
            'is_confirmed': self.is_confirmed,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'recorded_by_name': self.recorder.full_name or self.recorder.username if self.recorder else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ── MonitoringRecord ──────────────────────────────────────────────────────────

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

class MonitoringRecord(db.Model):
    __tablename__ = 'monitoring_records'
    id               = db.Column(db.Integer, primary_key=True)
    recorded_by      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    teacher_id       = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id       = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    class_id         = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    attendance_date  = db.Column(db.Date, nullable=False)
    students_present = db.Column(db.Integer, default=0)
    session_type     = db.Column(db.String(20), default='Normal')  # Normal | Extended
    time_in          = db.Column(db.String(10), nullable=True)      # HH:MM
    period           = db.Column(db.String(60), nullable=True)      # e.g. "Period 3 (09:30–10:20)"
    is_on_time       = db.Column(db.Boolean, nullable=True)
    notes            = db.Column(db.Text, nullable=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    recorder = db.relationship('User', foreign_keys=[recorded_by], backref='monitoring_records')
    teacher  = db.relationship('Teacher', backref='monitoring_records')
    subject  = db.relationship('Subject', backref='monitoring_records')
    school_class = db.relationship('Class', backref='monitoring_records')

    def to_dict(self):
        return {
            'id': self.id,
            'recorded_by': self.recorded_by,
            'recorded_by_name': self.recorder.full_name or self.recorder.username if self.recorder else None,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.full_name if self.teacher else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'class_id': self.class_id,
            'class_name': self.school_class.name if self.school_class else None,
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'students_present': self.students_present,
            'session_type': self.session_type,
            'time_in': self.time_in,
            'period': self.period,
            'is_on_time': self.is_on_time,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
