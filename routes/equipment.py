from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from csv_manager import csv_manager
from datetime import datetime
from database import db, Equipment, Reservation

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

@equipment_bp.route('/reservations')
def reservations():
    # Get equipment list from database
    equipment_list = Equipment.query.filter_by(status='사용가능').all()
    
    return render_template('equipment/reservations.html', 
                         equipment=equipment_list)

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
        
        return jsonify(events)
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
