from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from csv_manager import csv_manager
from datetime import datetime
from database import db, Equipment, Reservation, UsageLog
import pandas as pd
import csv

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
    df = pd.read_csv('data/equipment.csv')
    equipment_list = df.to_dict('records') if not df.empty else []
    return render_template('equipment/list_page.html', equipment=equipment_list)

@equipment_bp.route('/reservations')
def reservations_page():
    df = pd.read_csv('data/equipment.csv')
    equipment_list = [row for _, row in df.iterrows() if row['status'] in ['사용 가능', '사용가능']]
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
        # CSV 파일이 없거나 비어있는 경우 처리
        try:
            df = pd.read_csv('data/reservations.csv')
            if df.empty:
                return jsonify({'success': True, 'reservations': []})
        except FileNotFoundError:
            return jsonify({'success': True, 'reservations': []})
        except pd.errors.EmptyDataError:
            return jsonify({'success': True, 'reservations': []})
        
        reservations = []
        for _, row in df.iterrows():
            reservations.append({
                'id': str(row['id']) if pd.notna(row['id']) else '',
                'equipment_id': str(row['equipment_id']) if pd.notna(row['equipment_id']) else '',
                'equipment_name': str(row['equipment_name']) if pd.notna(row['equipment_name']) else '',
                'reserver': str(row['reserver']) if pd.notna(row['reserver']) else '',
                'purpose': str(row['purpose']) if pd.notna(row['purpose']) else '',
                'start_date': str(row['start_date']) if pd.notna(row['start_date']) else '',
                'end_date': str(row['end_date']) if pd.notna(row['end_date']) else '',
                'start_time': str(row['start_time']) if pd.notna(row['start_time']) else '',
                'end_time': str(row['end_time']) if pd.notna(row['end_time']) else '',
                'status': str(row['status']) if pd.notna(row['status']) else '',
                'notes': str(row['notes']) if pd.notna(row['notes']) else '',
                'created_date': str(row['created_date']) if pd.notna(row['created_date']) else ''
            })
        return jsonify({'success': True, 'reservations': reservations})
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
    try:
        df = pd.read_csv('data/equipment.csv')
        equipment_data = []
        for _, row in df.iterrows():
            equipment_data.append({
                'id': str(row['id']) if pd.notna(row['id']) else '',
                'name': str(row['name']) if pd.notna(row['name']) else '',
                'model': str(row['model']) if pd.notna(row['model']) else '',
                'manufacturer': str(row['manufacturer']) if pd.notna(row['manufacturer']) else '',
                'location': str(row['location']) if pd.notna(row['location']) else '',
                'status': str(row['status']) if pd.notna(row['status']) else '',
                'asset_number': str(row['asset_number']) if pd.notna(row['asset_number']) else '',
                'purchase_date': str(row['purchase_date']) if pd.notna(row['purchase_date']) else '',
                'maintenance_date': str(row['maintenance_date']) if pd.notna(row['maintenance_date']) else '',
                'notes': str(row['notes']) if pd.notna(row['notes']) else '',
                'created_date': str(row['created_date']) if pd.notna(row['created_date']) else ''
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
    file_path = 'data/equipment.csv'
    try:
        # 파일이 없으면 헤더 추가
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                pass
        except FileNotFoundError:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=new_row.keys())
                writer.writeheader()
        # 데이터 추가
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=new_row.keys())
            writer.writerow(new_row)
        return jsonify({'success': True})
    except Exception as e:
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
    data = request.get_json()
    new_row = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'equipment_id': data['equipment_id'],
        'equipment_name': data['equipment_name'],
        'reserver': data['reserver'],
        'purpose': data['purpose'],
        'start_date': data['start_date'],
        'end_date': data['end_date'],
        'start_time': data.get('start_time', ''),
        'end_time': data.get('end_time', ''),
        'status': '예약',
        'notes': data.get('notes', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    file_path = 'data/reservations.csv'
    try:
        # 파일이 없으면 헤더 추가
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                pass
        except FileNotFoundError:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=new_row.keys())
                writer.writeheader()
        # 데이터 추가
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=new_row.keys())
            writer.writerow(new_row)
        return jsonify({'success': True})
    except Exception as e:
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
    """사용일지 추가 API"""
    try:
        data = request.get_json()
        new_row = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'equipment_name': data['equipment_name'],
            'user': data['user'],
            'usage_date': data['usage_date'],
            'start_time': data.get('start_time', ''),
            'end_time': data.get('end_time', ''),
            'purpose': data['purpose'],
            'condition_before': data.get('condition_before', '정상'),
            'condition_after': data.get('condition_after', '정상'),
            'issues': data.get('issues', ''),
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        file_path = 'data/usage_logs.csv'
        try:
            # 파일이 없으면 헤더 추가
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    pass
            except FileNotFoundError:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=new_row.keys())
                    writer.writeheader()
            # 데이터 추가
            with open(file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=new_row.keys())
                writer.writerow(new_row)
            return jsonify({'success': True, 'id': new_row['id']})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# 사용일지 API 엔드포인트
@equipment_bp.route('/api/usage-logs')
def api_usage_logs():
    """사용일지 목록 API"""
    try:
        # CSV 파일이 없거나 비어있는 경우 처리
        try:
            df = pd.read_csv('data/usage_logs.csv')
            if df.empty:
                return jsonify({'success': True, 'logs': []})
        except FileNotFoundError:
            return jsonify({'success': True, 'logs': []})
        except pd.errors.EmptyDataError:
            return jsonify({'success': True, 'logs': []})
        
        logs_data = []
        for _, row in df.iterrows():
            logs_data.append({
                'id': str(row['id']) if pd.notna(row['id']) else '',
                'equipment_name': str(row['equipment_name']) if pd.notna(row['equipment_name']) else '',
                'user': str(row['user']) if pd.notna(row['user']) else '',
                'usage_date': str(row['usage_date']) if pd.notna(row['usage_date']) else '',
                'start_time': str(row['start_time']) if pd.notna(row['start_time']) else '',
                'end_time': str(row['end_time']) if pd.notna(row['end_time']) else '',
                'purpose': str(row['purpose']) if pd.notna(row['purpose']) else '',
                'condition_before': str(row['condition_before']) if pd.notna(row['condition_before']) else '',
                'condition_after': str(row['condition_after']) if pd.notna(row['condition_after']) else '',
                'issues': str(row['issues']) if pd.notna(row['issues']) else ''
            })
        # 최신 날짜 순으로 정렬
        logs_data.sort(key=lambda x: x['usage_date'], reverse=True)
        return jsonify({'success': True, 'logs': logs_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@equipment_bp.route('/api/usage-logs/<log_id>/update', methods=['POST'])
def api_update_usage_log(log_id):
    """사용일지 수정 API"""
    try:
        df = pd.read_csv('data/usage_logs.csv')
        data = request.get_json()
        # 해당 ID의 행 찾기 (타입 일치 보장)
        mask = df['id'].astype(str) == str(log_id).strip()
        if not mask.any():
            return jsonify({'success': False, 'error': '사용일지를 찾을 수 없습니다.'})
        # 데이터 업데이트
        if 'condition_before' in data:
            df.loc[mask, 'condition_before'] = data['condition_before']
        if 'condition_after' in data:
            df.loc[mask, 'condition_after'] = data['condition_after']
        if 'issues' in data:
            df.loc[mask, 'issues'] = data['issues']
        if 'equipment_name' in data:
            df.loc[mask, 'equipment_name'] = data['equipment_name']
        if 'user' in data:
            df.loc[mask, 'user'] = data['user']
        if 'usage_date' in data:
            df.loc[mask, 'usage_date'] = data['usage_date']
        if 'start_time' in data:
            df.loc[mask, 'start_time'] = data['start_time']
        if 'end_time' in data:
            df.loc[mask, 'end_time'] = data['end_time']
        if 'purpose' in data:
            df.loc[mask, 'purpose'] = data['purpose']
        # CSV 파일에 저장
        df.to_csv('data/usage_logs.csv', index=False, encoding='utf-8')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@equipment_bp.route('/api/usage-logs/<log_id>/delete', methods=['POST'])
def api_delete_usage_log(log_id):
    """사용일지 삭제 API"""
    try:
        df = pd.read_csv('data/usage_logs.csv')
        # 해당 ID의 행 찾기 (타입 일치 보장)
        mask = df['id'].astype(str) == str(log_id).strip()
        if not mask.any():
            return jsonify({'success': False, 'error': '사용일지를 찾을 수 없습니다.'})
        df = df[~mask]  # 해당 행 삭제
        df.to_csv('data/usage_logs.csv', index=False, encoding='utf-8')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
