from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, User, Teacher, Subject, Class, MonitoringRecord, SchoolSettings, AcademicYear
from datetime import date, datetime

supervisor_bp = Blueprint('supervisor', __name__)

# ── helper ──────────────────────────────────────────────────────────────────
def _require_monitor(claims):
    """Allow both supervisor and coordinator to record/view monitoring."""
    role = claims.get('role', '')
    if role not in ('supervisor', 'coordinator', 'admin'):
        return False
    return True


# ── POST /monitoring ─────────────────────────────────────────────────────────
@supervisor_bp.route('/monitoring', methods=['POST'])
@jwt_required()
def add_monitoring():
    claims = get_jwt()
    if not _require_monitor(claims):
        return jsonify({'error': 'Access denied'}), 403

    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    teacher_id       = data.get('teacher_id')
    subject_id       = data.get('subject_id')
    class_id         = data.get('class_id')
    attendance_date  = data.get('attendance_date')
    students_present = data.get('students_present', 0)
    session_type     = data.get('session_type', 'Normal')
    time_in          = data.get('time_in')        # "HH:MM"
    period           = data.get('period')          # e.g. "Period 1 (07:00–08:50)"
    notes            = data.get('notes', '')

    if not teacher_id or not attendance_date:
        return jsonify({'error': 'teacher_id and attendance_date are required'}), 400

    # Reject future dates
    try:
        rec_date = date.fromisoformat(attendance_date)
        if rec_date > date.today():
            return jsonify({'error': 'Cannot record monitoring for a future date'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid date format (use YYYY-MM-DD)'}), 400

    # Auto-compute is_on_time
    is_on_time = None
    if time_in:
        try:
            settings = SchoolSettings.query.first()
            if session_type == 'Normal':
                # For normal sessions, punctuality is based on period start if provided
                # otherwise use general normal_start from settings
                ref_time_str = None
                if period and '(' in period and '–' in period:
                    # Extract start time from "Period N (HH:MM–HH:MM)" format
                    try:
                        ref_time_str = period.split('(')[1].split('–')[0].strip()
                    except Exception:
                        ref_time_str = None
                if not ref_time_str and settings and settings.normal_start:
                    ref_time_str = settings.normal_start
                if ref_time_str:
                    ref_dt  = datetime.strptime(ref_time_str, '%H:%M')
                    in_dt   = datetime.strptime(time_in, '%H:%M')
                    is_on_time = (in_dt <= ref_dt)
            else:  # Extended
                if settings and settings.extended_start:
                    ref_dt  = datetime.strptime(settings.extended_start, '%H:%M')
                    in_dt   = datetime.strptime(time_in, '%H:%M')
                    is_on_time = (in_dt <= ref_dt)
        except Exception:
            is_on_time = None

    record = MonitoringRecord(
        recorded_by     = user_id,
        teacher_id      = teacher_id,
        subject_id      = subject_id or None,
        class_id        = class_id or None,
        attendance_date = rec_date,
        students_present= int(students_present),
        session_type    = session_type,
        time_in         = time_in,
        period          = period,
        is_on_time      = is_on_time,
        notes           = notes,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'message': 'Monitoring record saved', 'record': record.to_dict()}), 201


# ── GET /monitoring ──────────────────────────────────────────────────────────
@supervisor_bp.route('/monitoring', methods=['GET'])
@jwt_required()
def get_monitoring():
    claims = get_jwt()
    if not _require_monitor(claims):
        return jsonify({'error': 'Access denied'}), 403

    user_id      = get_jwt_identity()
    role         = claims.get('role', '')
    date_from    = request.args.get('date_from')
    date_to      = request.args.get('date_to')
    session_type = request.args.get('session_type')

    q = MonitoringRecord.query

    # Non-admins only see their own records
    if role not in ('admin',):
        q = q.filter_by(recorded_by=user_id)

    if date_from:
        try:
            q = q.filter(MonitoringRecord.attendance_date >= date.fromisoformat(date_from))
        except ValueError:
            pass
    if date_to:
        try:
            q = q.filter(MonitoringRecord.attendance_date <= date.fromisoformat(date_to))
        except ValueError:
            pass
    if session_type:
        q = q.filter_by(session_type=session_type)

    records = q.order_by(MonitoringRecord.attendance_date.desc()).all()
    return jsonify({'records': [r.to_dict() for r in records]})


# ── PUT /monitoring/<id> ─────────────────────────────────────────────────────
@supervisor_bp.route('/monitoring/<int:record_id>', methods=['PUT'])
@jwt_required()
def update_monitoring(record_id):
    claims  = get_jwt()
    if not _require_monitor(claims):
        return jsonify({'error': 'Access denied'}), 403

    user_id = get_jwt_identity()
    role    = claims.get('role', '')
    record  = MonitoringRecord.query.get_or_404(record_id)

    # Only the recorder (or admin) may edit
    if role != 'admin' and str(record.recorded_by) != str(user_id):
        return jsonify({'error': 'You can only edit your own records'}), 403

    data = request.get_json(silent=True) or {}
    for field in ['teacher_id', 'subject_id', 'class_id', 'students_present',
                  'session_type', 'time_in', 'period', 'notes']:
        if field in data:
            setattr(record, field, data[field])

    if 'attendance_date' in data:
        try:
            record.attendance_date = date.fromisoformat(data['attendance_date'])
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400

    # Recompute punctuality
    if record.time_in:
        try:
            settings = SchoolSettings.query.first()
            if record.session_type == 'Normal':
                ref_time_str = None
                if record.period and '(' in record.period and '–' in record.period:
                    try:
                        ref_time_str = record.period.split('(')[1].split('–')[0].strip()
                    except Exception:
                        ref_time_str = None
                if not ref_time_str and settings and settings.normal_start:
                    ref_time_str = settings.normal_start
                if ref_time_str:
                    ref_dt = datetime.strptime(ref_time_str, '%H:%M')
                    in_dt  = datetime.strptime(record.time_in, '%H:%M')
                    record.is_on_time = (in_dt <= ref_dt)
            else:
                if settings and settings.extended_start:
                    ref_dt = datetime.strptime(settings.extended_start, '%H:%M')
                    in_dt  = datetime.strptime(record.time_in, '%H:%M')
                    record.is_on_time = (in_dt <= ref_dt)
        except Exception:
            record.is_on_time = None

    db.session.commit()
    return jsonify({'message': 'Record updated', 'record': record.to_dict()})


# ── DELETE /monitoring/<id> ──────────────────────────────────────────────────
@supervisor_bp.route('/monitoring/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_monitoring(record_id):
    claims  = get_jwt()
    if not _require_monitor(claims):
        return jsonify({'error': 'Access denied'}), 403

    user_id = get_jwt_identity()
    role    = claims.get('role', '')
    record  = MonitoringRecord.query.get_or_404(record_id)

    if role != 'admin' and str(record.recorded_by) != str(user_id):
        return jsonify({'error': 'You can only delete your own records'}), 403

    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': 'Record deleted'})


# ── GET /teacher-summary ─────────────────────────────────────────────────────
@supervisor_bp.route('/teacher-summary', methods=['GET'])
@jwt_required()
def teacher_summary():
    claims = get_jwt()
    if not _require_monitor(claims):
        return jsonify({'error': 'Access denied'}), 403

    year_id = request.args.get('year_id')

    # Fetch active year if not provided
    if not year_id:
        active = AcademicYear.query.filter_by(is_active=True).first()
        year_id = active.id if active else None

    teachers = Teacher.query.filter_by(is_active=True).all()
    result = []
    for t in teachers:
        q = MonitoringRecord.query.filter_by(teacher_id=t.id)
        all_records = q.all()
        # Deduplicate: same teacher + date + period = one attendance
        seen = set()
        records = []
        for r in all_records:
            key = (r.teacher_id, str(r.attendance_date), r.period or str(r.id), r.session_type)
            if key not in seen:
                seen.add(key)
                records.append(r)

        normal_total    = sum(1 for r in records if r.session_type == 'Normal')
        normal_ontime   = sum(1 for r in records if r.session_type == 'Normal' and r.is_on_time is True)
        normal_late     = sum(1 for r in records if r.session_type == 'Normal' and r.is_on_time is False)
        extended_total  = sum(1 for r in records if r.session_type == 'Extended')
        extended_ontime = sum(1 for r in records if r.session_type == 'Extended' and r.is_on_time is True)
        extended_late   = sum(1 for r in records if r.session_type == 'Extended' and r.is_on_time is False)

        result.append({
            'teacher_id':       t.id,
            'teacher_name':     t.full_name,
            'primary_subject':  t.subject.name if t.subject else '—',
            'normal_total':     normal_total,
            'normal_ontime':    normal_ontime,
            'normal_late':      normal_late,
            'extended_total':   extended_total,
            'extended_ontime':  extended_ontime,
            'extended_late':    extended_late,
            'grand_total':      normal_total + extended_total,
        })

    result.sort(key=lambda x: x['teacher_name'])
    return jsonify({'summary': result})
