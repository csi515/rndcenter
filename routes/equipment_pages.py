"""
장비 관련 페이지 라우트
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.equipment_service import EquipmentService
from database import Equipment

equipment_pages_bp = Blueprint('equipment_pages', __name__)


@equipment_pages_bp.route('/list')
def equipment_list_page():
    """장비 목록 페이지"""
    try:
        equipment_list = Equipment.query.all()
        
        # Equipment 객체를 딕셔너리로 변환
        equipment_data = []
        for equipment in equipment_list:
            # 점검 상태 계산
            inspection_status = '정상'
            next_inspection_date = None
            
            if equipment.last_inspection_date and equipment.inspection_cycle_days:
                from datetime import timedelta
                next_inspection_date = equipment.last_inspection_date + timedelta(days=equipment.inspection_cycle_days)
                
                from datetime import date
                today = date.today()
                if next_inspection_date < today:
                    inspection_status = '점검지연'
                elif next_inspection_date - today <= timedelta(days=30):
                    inspection_status = '점검필요'
                else:
                    inspection_status = '정상'
            
            equipment_data.append({
                'id': equipment.id,
                'equipment_id': equipment.equipment_id,
                'name': equipment.name,
                'model': equipment.model,
                'manufacturer': equipment.manufacturer,
                'location': equipment.location,
                'status': equipment.status,
                'purchase_date': equipment.purchase_date.strftime('%Y-%m-%d') if equipment.purchase_date else '',
                'maintenance_date': equipment.maintenance_date.strftime('%Y-%m-%d') if equipment.maintenance_date else '',
                'inspection_cycle_days': equipment.inspection_cycle_days,
                'last_inspection_date': equipment.last_inspection_date.strftime('%Y-%m-%d') if equipment.last_inspection_date else '',
                'next_inspection_date': next_inspection_date.strftime('%Y-%m-%d') if next_inspection_date else '',
                'inspection_status': inspection_status,
                'notes': equipment.notes,
                'created_date': equipment.created_date.strftime('%Y-%m-%d') if equipment.created_date else ''
            })
        
        return render_template('equipment/list.html', equipment=equipment_data)
    except Exception as e:
        flash(f'장비 목록을 불러오는 중 오류가 발생했습니다: {str(e)}', 'error')
        return render_template('equipment/list.html', equipment=[])


@equipment_pages_bp.route('/reservations')
def reservations_page():
    """장비 예약 페이지"""
    try:
        equipment_list = Equipment.query.filter(
            Equipment.status.in_(['사용 가능', '사용가능'])
        ).all()
        return render_template('equipment/reservations_page.html', equipment=equipment_list)
    except Exception as e:
        flash(f'예약 페이지를 불러오는 중 오류가 발생했습니다: {str(e)}', 'error')
        return render_template('equipment/reservations_page.html', equipment=[])


@equipment_pages_bp.route('/usage-log')
def usage_log_page():
    """사용일지 페이지"""
    return render_template('equipment/usage_log_page.html')


@equipment_pages_bp.route('/management')
def equipment_management():
    """장비 관리 통합 페이지"""
    return render_template('equipment/management.html') 


 