from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from csv_manager import csv_manager
from datetime import datetime
from database import db, Equipment, Reservation, UsageLog

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/list')
def equipment_list():
    equipment_data = csv_manager.read_csv('equipment.csv')
    equipment_list = equipment_data.to_dict('records') if not equipment_data.empty else []
    return render_template('equipment/list.html', equipment=equipment_list)

@equipment_bp.route('/add', methods=['POST'])
def add_equipment():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'name': request.form.get('name'),
        'model': request.form.get('model'),
        'manufacturer': request.form.get('manufacturer'),
        'location': request.form.get('location'),
        'status': request.form.get('status', '사용 가능'),
        'purchase_date': request.form.get('purchase_date'),
        'maintenance_date': request.form.get('maintenance_date', ''),
        'notes': request.form.get('notes', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('equipment.csv', data):
        flash('장비가 성공적으로 추가되었습니다.', 'success')
    else:
        flash('장비 추가 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('equipment.equipment_list'))

@equipment_bp.route('/list')
def equipment_list_page():
    """장비 목록 페이지"""
    equipment_list = Equipment.query.all()
    return render_template('equipment/list_page.html', equipment=equipment_list)

@equipment_bp.route('/reservations')
def reservations_page():
    """장비 예약 페이지"""
    equipment_list = Equipment.query.filter_by(status='사용가능').all()
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
    """API endpoint for calendar reservations"""
    try:
        reservations = Reservation.query.all()
        events = []
        
        for reservation in reservations:
            # Combine date and time for start/end datetime
            start_datetime = datetime.combine(reservation.start_date, reservation.start_time or datetime.min.time())
            end_datetime = datetime.combine(reservation.end_date, reservation.end_time or datetime.max.time())
            
            events.append({
                'id': reservation.id,
                'title': f"{reservation.equipment_name} - {reservation.reserver}",
                'start': start_datetime.isoformat(),
                'end': end_datetime.isoformat(),
                'backgroundColor': get_equipment_color(reservation.equipment_name),
                'borderColor': get_equipment_color(reservation.equipment_name),
                'extendedProps': {
                    'equipment_name': reservation.equipment_name,
                    'reserver': reservation.reserver,
                    'purpose': reservation.purpose,
                    'notes': reservation.notes,
                    'status': reservation.status
                }
            })
        
        return jsonify({
            'success': True,
            'reservations': [{
                'id': reservation.id,
                'equipment_name': reservation.equipment_name,
                'reserver': reservation.reserver,
                'start_date': reservation.start_date.strftime('%Y-%m-%d'),
                'end_date': reservation.end_date.strftime('%Y-%m-%d'),
                'start_time': reservation.start_time.strftime('%H:%M') if reservation.start_time else None,
                'end_time': reservation.end_time.strftime('%H:%M') if reservation.end_time else None,
                'purpose': reservation.purpose,
                'notes': reservation.notes,
                'status': reservation.status
            } for reservation in reservations]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
    usage_log_data = csv_manager.read_csv('usage_log.csv')
    usage_log_list = usage_log_data.to_dict('records') if not usage_log_data.empty else []
    return render_template('equipment/usage_log.html', usage_logs=usage_log_list)

@equipment_bp.route('/usage_log/add', methods=['POST'])
def add_usage_log():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'equipment_name': request.form.get('equipment_name'),
        'user_name': request.form.get('user_name'),
        'usage_date': request.form.get('usage_date'),
        'start_time': request.form.get('start_time'),
        'end_time': request.form.get('end_time'),
        'purpose': request.form.get('purpose'),
        'notes': request.form.get('notes', ''),
        'issues': request.form.get('issues', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('usage_log.csv', data):
        flash('사용일지가 성공적으로 작성되었습니다.', 'success')
    else:
        flash('사용일지 작성 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('equipment.usage_log'))

# 통합 장비 관리 페이지
@equipment_bp.route('/management')
def equipment_management_old():
    return render_template('equipment/management.html')

# 장비 API 엔드포인트
@equipment_bp.route('/api/equipment')
def api_equipment():
    """장비 목록 API"""
    try:
        equipment_list = Equipment.query.all()
        equipment_data = []
        for eq in equipment_list:
            equipment_data.append({
                'id': eq.id,
                'equipment_id': eq.equipment_id,
                'name': eq.name,
                'model': eq.model,
                'manufacturer': eq.manufacturer,
                'serial_number': eq.serial_number,
                'location': eq.location,
                'manager': eq.manager,
                'status': eq.status,
                'purchase_date': eq.purchase_date.strftime('%Y-%m-%d') if eq.purchase_date else None,
                'purchase_price': float(eq.purchase_price) if eq.purchase_price else None,
                'maintenance_date': eq.maintenance_date.strftime('%Y-%m-%d') if eq.maintenance_date else None,
                'warranty_expiry': eq.warranty_expiry.strftime('%Y-%m-%d') if eq.warranty_expiry else None,
                'specifications': eq.specifications,
                'notes': getattr(eq, 'notes', None)
            })
        return jsonify({
            'success': True,
            'equipment': equipment_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/api/equipment/add', methods=['POST'])
def api_add_equipment():
    """장비 추가 API"""
    try:
        data = request.get_json()
        
        # 장비 ID 생성
        last_equipment = Equipment.query.order_by(Equipment.id.desc()).first()
        next_id = (last_equipment.id + 1) if last_equipment else 1
        equipment_id = f"EQ{next_id:03d}"
        
        new_equipment = Equipment(
            equipment_id=data.get('equipment_id', equipment_id),
            name=data['name'],
            model=data.get('model'),
            manufacturer=data.get('manufacturer'),
            serial_number=data.get('serial_number'),
            location=data.get('location'),
            manager=data.get('manager'),
            status=data.get('status', '사용가능'),
            purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data.get('purchase_date') else None,
            purchase_price=float(data['purchase_price']) if data.get('purchase_price') else None,
            maintenance_date=datetime.strptime(data['maintenance_date'], '%Y-%m-%d').date() if data.get('maintenance_date') else None,
            warranty_expiry=datetime.strptime(data['warranty_expiry'], '%Y-%m-%d').date() if data.get('warranty_expiry') else None,
            specifications=data.get('specifications'),
            notes=data.get('notes')
        )
        
        db.session.add(new_equipment)
        db.session.commit()
        
        return jsonify({'success': True, 'id': new_equipment.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
        equipment.purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data.get('purchase_date') else None
        equipment.purchase_price = float(data['purchase_price']) if data.get('purchase_price') else None
        equipment.maintenance_date = datetime.strptime(data['maintenance_date'], '%Y-%m-%d').date() if data.get('maintenance_date') else None
        equipment.warranty_expiry = datetime.strptime(data['warranty_expiry'], '%Y-%m-%d').date() if data.get('warranty_expiry') else None
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
    """예약 추가 API"""
    try:
        data = request.get_json()
        
        # 장비 정보 조회
        equipment = Equipment.query.get(data['equipment_id'])
        if not equipment:
            return jsonify({'error': '장비를 찾을 수 없습니다.'}), 400
        
        new_reservation = Reservation(
            equipment_name=equipment.name,
            reserver=data['reserver'],
            purpose=data['purpose'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else None,
            end_time=datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None,
            status='예약'
        )
        
        db.session.add(new_reservation)
        db.session.flush()  # ID를 얻기 위해 flush
        
        # 사용일지에 자동 추가
        new_usage_log = UsageLog(
            equipment_name=equipment.name,
            user=data['reserver'],
            usage_date=new_reservation.start_date,
            start_time=new_reservation.start_time,
            end_time=new_reservation.end_time,
            purpose=data['purpose']
        )
        
        db.session.add(new_usage_log)
        db.session.commit()
        
        return jsonify({'success': True, 'id': new_reservation.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
    """사용일지 추가 API"""
    try:
        data = request.get_json()
        
        new_log = UsageLog(
            equipment_name=data['equipment_name'],
            user=data['user'],
            usage_date=datetime.strptime(data['usage_date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(data['start_time'], '%H:%M').time() if data.get('start_time') else None,
            end_time=datetime.strptime(data['end_time'], '%H:%M').time() if data.get('end_time') else None,
            purpose=data['purpose'],
            condition_after=data.get('condition_after', '정상'),
            issues=data.get('issues')
        )
        
        db.session.add(new_log)
        db.session.commit()
        
        return jsonify({'success': True, 'id': new_log.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 사용일지 API 엔드포인트
@equipment_bp.route('/api/usage-logs')
def api_usage_logs():
    """사용일지 목록 API"""
    try:
        usage_logs = UsageLog.query.order_by(UsageLog.usage_date.desc()).all()
        logs_data = []
        for log in usage_logs:
            logs_data.append({
                'id': log.id,
                'equipment_name': log.equipment_name,
                'user': log.user,
                'usage_date': log.usage_date.strftime('%Y-%m-%d'),
                'start_time': log.start_time.strftime('%H:%M') if log.start_time else None,
                'end_time': log.end_time.strftime('%H:%M') if log.end_time else None,
                'purpose': log.purpose,
                'condition_before': log.condition_before,
                'condition_after': log.condition_after,
                'issues': log.issues
            })
        return jsonify(logs_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@equipment_bp.route('/api/usage-logs/<int:log_id>/update', methods=['POST'])
def api_update_usage_log(log_id):
    """사용일지 수정 API"""
    try:
        usage_log = UsageLog.query.get_or_404(log_id)
        data = request.get_json()
        
        usage_log.condition_before = data.get('condition_before', '')
        usage_log.condition_after = data.get('condition_after', '')
        usage_log.issues = data.get('issues', '')
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
