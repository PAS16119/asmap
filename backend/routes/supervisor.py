from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from datetime import date as date_type
from models import db, MonitoringRecord, Teacher, AcademicYear
from sqlalchemy import func

supervisor_bp = Blueprint('supervisor', __name__)


def supervisor_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        role = get_jwt().get('role')
        if role not in ('admin', 'supervisor'):
            return jsonify({'error': 'Supervisor access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


def _active_year_id():
    y = AcademicYear.query.filter_by(is_active=True).first()
    return y.id if y else None


def _get_school_times():
    """Returns (normal_start, extended_start) as 'HH:MM' strings."""
    from models import SchoolSettings
    s = SchoolSettings.query.first()
    normal   = s.normal_start   if s and s.normal_start   else '07:30'
    extended = s.extended_start if s and s.extended_start else '15:30'
    return normal, extended


def _compute_on_time(time_in_str, session_type):
    """
    Returns True if teacher arrived on time, False if late, None if time_in not provided.
    On time = time_in <= configured start time for that session type.
    """
    if not time_in_str:
        return None
    try:
        from datetime import datetime as dt
        normal_start, extended_start = _get_school_times()
        cutoff_str = extended_start if session_type == 'Extended' else normal_start
        teacher_t = dt.strptime(time_in_str.strip(), '%H:%M')
        cutoff_t  = dt.strptime(cutoff_str, '%H:%M')
        return teacher_t <= cutoff_t
    except ValueError:
        return None


# ── Record monitoring ──────────────────────────────────────────────────────────
@supervisor_bp.route('/monitoring', methods=['POST'])
@supervisor_required
def record_monitoring():
    data = request.get_json(silent=True) or {}
    uid  = get_jwt_identity()

    required = ['teacher_id', 'subject_id', 'class_id', 'attendance_date', 'students_present']
    for f in required:
        if data.get(f) is None or data.get(f) == '':
            return jsonify({'error': f'{f} is required'}), 400

    # Validate date
    try:
        att_date = date_type.fromisoformat(data['attendance_date'])
        if att_date > date_type.today():
            return jsonify({'error': 'Cannot record monitoring for a future date'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Validate students_present
    try:
        students_present = int(data['students_present'])
        if students_present < 0:
            return jsonify({'error': 'Students present cannot be negative'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'students_present must be a number'}), 400

    session_type = data.get('session_type', 'Normal')
    if session_type not in ('Normal', 'Extended'):
        return jsonify({'error': 'session_type must be Normal or Extended'}), 400

    time_in   = (data.get('time_in') or '').strip() or None
    is_on_time = _compute_on_time(time_in, session_type)

    year_id = data.get('academic_year_id') or _active_year_id()

    rec = MonitoringRecord(
        teacher_id=int(data['teacher_id']),
        subject_id=int(data['subject_id']),
        class_id=int(data['class_id']),
        academic_year_id=year_id,
        students_present=students_present,
        recorded_by_user_id=uid,
        attendance_date=att_date,
        period=data.get('period') or None,
        session_type=session_type,
        time_in=time_in,
        is_on_time=is_on_time,
        notes=(data.get('notes') or '').strip() or None
    )
    db.session.add(rec)
    db.session.commit()
    return jsonify(rec.to_dict()), 201


# ── List my monitoring records ─────────────────────────────────────────────────
@supervisor_bp.route('/monitoring', methods=['GET'])
@supervisor_required
def list_monitoring():
    uid        = get_jwt_identity()
    year_id    = request.args.get('year_id') or _active_year_id()
    date_from  = request.args.get('date_from')
    date_to    = request.args.get('date_to')
    session_t  = request.args.get('session_type')

    q = MonitoringRecord.query.filter_by(recorded_by_user_id=uid)
    if year_id:   q = q.filter_by(academic_year_id=int(year_id))
    if session_t: q = q.filter_by(session_type=session_t)
    if date_from: q = q.filter(MonitoringRecord.attendance_date >= date_from)
    if date_to:   q = q.filter(MonitoringRecord.attendance_date <= date_to)

    return jsonify([r.to_dict() for r in q.order_by(MonitoringRecord.attendance_date.desc()).all()])


# ── Update a monitoring record ─────────────────────────────────────────────────
@supervisor_bp.route('/monitoring/<int:rid>', methods=['PUT'])
@supervisor_required
def update_monitoring(rid):
    rec = MonitoringRecord.query.get_or_404(rid)
    uid = get_jwt_identity()

    # Only recorder or admin can edit
    if get_jwt().get('role') != 'admin' and str(rec.recorded_by_user_id) != str(uid):
        return jsonify({'error': 'You can only edit your own records'}), 403

    data = request.get_json(silent=True) or {}
    if 'students_present' in data:
        try:
            rec.students_present = int(data['students_present'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid students_present'}), 400
    if 'notes'   in data: rec.notes   = data['notes'] or None
    if 'period'  in data: rec.period  = data['period'] or None
    if 'time_in' in data:
        rec.time_in    = data['time_in'] or None
        rec.is_on_time = _compute_on_time(rec.time_in, rec.session_type)

    db.session.commit()
    return jsonify(rec.to_dict())


# ── Delete a monitoring record ─────────────────────────────────────────────────
@supervisor_bp.route('/monitoring/<int:rid>', methods=['DELETE'])
@supervisor_required
def delete_monitoring(rid):
    rec = MonitoringRecord.query.get_or_404(rid)
    uid = get_jwt_identity()
    if get_jwt().get('role') != 'admin' and str(rec.recorded_by_user_id) != str(uid):
        return jsonify({'error': 'You can only delete your own records'}), 403
    db.session.delete(rec)
    db.session.commit()
    return jsonify({'message': 'Record deleted'})


# ── Teacher summary (my records) ───────────────────────────────────────────────
@supervisor_bp.route('/teacher-summary', methods=['GET'])
@supervisor_required
def teacher_summary():
    uid     = get_jwt_identity()
    year_id = request.args.get('year_id') or _active_year_id()

    q = (db.session.query(
            Teacher.id, Teacher.teacher_name, Teacher.subject,
            MonitoringRecord.session_type,
            func.count(MonitoringRecord.id).label('sessions'),
            func.sum(MonitoringRecord.students_present).label('total_students'),
            func.sum(
                db.case((MonitoringRecord.is_on_time == True, 1), else_=0)
            ).label('on_time'),
            func.sum(
                db.case((MonitoringRecord.is_on_time == False, 1), else_=0)
            ).label('late')
         )
         .join(MonitoringRecord, MonitoringRecord.teacher_id == Teacher.id)
         .filter(MonitoringRecord.recorded_by_user_id == uid))

    if year_id:
        q = q.filter(MonitoringRecord.academic_year_id == int(year_id))

    rows = q.group_by(Teacher.id, Teacher.teacher_name, Teacher.subject,
                      MonitoringRecord.session_type).all()

    # Pivot: one dict per teacher, with normal + extended sub-keys
    teachers = {}
    for r in rows:
        if r.id not in teachers:
            teachers[r.id] = {
                'teacher_id':   r.id,
                'teacher_name': r.teacher_name,
                'subject':      r.subject or '',
                'normal':   {'sessions': 0, 'on_time': 0, 'late': 0, 'total_students': 0},
                'extended': {'sessions': 0, 'on_time': 0, 'late': 0, 'total_students': 0},
            }
        bucket = 'extended' if r.session_type == 'Extended' else 'normal'
        teachers[r.id][bucket] = {
            'sessions':       r.sessions,
            'on_time':        int(r.on_time or 0),
            'late':           int(r.late or 0),
            'total_students': int(r.total_students or 0),
        }

    result = sorted(teachers.values(), key=lambda x: -(x['normal']['sessions'] + x['extended']['sessions']))
    return jsonify(result)
