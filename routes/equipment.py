from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from app import db, Equipment, Reservation, UsageLog
import csv

equipment_bp = Blueprint('equipment', __name__)

def parse_date(date_str):
    """문자열을 date 객체로 변환하는 헬퍼 함수"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

@equipment_bp.route('/list')
def equipment_list():
    equipment = Equipment.query.order_by(Equipment.created_date.desc()).all()
    equipment_list = []
    for e in equipment:
        equipment_list.append({
            'id': e.id,
            'equipment_id': e.equipment_id,
            'name': e.name,
            'model': e.model,
            'manufacturer': e.manufacturer,
            'location': e.location,
            'status': e.status,
            'purchase_date': e.purchase_date.strftime('%Y-%m-%d') if e.purchase_date else '',
            'maintenance_date': e.maintenance_date.strftime('%Y-%m-%d') if e.maintenance_date else '',
            'notes': e.notes,
            'created_date': e.created_date.strftime('%Y-%m-%d') if e.created_date else ''
        })
    return render_template('equipment/list.html', equipment=equipment_list)

@equipment_bp.route('/add', methods=['POST'])
def add_equipment():
    try:
        equipment = Equipment(
            equipment_id=datetime.now().strftime('%Y%m%d%H%M%S'),
            name=request.form.get('name'),
            model=request.form.get('model'),
            manufacturer=request.form.get('manufacturer'),
            location=request.form.get('location'),
            status=request.form.get('status', '사용 가능'),
            purchase_date=parse_date(request.form.get('purchase_date')),
            maintenance_date=parse_date(request.form.get('maintenance_date')),
            notes=request.form.get('notes', ''),
            created_date=datetime.now()
        )
        db.session.add(equipment)
        db.session.commit()
        flash('장비가 성공적으로 추가되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'장비 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('equipment.equipment_list'))

@equipment_bp.route('/list')
def equipment_list_page():
    equipment_list = Equipment.query.all()
    return render_template('equipment/list_page.html', equipment=equipment_list)

@equipment_bp.route('/reservations')
def reservations_page():
    equipment_list = Equipment.query.filter(Equipment.status.in_(['사용 가능', '사용가능'])).all()
    return render_template('equipment/reservations_page.html', equipment=equipment_list)

@equipment_bp.route('/usage-log')
def usage_log_page():
    """사용일지 페이지"""
    return render_template('equipment/usage_log_page.html')

@equipment_bp.route('/all-in-one')
def equipment_management():
    """장비 관리 통합 페이지 (기존)"""
    return render_template('equipment/management.html')

@equipment_bp.route('/api/reservations')
def api_reservations():
    try:
        reservations = Reservation.query.order_by(Reservation.start_date.desc()).all()
        result = []
        for r in reservations:
            # 장비 id를 name으로 역참조
            equipment = Equipment.query.filter_by(name=r.equipment_name).first()
            equipment_id = equipment.id if equipment else None
            result.append({
                'id': r.id,
                'equipment_id': equipment_id,
                'equipment_name': r.equipment_name,
                'reserver': r.reserver,
                'purpose': r.purpose,
                'start_date': r.start_date.strftime('%Y-%m-%d') if r.start_date else '',
                'end_date': r.end_date.strftime('%Y-%m-%d') if r.end_date else '',
                'start_time': r.start_time.strftime('%H:%M') if r.start_time else '',
                'end_time': r.end_time.strftime('%H:%M') if r.end_time else '',
                'status': r.status,
                'notes': r.notes,
                'created_date': r.created_date.strftime('%Y-%m-%d') if r.created_date else ''
            })
        return jsonify({'success': True, 'reservations': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_equipment_color(equipment_name):
    """Get consistent color for equipment"""
    colors = ['#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6f42c1', '#e83e8c', '#fd7e14']
    return colors[hash(equipment_name) % len(colors)]

@equipment_bp.route('/reservations/add', methods=['POST'])
def add_reservation():
    try:
        data = request.get_json() if request.is_json else request.form
        
        # Parse dates and times
        if data.get('start'):
            start_str = str(data.get('start'))
            if start_str and start_str.endswith('Z'):
                start_str = start_str.replace('Z', '+00:00')
            start_datetime = datetime.fromisoformat(start_str)
            start_date = start_datetime.date()
            start_time = start_datetime.time()
        else:
            start_date_str = data.get('start_date')
            if start_date_str:
                start_date = datetime.strptime(str(start_date_str), '%Y-%m-%d').date()
            else:
                raise ValueError("Start date is required")
            
            start_time_str = data.get('start_time')
            start_time = datetime.strptime(str(start_time_str), '%H:%M').time() if start_time_str else None
        
        if data.get('end'):
            end_str = str(data.get('end'))
            if end_str and end_str.endswith('Z'):
                end_str = end_str.replace('Z', '+00:00')
            end_datetime = datetime.fromisoformat(end_str)
            end_date = end_datetime.date()
            end_time = end_datetime.time()
        else:
            end_date_str = data.get('end_date')
            if end_date_str:
                end_date = datetime.strptime(str(end_date_str), '%Y-%m-%d').date()
            else:
                end_date = start_date
                
            end_time_str = data.get('end_time')
            end_time = datetime.strptime(str(end_time_str), '%H:%M').time() if end_time_str else None
        
        new_reservation = Reservation()
        new_reservation.equipment_name = data.get('equipment_name')
        new_reservation.reserver = data.get('reserver')
        new_reservation.purpose = data.get('purpose', '')
        new_reservation.start_date = start_date
        new_reservation.end_date = end_date
        new_reservation.start_time = start_time
        new_reservation.end_time = end_time
        new_reservation.status = '예약'
        new_reservation.notes = data.get('notes', '')
        
        db.session.add(new_reservation)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': '예약이 생성되었습니다.'})
        else:
            flash('장비 예약이 성공적으로 완료되었습니다.', 'success')
            return redirect(url_for('equipment.reservations'))
    
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': f'예약 생성 중 오류가 발생했습니다: {str(e)}'}), 500
        else:
            flash(f'장비 예약 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('equipment.reservations'))

@equipment_bp.route('/reservations/update/<int:reservation_id>', methods=['POST'])
def update_reservation(reservation_id):
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        data = request.get_json() if request.is_json else request.form
        
        # Update reservation details
        if data.get('start'):
            start_str = str(data.get('start'))
            if start_str and start_str.endswith('Z'):
                start_str = start_str.replace('Z', '+00:00')
            start_datetime = datetime.fromisoformat(start_str)
            reservation.start_date = start_datetime.date()
            reservation.start_time = start_datetime.time()
        
        if data.get('end'):
            end_str = str(data.get('end'))
            if end_str and end_str.endswith('Z'):
                end_str = end_str.replace('Z', '+00:00')
            end_datetime = datetime.fromisoformat(end_str)
            reservation.end_date = end_datetime.date()
            reservation.end_time = end_datetime.time()
        
        if data.get('equipment_name'):
            reservation.equipment_name = data.get('equipment_name')
        if data.get('reserver'):
            reservation.reserver = data.get('reserver')
        if data.get('purpose'):
            reservation.purpose = data.get('purpose')
        if data.get('notes'):
            reservation.notes = data.get('notes')
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': '예약이 수정되었습니다.'})
        else:
            flash('예약이 성공적으로 수정되었습니다.', 'success')
            return redirect(url_for('equipment.reservations'))
    
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': f'예약 수정 중 오류가 발생했습니다: {str(e)}'}), 500
        else:
            flash(f'예약 수정 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('equipment.reservations'))

@equipment_bp.route('/reservations/delete/<int:reservation_id>', methods=['POST', 'DELETE'])
def delete_reservation(reservation_id):
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        db.session.delete(reservation)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'success': True, 'message': '예약이 삭제되었습니다.'})
        else:
            flash('예약이 성공적으로 삭제되었습니다.', 'success')
            return redirect(url_for('equipment.reservations'))
    
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': f'예약 삭제 중 오류가 발생했습니다: {str(e)}'}), 500
        else:
            flash(f'예약 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('equipment.reservations'))

@equipment_bp.route('/usage_log')
def usage_log():
    usage_logs = UsageLog.query.order_by(UsageLog.usage_date.desc(), UsageLog.start_time.asc()).all()
    return render_template('equipment/usage_log.html', usage_logs=usage_logs)

@equipment_bp.route('/usage_log/add', methods=['POST'])
def add_usage_log():
    try:
        usage_log = UsageLog(
            equipment_name=request.form.get('equipment_name'),
            user=request.form.get('user_name'),
            usage_date=datetime.strptime(request.form.get('usage_date'), '%Y-%m-%d').date() if request.form.get('usage_date') else None,
            start_time=datetime.strptime(request.form.get('start_time'), '%H:%M').time() if request.form.get('start_time') else None,
            end_time=datetime.strptime(request.form.get('end_time'), '%H:%M').time() if request.form.get('end_time') else None,
            purpose=request.form.get('purpose'),
            notes=request.form.get('notes', ''),
            issues=request.form.get('issues', ''),
            created_date=datetime.now()
        )
        db.session.add(usage_log)
        db.session.commit()
        flash('사용일지가 성공적으로 작성되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('사용일지 작성 중 오류가 발생했습니다: {}'.format(str(e)), 'error')
    return redirect(url_for('equipment.usage_log'))

# 통합 장비 관리 페이지
@equipment_bp.route('/management')
def equipment_management_old():
    return render_template('equipment/management.html')

# 장비 API 엔드포인트
@equipment_bp.route('/api/equipment')
def api_equipment():
    try:
        equipment_list = Equipment.query.order_by(Equipment.created_date.desc()).all()
        equipment_data = []
        for e in equipment_list:
            equipment_data.append({
                'id': e.id,
                'name': e.name,
                'model': e.model,
                'manufacturer': e.manufacturer,
                'location': e.location,
                'status': e.status,
                'asset_number': getattr(e, 'asset_number', ''),
                'purchase_date': e.purchase_date.strftime('%Y-%m-%d') if e.purchase_date else '',
                'maintenance_date': e.maintenance_date.strftime('%Y-%m-%d') if e.maintenance_date else '',
                'notes': e.notes,
                'created_date': e.created_date.strftime('%Y-%m-%d') if e.created_date else ''
            })
        return jsonify({'success': True, 'equipment': equipment_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@equipment_bp.route('/api/equipment/add', methods=['POST'])
def api_add_equipment():
    data = request.get_json()
    new_row = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'name': data['name'],
        'model': data.get('model', ''),
        'manufacturer': data.get('manufacturer', ''),
        'location': data.get('location', ''),
        'status': data.get('status', '사용 가능'),
        'asset_number': data.get('asset_number', ''),
        'purchase_date': data.get('purchase_date', ''),
        'maintenance_date': data.get('maintenance_date', ''),
        'notes': data.get('notes', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    try:
        # SQLAlchemy 모델로 데이터 추가
        equipment = Equipment(**new_row)
        db.session.add(equipment)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@equipment_bp.route('/api/equipment/<int:equipment_id>/update', methods=['POST'])
def api_update_equipment(equipment_id):
    """장비 수정 API"""
    try:
        equipment = Equipment.query.get_or_404(equipment_id)
        data = request.get_json()
        
        equipment.name = data['name']
        equipment.model = data.get('model')
        equipment.manufacturer = data.get('manufacturer')
        equipment.serial_number = data.get('serial_number')
        equipment.location = data.get('location')
        equipment.manager = data.get('manager')
        equipment.status = data.get('status', '사용가능')
        equipment.purchase_date = parse_date(data.get('purchase_date'))
        equipment.purchase_price = float(data['purchase_price']) if data.get('purchase_price') else None
        equipment.maintenance_date = parse_date(data.get('maintenance_date'))
        equipment.warranty_expiry = parse_date(data.get('warranty_expiry'))
        equipment.specifications = data.get('specifications')
        equipment.notes = data.get('notes')
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/api/equipment/<int:equipment_id>/delete', methods=['POST'])
def api_delete_equipment(equipment_id):
    """장비 삭제 API"""
    try:
        equipment = Equipment.query.get_or_404(equipment_id)
        
        # 관련 예약이 있는지 확인
        active_reservations = Reservation.query.filter_by(equipment_name=equipment.name, status='예약').count()
        if active_reservations > 0:
            return jsonify({'error': '활성 예약이 있는 장비는 삭제할 수 없습니다.'}), 400
        
        db.session.delete(equipment)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 예약 API 엔드포인트  
@equipment_bp.route('/api/reservations/add', methods=['POST'])
def api_add_reservation():
    try:
        data = request.get_json()
        equipment = Equipment.query.get(data['equipment_id'])
        if not equipment:
            return jsonify({'success': False, 'error': '장비를 찾을 수 없습니다.'}), 400
        reservation = Reservation(
            equipment_name=equipment.name,
            reserver=data['reserver'],
            purpose=data['purpose'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else None,
            end_time=datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None,
            status='예약',
            notes=data.get('notes', ''),
            created_date=datetime.now()
        )
        db.session.add(reservation)
        db.session.commit()
        return jsonify({'success': True, 'id': reservation.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@equipment_bp.route('/api/reservations/<int:reservation_id>/update', methods=['POST'])
def api_update_reservation_new(reservation_id):
    """예약 수정 API"""
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        data = request.get_json()
        
        # 장비 정보 조회
        equipment = Equipment.query.get(data['equipment_id'])
        if not equipment:
            return jsonify({'error': '장비를 찾을 수 없습니다.'}), 400
        
        old_equipment_name = reservation.equipment_name
        old_user = reservation.reserver
        old_date = reservation.start_date
        
        reservation.equipment_name = equipment.name
        reservation.reserver = data['reserver']
        reservation.purpose = data['purpose']
        reservation.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        reservation.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        reservation.start_time = datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else None
        reservation.end_time = datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None
        
        db.session.commit()
        
        # 연관된 사용일지도 업데이트
        usage_log = UsageLog.query.filter_by(
            equipment_name=old_equipment_name,
            user=old_user,
            usage_date=old_date
        ).first()
        
        if usage_log:
            usage_log.equipment_name = equipment.name
            usage_log.user = data['reserver']
            usage_log.usage_date = reservation.start_date
            usage_log.start_time = reservation.start_time
            usage_log.end_time = reservation.end_time
            usage_log.purpose = data['purpose']
            db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/api/reservations/<int:reservation_id>/delete', methods=['POST'])
def api_delete_reservation_new(reservation_id):
    """예약 삭제 API"""
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        
        # 연관된 사용일지도 삭제
        usage_logs = UsageLog.query.filter_by(
            equipment_name=reservation.equipment_name,
            user=reservation.reserver,
            usage_date=reservation.start_date
        ).all()
        
        for log in usage_logs:
            db.session.delete(log)
        
        db.session.delete(reservation)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/api/usage-logs/add', methods=['POST'])
def api_add_usage_log():
    try:
        data = request.get_json()
        usage_log = UsageLog(
            equipment_name=data['equipment_name'],
            user=data['user'],
            usage_date=datetime.strptime(data['usage_date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else None,
            end_time=datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None,
            purpose=data['purpose'],
            condition_before=data.get('condition_before', '정상'),
            condition_after=data.get('condition_after', '정상'),
            issues=data.get('issues', ''),
            created_date=datetime.now()
        )
        db.session.add(usage_log)
        db.session.commit()
        return jsonify({'success': True, 'id': usage_log.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# 사용일지 API 엔드포인트
@equipment_bp.route('/api/usage-logs')
def api_usage_logs():
    """사용일지 목록 API (DB 기반)"""
    try:
        usage_logs = UsageLog.query.order_by(UsageLog.usage_date.desc(), UsageLog.start_time.asc()).all()
        logs_data = []
        for log in usage_logs:
            logs_data.append({
                'id': str(log.id),
                'equipment_name': log.equipment_name,
                'user': log.user,
                'usage_date': log.usage_date.strftime('%Y-%m-%d') if log.usage_date else '',
                'start_time': log.start_time.strftime('%H:%M') if log.start_time else '',
                'end_time': log.end_time.strftime('%H:%M') if log.end_time else '',
                'purpose': log.purpose or '',
                'condition_before': getattr(log, 'condition_before', '정상') or '정상',
                'condition_after': getattr(log, 'condition_after', '정상') or '정상',
                'issues': log.issues or ''
            })
        return jsonify({'success': True, 'logs': logs_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@equipment_bp.route('/api/usage-logs/<log_id>/update', methods=['POST'])
def api_update_usage_log(log_id):
    """사용일지 수정 API"""
    try:
        usage_log = UsageLog.query.get_or_404(log_id)
        data = request.get_json()
        
        usage_log.condition_before = data.get('condition_before', '정상')
        usage_log.condition_after = data.get('condition_after', '정상')
        usage_log.issues = data.get('issues', '')
        usage_log.equipment_name = data.get('equipment_name')
        usage_log.user = data.get('user')
        usage_log.usage_date = datetime.strptime(data['usage_date'], '%Y-%m-%d').date() if data.get('usage_date') else usage_log.usage_date
        usage_log.start_time = datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else usage_log.start_time
        usage_log.end_time = datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else usage_log.end_time
        usage_log.purpose = data.get('purpose')
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@equipment_bp.route('/api/usage-logs/<log_id>/delete', methods=['POST'])
def api_delete_usage_log(log_id):
    """사용일지 삭제 API"""
    try:
        usage_log = UsageLog.query.get_or_404(log_id)
        db.session.delete(usage_log)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
