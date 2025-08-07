"""
장비 예약 및 사용일지 관련 라우트
(장비 CRUD 기능은 equipment_api.py와 equipment_pages.py로 분리됨)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from database import db, Equipment, Reservation, UsageLog
from utils.date_utils import parse_date, format_date
from utils.response_utils import json_success_response, json_error_response
import csv

equipment_bp = Blueprint('equipment', __name__)

# 예약 관련 라우트들
@equipment_bp.route('/api/reservations')
def api_reservations():
    """예약 목록 API"""
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
                'start_date': format_date(r.start_date),
                'end_date': format_date(r.end_date),
                'start_time': r.start_time.strftime('%H:%M') if r.start_time else '',
                'end_time': r.end_time.strftime('%H:%M') if r.end_time else '',
                'status': r.status,
                'notes': r.notes,
                'created_date': format_date(r.created_date)
            })
        return json_success_response({'reservations': result})
    except Exception as e:
        return json_error_response(str(e))

def get_equipment_color(equipment_name):
    """Get consistent color for equipment"""
    colors = ['#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6f42c1', '#e83e8c', '#fd7e14']
    return colors[hash(equipment_name) % len(colors)]

@equipment_bp.route('/reservations/add', methods=['POST'])
def add_reservation():
    """예약 추가 (폼 기반)"""
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
        new_reservation.status = data.get('status', '예약')
        new_reservation.notes = data.get('notes', '')
        new_reservation.created_date = datetime.now()
        
        db.session.add(new_reservation)
        db.session.commit()
        
        flash('예약이 성공적으로 추가되었습니다.', 'success')
        return redirect(url_for('equipment.reservations_page'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'예약 추가 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('equipment.reservations_page'))

@equipment_bp.route('/reservations/update/<int:reservation_id>', methods=['POST'])
def update_reservation(reservation_id):
    """예약 수정 (폼 기반)"""
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
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
        
        reservation.equipment_name = data.get('equipment_name')
        reservation.reserver = data.get('reserver')
        reservation.purpose = data.get('purpose', '')
        reservation.start_date = start_date
        reservation.end_date = end_date
        reservation.start_time = start_time
        reservation.end_time = end_time
        reservation.status = data.get('status', '예약')
        reservation.notes = data.get('notes', '')
        
        db.session.commit()
        
        flash('예약이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('equipment.reservations_page'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'예약 수정 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('equipment.reservations_page'))

@equipment_bp.route('/reservations/delete/<int:reservation_id>', methods=['POST', 'DELETE'])
def delete_reservation(reservation_id):
    """예약 삭제"""
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        db.session.delete(reservation)
        db.session.commit()
        
        flash('예약이 성공적으로 삭제되었습니다.', 'success')
        return redirect(url_for('equipment.reservations_page'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'예약 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('equipment.reservations_page'))

# 사용일지 관련 라우트들
@equipment_bp.route('/usage_log')
def usage_log():
    """사용일지 페이지 (기존)"""
    return render_template('equipment/usage_log_page.html')

@equipment_bp.route('/usage_log/add', methods=['POST'])
def add_usage_log():
    """사용일지 추가 (폼 기반)"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        new_log = UsageLog()
        new_log.equipment_name = data.get('equipment_name')
        new_log.user = data.get('user')
        new_log.usage_date = parse_date(data.get('usage_date'))
        new_log.start_time = datetime.strptime(data.get('start_time'), '%H:%M').time() if data.get('start_time') else None
        new_log.end_time = datetime.strptime(data.get('end_time'), '%H:%M').time() if data.get('end_time') else None
        new_log.purpose = data.get('purpose', '')
        new_log.notes = data.get('notes', '')
        new_log.condition_before = data.get('condition_before', '')
        new_log.condition_after = data.get('condition_after', '')
        new_log.issues = data.get('issues', '')
        new_log.created_date = datetime.now()
        
        db.session.add(new_log)
        db.session.commit()
        
        flash('사용일지가 성공적으로 추가되었습니다.', 'success')
        return redirect(url_for('equipment.usage_log'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'사용일지 추가 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('equipment.usage_log'))

# API 라우트들
@equipment_bp.route('/api/reservations/add', methods=['POST'])
def api_add_reservation():
    """예약 추가 API"""
    try:
        data = request.get_json()
        
        # equipment_id가 있으면 equipment_name으로 변환
        equipment_name = data.get('equipment_name')
        if data.get('equipment_id'):
            equipment = Equipment.query.get(data.get('equipment_id'))
            if equipment:
                equipment_name = equipment.name
            else:
                return json_error_response("존재하지 않는 장비입니다.")
        
        # Parse dates and times
        start_date = parse_date(data.get('start_date'))
        end_date = parse_date(data.get('end_date'))
        start_time = datetime.strptime(data.get('start_time'), '%H:%M').time() if data.get('start_time') else None
        end_time = datetime.strptime(data.get('end_time'), '%H:%M').time() if data.get('end_time') else None
        
        new_reservation = Reservation(
            equipment_name=equipment_name,
            reserver=data.get('reserver'),
            purpose=data.get('purpose', ''),
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            status=data.get('status', '예약'),
            notes=data.get('notes', ''),
            created_date=datetime.now()
        )
        
        db.session.add(new_reservation)
        db.session.commit()
        
        return json_success_response(message="예약이 성공적으로 추가되었습니다.")
        
    except Exception as e:
        db.session.rollback()
        return json_error_response(f"예약 추가 중 오류가 발생했습니다: {str(e)}")

@equipment_bp.route('/api/reservations/<int:reservation_id>/update', methods=['POST'])
def api_update_reservation_new(reservation_id):
    """예약 수정 API"""
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        data = request.get_json()
        
        # equipment_id가 있으면 equipment_name으로 변환
        equipment_name = data.get('equipment_name')
        if data.get('equipment_id'):
            equipment = Equipment.query.get(data.get('equipment_id'))
            if equipment:
                equipment_name = equipment.name
            else:
                return json_error_response("존재하지 않는 장비입니다.")
        
        # Parse dates and times
        start_date = parse_date(data.get('start_date'))
        end_date = parse_date(data.get('end_date'))
        start_time = datetime.strptime(data.get('start_time'), '%H:%M').time() if data.get('start_time') else None
        end_time = datetime.strptime(data.get('end_time'), '%H:%M').time() if data.get('end_time') else None
        
        reservation.equipment_name = equipment_name
        reservation.reserver = data.get('reserver')
        reservation.purpose = data.get('purpose', '')
        reservation.start_date = start_date
        reservation.end_date = end_date
        reservation.start_time = start_time
        reservation.end_time = end_time
        reservation.status = data.get('status', '예약')
        reservation.notes = data.get('notes', '')
        
        db.session.commit()
        
        return json_success_response(message="예약이 성공적으로 수정되었습니다.")
        
    except Exception as e:
        db.session.rollback()
        return json_error_response(f"예약 수정 중 오류가 발생했습니다: {str(e)}")

@equipment_bp.route('/api/reservations/<int:reservation_id>/delete', methods=['POST'])
def api_delete_reservation_new(reservation_id):
    """예약 삭제 API"""
    try:
        reservation = Reservation.query.get_or_404(reservation_id)
        db.session.delete(reservation)
        db.session.commit()
        
        return json_success_response(message="예약이 성공적으로 삭제되었습니다.")
        
    except Exception as e:
        db.session.rollback()
        return json_error_response(f"예약 삭제 중 오류가 발생했습니다: {str(e)}")

@equipment_bp.route('/api/usage-logs/add', methods=['POST'])
def api_add_usage_log():
    """사용일지 추가 API"""
    try:
        data = request.get_json()
        
        new_log = UsageLog(
            equipment_name=data.get('equipment_name'),
            user=data.get('user'),
            usage_date=parse_date(data.get('usage_date')),
            start_time=datetime.strptime(data.get('start_time'), '%H:%M').time() if data.get('start_time') else None,
            end_time=datetime.strptime(data.get('end_time'), '%H:%M').time() if data.get('end_time') else None,
            purpose=data.get('purpose', ''),
            notes=data.get('notes', ''),
            condition_before=data.get('condition_before', ''),
            condition_after=data.get('condition_after', ''),
            issues=data.get('issues', ''),
            created_date=datetime.now()
        )
        
        db.session.add(new_log)
        db.session.commit()
        
        return json_success_response(message="사용일지가 성공적으로 추가되었습니다.")
        
    except Exception as e:
        db.session.rollback()
        return json_error_response(f"사용일지 추가 중 오류가 발생했습니다: {str(e)}")

@equipment_bp.route('/api/usage-logs')
def api_usage_logs():
    """사용일지 목록 API"""
    try:
        logs = UsageLog.query.order_by(UsageLog.usage_date.desc()).all()
        result = []
        for log in logs:
            result.append({
                'id': log.id,
                'equipment_name': log.equipment_name,
                'user': log.user,
                'usage_date': format_date(log.usage_date),
                'start_time': log.start_time.strftime('%H:%M') if log.start_time else '',
                'end_time': log.end_time.strftime('%H:%M') if log.end_time else '',
                'purpose': log.purpose,
                'notes': log.notes,
                'condition_before': log.condition_before,
                'condition_after': log.condition_after,
                'issues': log.issues,
                'created_date': format_date(log.created_date)
            })
        return json_success_response({'logs': result})
    except Exception as e:
        return json_error_response(str(e))

@equipment_bp.route('/api/usage-logs/<log_id>/update', methods=['POST'])
def api_update_usage_log(log_id):
    """사용일지 수정 API"""
    try:
        log = UsageLog.query.get_or_404(log_id)
        data = request.get_json()
        
        log.equipment_name = data.get('equipment_name')
        log.user = data.get('user')
        log.usage_date = parse_date(data.get('usage_date'))
        log.start_time = datetime.strptime(data.get('start_time'), '%H:%M').time() if data.get('start_time') else None
        log.end_time = datetime.strptime(data.get('end_time'), '%H:%M').time() if data.get('end_time') else None
        log.purpose = data.get('purpose', '')
        log.notes = data.get('notes', '')
        log.condition_before = data.get('condition_before', '')
        log.condition_after = data.get('condition_after', '')
        log.issues = data.get('issues', '')
        
        db.session.commit()
        
        return json_success_response(message="사용일지가 성공적으로 수정되었습니다.")
        
    except Exception as e:
        db.session.rollback()
        return json_error_response(f"사용일지 수정 중 오류가 발생했습니다: {str(e)}")

@equipment_bp.route('/api/usage-logs/<log_id>/delete', methods=['POST'])
def api_delete_usage_log(log_id):
    """사용일지 삭제 API"""
    try:
        log = UsageLog.query.get_or_404(log_id)
        db.session.delete(log)
        db.session.commit()
        
        return json_success_response(message="사용일지가 성공적으로 삭제되었습니다.")
        
    except Exception as e:
        db.session.rollback()
        return json_error_response(f"사용일지 삭제 중 오류가 발생했습니다: {str(e)}")
