from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from models import db, Student, Payment, CoordinatorClassAssignment, AcademicYear, Class

coordinator_bp = Blueprint('coordinator', __name__)


def coordinator_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        role = get_jwt().get('role')
        if role not in ('admin', 'coordinator'):
            return jsonify({'error': 'Coordinator access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


def _active_year_id():
    y = AcademicYear.query.filter_by(is_active=True).first()
    return y.id if y else None


def _my_class_ids(user_id):
    """Return list of class IDs assigned to this coordinator."""
    assignments = CoordinatorClassAssignment.query.filter_by(coordinator_id=user_id).all()
    return [a.class_id for a in assignments]


# ── My assigned classes ────────────────────────────────────────────────────────
@coordinator_bp.route('/classes', methods=['GET'])
@coordinator_required
def my_classes():
    uid = get_jwt_identity()
    assignments = CoordinatorClassAssignment.query.filter_by(coordinator_id=uid).all()
    return jsonify([
        {'class_id': a.class_id, 'class_name': a.class_.class_name}
        for a in assignments if a.class_
    ])


# ── Students in assigned class ─────────────────────────────────────────────────
@coordinator_bp.route('/students/<int:class_id>', methods=['GET'])
@coordinator_required
def class_students(class_id):
    uid     = get_jwt_identity()
    my_cids = _my_class_ids(uid)

    # Admins can see all; coordinators restricted
    if get_jwt().get('role') == 'coordinator' and class_id not in my_cids:
        return jsonify({'error': 'Access denied to this class'}), 403

    year_id = request.args.get('year_id') or _active_year_id()
    q = Student.query.filter_by(class_id=class_id, is_active=True)
    if year_id:
        q = q.filter_by(academic_year_id=int(year_id))
    return jsonify([s.to_dict() for s in q.order_by(Student.student_name).all()])


# ── Record payment (coordinator) ───────────────────────────────────────────────
@coordinator_bp.route('/payments', methods=['POST'])
@coordinator_required
def record_payment():
    data = request.get_json(silent=True) or {}
    uid  = get_jwt_identity()

    student_id = data.get('student_id')
    amount     = data.get('amount')
    purpose    = data.get('purpose')

    if not student_id or not amount or not purpose:
        return jsonify({'error': 'student_id, amount and purpose are required'}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than zero'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount'}), 400

    # Verify coordinator owns the class of this student
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    if get_jwt().get('role') == 'coordinator':
        my_cids = _my_class_ids(uid)
        if student.class_id not in my_cids:
            return jsonify({'error': 'You are not assigned to this student\'s class'}), 403

    year_id = data.get('academic_year_id') or _active_year_id()
    p = Payment(
        student_id=int(student_id),
        amount=amount,
        purpose=purpose,
        notes=data.get('notes'),
        collected_by_user_id=uid,
        academic_year_id=year_id,
        is_confirmed=False   # Awaits admin confirmation
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(p.to_dict()), 201


# ── View payments (coordinator sees own classes only) ──────────────────────────
@coordinator_bp.route('/payments', methods=['GET'])
@coordinator_required
def list_payments():
    uid     = get_jwt_identity()
    role    = get_jwt().get('role')
    year_id = request.args.get('year_id') or _active_year_id()
    class_id= request.args.get('class_id')

    q = Payment.query.join(Student, Student.id == Payment.student_id)

    if role == 'coordinator':
        my_cids = _my_class_ids(uid)
        if not my_cids:
            return jsonify([])
        q = q.filter(Student.class_id.in_(my_cids))
        if class_id and int(class_id) in my_cids:
            q = q.filter(Student.class_id == int(class_id))
    elif class_id:
        q = q.filter(Student.class_id == int(class_id))

    if year_id:
        q = q.filter(Payment.academic_year_id == int(year_id))

    return jsonify([p.to_dict() for p in q.order_by(Payment.created_at.desc()).all()])


# ── Student payment total (for live display) ───────────────────────────────────
@coordinator_bp.route('/payments/student/<int:student_id>', methods=['GET'])
@coordinator_required
def student_payment_total(student_id):
    uid     = get_jwt_identity()
    year_id = request.args.get('year_id') or _active_year_id()

    student = Student.query.get_or_404(student_id)

    # Validate access
    if get_jwt().get('role') == 'coordinator':
        my_cids = _my_class_ids(uid)
        if student.class_id not in my_cids:
            return jsonify({'error': 'Access denied'}), 403

    q = Payment.query.filter_by(student_id=student_id)
    if year_id:
        q = q.filter_by(academic_year_id=int(year_id))
    payments = q.order_by(Payment.created_at.desc()).all()
    total_paid = sum(float(p.amount) for p in payments)
    return jsonify({
        'student_name': student.student_name,
        'class_name':   student.class_.class_name if student.class_ else '',
        'total_paid':   total_paid,
        'payments':     [p.to_dict() for p in payments]
    })
