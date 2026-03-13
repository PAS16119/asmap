from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()


# ─── SCHOOL SETTINGS ─────────────────────────────────────────────────────────
class SchoolSettings(db.Model):
    __tablename__ = 'school_settings'
    id             = db.Column(db.Integer, primary_key=True)
    school_name    = db.Column(db.String(200), default='Your School')
    school_short   = db.Column(db.String(80), nullable=True)
    school_motto   = db.Column(db.String(200), nullable=True)
    school_logo    = db.Column(db.Text, nullable=True)   # base64 data-URL
    normal_start   = db.Column(db.String(5), default='07:30')   # HH:MM
    extended_start = db.Column(db.String(5), default='15:30')   # HH:MM
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':             self.id,
            'school_name':    self.school_name,
            'school_short':   self.school_short or '',
            'school_motto':   self.school_motto or '',
            'school_logo':    self.school_logo or '',
            'normal_start':   self.normal_start or '07:30',
            'extended_start': self.extended_start or '15:30',
        }

    def to_public_dict(self):
        """No logo – used by unauthenticated login page."""
        return {
            'school_name':  self.school_name,
            'school_short': self.school_short or '',
            'school_motto': self.school_motto or '',
            'school_logo':  self.school_logo or '',
        }


# ─── ACADEMIC YEAR ───────────────────────────────────────────────────────────
class AcademicYear(db.Model):
    __tablename__ = 'academic_years'
    id         = db.Column(db.Integer, primary_key=True)
    label      = db.Column(db.String(20), nullable=False, unique=True)
    is_active  = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {
            'id':         self.id,
            'label':      self.label,
            'is_active':  self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ─── USER ─────────────────────────────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20), nullable=False)  # admin|coordinator|supervisor
    full_name     = db.Column(db.String(120), nullable=True)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    created_by    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def to_dict(self):
        return {
            'id':         self.id,
            'username':   self.username,
            'email':      self.email,
            'role':       self.role,
            'full_name':  self.full_name,
            'is_active':  self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ─── TEACHER ──────────────────────────────────────────────────────────────────
class Teacher(db.Model):
    __tablename__ = 'teachers'
    id           = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(120), nullable=False)
    subject      = db.Column(db.String(100), nullable=True)
    is_active    = db.Column(db.Boolean, default=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    created_by   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {
            'id':           self.id,
            'teacher_name': self.teacher_name,
            'subject':      self.subject or '',
            'is_active':    self.is_active,
            'created_at':   self.created_at.isoformat() if self.created_at else None,
        }


# ─── SUBJECT ──────────────────────────────────────────────────────────────────
class Subject(db.Model):
    __tablename__ = 'subjects'
    id           = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(120), nullable=False, unique=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    created_by   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {'id': self.id, 'subject_name': self.subject_name}


# ─── CLASS ────────────────────────────────────────────────────────────────────
class Class(db.Model):
    __tablename__ = 'classes'
    id         = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(80), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {'id': self.id, 'class_name': self.class_name}


# ─── STUDENT ──────────────────────────────────────────────────────────────────
class Student(db.Model):
    __tablename__ = 'students'
    id               = db.Column(db.Integer, primary_key=True)
    student_name     = db.Column(db.String(120), nullable=False)
    class_id         = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=True)
    is_active        = db.Column(db.Boolean, default=True)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    created_by       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    class_        = db.relationship('Class', backref='students')
    academic_year = db.relationship('AcademicYear', backref='students')

    def to_dict(self):
        return {
            'id':               self.id,
            'student_name':     self.student_name,
            'class_id':         self.class_id,
            'class_name':       self.class_.class_name if self.class_ else None,
            'academic_year_id': self.academic_year_id,
            'academic_year':    self.academic_year.label if self.academic_year else None,
            'is_active':        self.is_active,
        }


# ─── COORDINATOR CLASS ASSIGNMENT ─────────────────────────────────────────────
class CoordinatorClassAssignment(db.Model):
    __tablename__ = 'coordinator_class_assignments'
    id             = db.Column(db.Integer, primary_key=True)
    coordinator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id       = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    coordinator = db.relationship('User', backref='class_assignments')
    class_      = db.relationship('Class')

    def to_dict(self):
        return {
            'id':               self.id,
            'coordinator_id':   self.coordinator_id,
            'coordinator_name': (self.coordinator.full_name or self.coordinator.username) if self.coordinator else None,
            'class_id':         self.class_id,
            'class_name':       self.class_.class_name if self.class_ else None,
        }


# ─── PAYMENT ──────────────────────────────────────────────────────────────────
class Payment(db.Model):
    __tablename__ = 'payments'
    id                   = db.Column(db.Integer, primary_key=True)
    student_id           = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    academic_year_id     = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=True)
    amount               = db.Column(db.Numeric(12, 2), nullable=False)
    purpose              = db.Column(db.String(200), nullable=False)
    collected_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    confirmed_by_admin_id= db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_confirmed         = db.Column(db.Boolean, default=False)
    notes                = db.Column(db.Text, nullable=True)
    created_at           = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at           = db.Column(db.DateTime, onupdate=datetime.utcnow)

    student       = db.relationship('Student', backref='payments')
    collector     = db.relationship('User', foreign_keys=[collected_by_user_id])
    confirmer     = db.relationship('User', foreign_keys=[confirmed_by_admin_id])
    academic_year = db.relationship('AcademicYear', backref='payments')

    def to_dict(self):
        return {
            'id':                 self.id,
            'student_id':         self.student_id,
            'student_name':       self.student.student_name if self.student else None,
            'class_id':           self.student.class_id if self.student else None,
            'class_name':         (self.student.class_.class_name if self.student and self.student.class_ else None),
            'academic_year_id':   self.academic_year_id,
            'academic_year':      self.academic_year.label if self.academic_year else None,
            'amount':             float(self.amount),
            'purpose':            self.purpose,
            'collected_by_user_id': self.collected_by_user_id,
            'collector_name':     ((self.collector.full_name or self.collector.username) if self.collector else None),
            'is_confirmed':       self.is_confirmed,
            'confirmed_by':       (self.confirmer.full_name or self.confirmer.username) if self.confirmer else None,
            'notes':              self.notes,
            'created_at':         self.created_at.isoformat() if self.created_at else None,
            'updated_at':         self.updated_at.isoformat() if self.updated_at else None,
        }


# ─── MONITORING RECORD ────────────────────────────────────────────────────────
class MonitoringRecord(db.Model):
    __tablename__ = 'monitoring_records'
    id                  = db.Column(db.Integer, primary_key=True)
    teacher_id          = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    subject_id          = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    class_id            = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    academic_year_id    = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=True)
    students_present    = db.Column(db.Integer, nullable=False)
    recorded_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attendance_date     = db.Column(db.Date, nullable=False)
    period              = db.Column(db.String(10), nullable=True)
    session_type        = db.Column(db.String(20), default='Normal')   # Normal | Extended
    time_in             = db.Column(db.String(5), nullable=True)        # HH:MM
    is_on_time          = db.Column(db.Boolean, nullable=True)          # null = not marked
    notes               = db.Column(db.Text, nullable=True)
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)

    teacher       = db.relationship('Teacher', backref='monitoring_records')
    subject       = db.relationship('Subject')
    class_        = db.relationship('Class')
    recorder      = db.relationship('User')
    academic_year = db.relationship('AcademicYear', backref='monitoring_records')

    def to_dict(self):
        return {
            'id':               self.id,
            'teacher_id':       self.teacher_id,
            'teacher_name':     self.teacher.teacher_name if self.teacher else None,
            'subject_id':       self.subject_id,
            'subject_name':     self.subject.subject_name if self.subject else None,
            'class_id':         self.class_id,
            'class_name':       self.class_.class_name if self.class_ else None,
            'academic_year_id': self.academic_year_id,
            'academic_year':    self.academic_year.label if self.academic_year else None,
            'students_present': self.students_present,
            'recorded_by':      ((self.recorder.full_name or self.recorder.username) if self.recorder else None),
            'attendance_date':  self.attendance_date.isoformat() if self.attendance_date else None,
            'period':           self.period,
            'session_type':     self.session_type or 'Normal',
            'time_in':          self.time_in,
            'is_on_time':       self.is_on_time,
            'notes':            self.notes,
            'created_at':       self.created_at.isoformat() if self.created_at else None,
        }
