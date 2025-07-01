from flask import Blueprint, render_template, request, redirect, url_for, flash
from csv_manager import csv_manager
from datetime import datetime

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
    reservations_data = csv_manager.read_csv('reservations.csv')
    equipment_data = csv_manager.read_csv('equipment.csv')
    
    reservations_list = reservations_data.to_dict('records') if not reservations_data.empty else []
    equipment_list = equipment_data.to_dict('records') if not equipment_data.empty else []
    
    return render_template('equipment/reservations.html', 
                         reservations=reservations_list,
                         equipment=equipment_list)

@equipment_bp.route('/reservations/add', methods=['POST'])
def add_reservation():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'equipment_name': request.form.get('equipment_name'),
        'user_name': request.form.get('user_name'),
        'reservation_date': request.form.get('reservation_date'),
        'start_time': request.form.get('start_time'),
        'end_time': request.form.get('end_time'),
        'purpose': request.form.get('purpose'),
        'status': '예약됨',
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('reservations.csv', data):
        flash('장비 예약이 성공적으로 완료되었습니다.', 'success')
    else:
        flash('장비 예약 중 오류가 발생했습니다.', 'error')
    
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
