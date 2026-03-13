from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, User, Student, Payment, CoordinatorClassAssignment, AcademicYear
from datetime import datetime
import uuid

coordinator_bp = Blueprint('coordinator', __name__)

# ── helpers ──────────────────────────────────────────────────────────────────
def _require_coordinator(claims):
    return claims.get('role') in ('coordinator', 'admin')

def _my_class_ids(user_id):
    assignments = CoordinatorClassAssignment.query.filter_by(user_id=user_id).all()
    return [a.class_id for a in assignments]


# ════════════════════════════════════════════════════════════════════════════
#  PAYMENT ROUTES (coordinator primary function)
# ════════════════════════════════════════════════════════════════════════════

@coordinator_bp.route('/classes', methods=['GET'])
@jwt_required()
def get_my_classes():
    claims  = get_jwt()
    if not _require_coordinator(claims):
        return jsonify({'error': 'Access denied'}), 403
    user_id = get_jwt_identity()
    assignments = CoordinatorClassAssignment.query.filter_by(user_id=user_id).all()
    classes = [{'id': a.school_class.id, 'name': a.school_class.name}
               for a in assignments if a.school_class]
    return jsonify({'classes': classes})


@coordinator_bp.route('/students/<int:class_id>', methods=['GET'])
@jwt_required()
def get_students(class_id):
    claims  = get_jwt()
    if not _require_coordinator(claims):
        return jsonify({'error': 'Access denied'}), 403
    user_id  = get_jwt_identity()
    role     = claims.get('role')

    if role != 'admin':
        my_ids = _my_class_ids(user_id)
        if class_id not in my_ids:
            return jsonify({'error': 'You are not assigned to this class'}), 403

    year_id = request.args.get('year_id')
    if not year_id:
        active = AcademicYear.query.filter_by(is_active=True).first()
        year_id = active.id if active else None

    q = Student.query.filter_by(class_id=class_id)
    if year_id:
        q = q.filter_by(year_id=year_id)
    students = q.order_by(Student.name).all()
    return jsonify({'students': [s.to_dict() for s in students]})


@coordinator_bp.route('/payments', methods=['POST'])
@jwt_required()
def record_payment():
    claims  = get_jwt()
    if not _require_coordinator(claims):
        return jsonify({'error': 'Access denied'}), 403
    user_id  = get_jwt_identity()
    role     = claims.get('role')
    data     = request.get_json(silent=True) or {}

    student_id = data.get('student_id')
    amount     = data.get('amount')
    purpose    = data.get('purpose', 'Extended Teaching Fees')

    if not student_id or not amount:
        return jsonify({'error': 'student_id and amount are required'}), 400

    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    if role != 'admin':
        my_ids = _my_class_ids(user_id)
        if student.class_id not in my_ids:
            return jsonify({'error': 'This student is not in your assigned class'}), 403

    receipt_number = f"RCP-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

    payment = Payment(
        student_id     = student_id,
        recorded_by    = user_id,
        amount         = float(amount),
        purpose        = purpose,
        receipt_number = receipt_number,
        is_confirmed   = False,
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({'message': 'Payment recorded', 'payment': payment.to_dict()}), 201


@coordinator_bp.route('/payments', methods=['GET'])
@jwt_required()
def get_payments():
    claims  = get_jwt()
    if not _require_coordinator(claims):
        return jsonify({'error': 'Access denied'}), 403
    user_id  = get_jwt_identity()
    role     = claims.get('role')
    class_id = request.args.get('class_id', type=int)

    year_id = request.args.get('year_id')
    if not year_id:
        active = AcademicYear.query.filter_by(is_active=True).first()
        year_id = active.id if active else None

    if role != 'admin':
        my_ids = _my_class_ids(user_id)
        if class_id and class_id not in my_ids:
            return jsonify({'error': 'Access denied to this class'}), 403

    q = Payment.query.join(Student)
    if role != 'admin':
        my_ids = _my_class_ids(user_id)
        q = q.filter(Student.class_id.in_(my_ids))
    elif class_id:
        q = q.filter(Student.class_id == class_id)

    if year_id:
        q = q.filter(Student.year_id == year_id)

    payments = q.order_by(Payment.created_at.desc()).all()
    return jsonify({'payments': [p.to_dict() for p in payments]})


@coordinator_bp.route('/payments/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_payments(student_id):
    claims  = get_jwt()
    if not _require_coordinator(claims):
        return jsonify({'error': 'Access denied'}), 403
    user_id = get_jwt_identity()
    role    = claims.get('role')

    student = Student.query.get_or_404(student_id)
    if role != 'admin':
        my_ids = _my_class_ids(user_id)
        if student.class_id not in my_ids:
            return jsonify({'error': 'Access denied'}), 403

    year_id = request.args.get('year_id')
    if not year_id:
        active = AcademicYear.query.filter_by(is_active=True).first()
        year_id = active.id if active else None

    q = Payment.query.filter_by(student_id=student_id)
    payments = q.order_by(Payment.created_at.desc()).all()
    total = sum(p.amount for p in payments if p.is_confirmed)
    return jsonify({'student': student.to_dict(), 'payments': [p.to_dict() for p in payments], 'total_confirmed': total})


# ════════════════════════════════════════════════════════════════════════════
#  MONITORING ROUTES  (coordinator can also do monitoring)
#  These proxy the supervisor routes — coordinator role is accepted by supervisor.py
# ════════════════════════════════════════════════════════════════════════════
# NOTE: The supervisor blueprint already accepts 'coordinator' role.
# We expose /coordinator/monitoring endpoints that simply re-use the same logic.

from models import MonitoringRecord, Teacher, Subject, Class, SchoolSettings
from datetime import date

@coordinator_bp.route('/monitoring', methods=['POST'])
@jwt_required()
def coord_add_monitoring():
    """Coordinator records teacher monitoring — same logic as supervisor."""
    claims  = get_jwt()
    if claims.get('role') not in ('coordinator', 'admin'):
        return jsonify({'error': 'Access denied'}), 403

    user_id          = get_jwt_identity()
    data             = request.get_json(silent=True) or {}
    teacher_id       = data.get('teacher_id')
    subject_id       = data.get('subject_id')
    class_id         = data.get('class_id')
    attendance_date  = data.get('attendance_date')
    students_present = data.get('students_present', 0)
    session_type     = data.get('session_type', 'Normal')
    time_in          = data.get('time_in')
    period           = data.get('period')
    notes            = data.get('notes', '')

    if not teacher_id or not attendance_date:
        return jsonify({'error': 'teacher_id and attendance_date are required'}), 400

    try:
        rec_date = date.fromisoformat(attendance_date)
        if rec_date > date.today():
            return jsonify({'error': 'Cannot record monitoring for a future date'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    is_on_time = None
    if time_in:
        try:
            from datetime import datetime as dt2
            settings = SchoolSettings.query.first()
            if session_type == 'Normal':
                ref_time_str = None
                if period and '(' in period and '–' in period:
                    try:
                        ref_time_str = period.split('(')[1].split('–')[0].strip()
                    except Exception:
                        ref_time_str = None
                if not ref_time_str and settings and settings.normal_start:
                    ref_time_str = settings.normal_start
                if ref_time_str:
                    ref_dt = dt2.strptime(ref_time_str, '%H:%M')
                    in_dt  = dt2.strptime(time_in, '%H:%M')
                    is_on_time = (in_dt <= ref_dt)
            else:
                if settings and settings.extended_start:
                    ref_dt = dt2.strptime(settings.extended_start, '%H:%M')
                    in_dt  = dt2.strptime(time_in, '%H:%M')
                    is_on_time = (in_dt <= ref_dt)
        except Exception:
            is_on_time = None

    record = MonitoringRecord(
        recorded_by      = user_id,
        teacher_id       = teacher_id,
        subject_id       = subject_id or None,
        class_id         = class_id or None,
        attendance_date  = rec_date,
        students_present = int(students_present),
        session_type     = session_type,
        time_in          = time_in,
        period           = period,
        is_on_time       = is_on_time,
        notes            = notes,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({'message': 'Monitoring record saved', 'record': record.to_dict()}), 201


@coordinator_bp.route('/monitoring', methods=['GET'])
@jwt_required()
def coord_get_monitoring():
    claims  = get_jwt()
    if claims.get('role') not in ('coordinator', 'admin'):
        return jsonify({'error': 'Access denied'}), 403

    user_id      = get_jwt_identity()
    role         = claims.get('role')
    date_from    = request.args.get('date_from')
    date_to      = request.args.get('date_to')
    session_type = request.args.get('session_type')

    q = MonitoringRecord.query
    if role not in ('admin',):
        q = q.filter_by(recorded_by=user_id)
    if date_from:
        try: q = q.filter(MonitoringRecord.attendance_date >= date.fromisoformat(date_from))
        except ValueError: pass
    if date_to:
        try: q = q.filter(MonitoringRecord.attendance_date <= date.fromisoformat(date_to))
        except ValueError: pass
    if session_type:
        q = q.filter_by(session_type=session_type)

    records = q.order_by(MonitoringRecord.attendance_date.desc()).all()
    return jsonify({'records': [r.to_dict() for r in records]})


@coordinator_bp.route('/monitoring/<int:record_id>', methods=['DELETE'])
@jwt_required()
def coord_delete_monitoring(record_id):
    claims  = get_jwt()
    if claims.get('role') not in ('coordinator', 'admin'):
        return jsonify({'error': 'Access denied'}), 403

    user_id = get_jwt_identity()
    role    = claims.get('role')
    record  = MonitoringRecord.query.get_or_404(record_id)

    if role != 'admin' and str(record.recorded_by) != str(user_id):
        return jsonify({'error': 'You can only delete your own records'}), 403

    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': 'Record deleted'})


@coordinator_bp.route('/teacher-summary', methods=['GET'])
@jwt_required()
def coord_teacher_summary():
    claims = get_jwt()
    if claims.get('role') not in ('coordinator', 'admin'):
        return jsonify({'error': 'Access denied'}), 403

    teachers = Teacher.query.filter_by(is_active=True).all()
    result = []
    for t in teachers:
        records = MonitoringRecord.query.filter_by(teacher_id=t.id).all()
        normal_total    = sum(1 for r in records if r.session_type == 'Normal')
        normal_ontime   = sum(1 for r in records if r.session_type == 'Normal' and r.is_on_time is True)
        normal_late     = sum(1 for r in records if r.session_type == 'Normal' and r.is_on_time is False)
        extended_total  = sum(1 for r in records if r.session_type == 'Extended')
        extended_ontime = sum(1 for r in records if r.session_type == 'Extended' and r.is_on_time is True)
        extended_late   = sum(1 for r in records if r.session_type == 'Extended' and r.is_on_time is False)
        result.append({
            'teacher_id': t.id, 'teacher_name': t.full_name,
            'primary_subject': t.subject.name if t.subject else '—',
            'normal_total': normal_total, 'normal_ontime': normal_ontime, 'normal_late': normal_late,
            'extended_total': extended_total, 'extended_ontime': extended_ontime, 'extended_late': extended_late,
            'grand_total': normal_total + extended_total,
        })
    result.sort(key=lambda x: x['teacher_name'])
    return jsonify({'summary': result})
