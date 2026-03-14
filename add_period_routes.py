f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\routes\admin.py','r',encoding='utf-8').read()

period_routes = '''
# --- PERIOD MANAGEMENT --------------------------------------------------------
@admin_bp.route('/periods', methods=['GET'])
@jwt_required()
def get_periods():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    from models import Period
    periods = Period.query.order_by(Period.order_num).all()
    return jsonify({'periods': [p.to_dict() for p in periods]})

@admin_bp.route('/periods', methods=['POST'])
@jwt_required()
def create_period():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    from models import Period
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'Period name required'}), 400
    p = Period(
        name=data['name'],
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        session_type=data.get('session_type', 'Normal'),
        order_num=data.get('order_num', 0)
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'message': 'Period created', 'period': p.to_dict()}), 201

@admin_bp.route('/periods/<int:pid>', methods=['PUT'])
@jwt_required()
def update_period(pid):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    from models import Period
    p = Period.query.get_or_404(pid)
    data = request.get_json()
    if 'name' in data: p.name = data['name']
    if 'start_time' in data: p.start_time = data['start_time']
    if 'end_time' in data: p.end_time = data['end_time']
    if 'session_type' in data: p.session_type = data['session_type']
    if 'order_num' in data: p.order_num = data['order_num']
    if 'is_active' in data: p.is_active = data['is_active']
    db.session.commit()
    return jsonify({'message': 'Period updated', 'period': p.to_dict()})

@admin_bp.route('/periods/<int:pid>', methods=['DELETE'])
@jwt_required()
def delete_period(pid):
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    from models import Period
    p = Period.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'Period deleted'})

# Public endpoint - all roles can read periods for dropdowns
@admin_bp.route('/periods/active', methods=['GET'])
@jwt_required()
def get_active_periods():
    from models import Period
    periods = Period.query.filter_by(is_active=True).order_by(Period.order_num).all()
    return jsonify({'periods': [p.to_dict() for p in periods]})

'''

# Add before last line of file
f = f.rstrip() + '\n' + period_routes
open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\routes\admin.py','w',encoding='utf-8').write(f)
print('Done!')
