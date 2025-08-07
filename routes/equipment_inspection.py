"""
장비 점검 기록 관련 라우트
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, timedelta
from database import db, Equipment, EquipmentInspection
from utils.date_utils import parse_date, format_date
from utils.response_utils import json_success_response, json_error_response

equipment_inspection_bp = Blueprint('equipment_inspection', __name__)

@equipment_inspection_bp.route('/equipment/inspections')
def inspection_list():
    """장비 점검 기록 목록 페이지"""
    try:
        inspections = EquipmentInspection.query.join(Equipment).order_by(EquipmentInspection.inspection_date.desc()).all()
        return render_template('equipment/inspections.html', inspections=inspections)
    except Exception as e:
        flash(f'점검 기록을 불러오는 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@equipment_inspection_bp.route('/equipment/inspections/add', methods=['GET', 'POST'])
def add_inspection():
    """장비 점검 기록 추가"""
    if request.method == 'GET':
        equipment_list = Equipment.query.all()
        return render_template('equipment/add_inspection.html', equipment_list=equipment_list)

@equipment_inspection_bp.route('/equipment/inspections/add/modal', methods=['GET'])
def add_inspection_modal():
    """장비 점검 기록 추가 모달"""
    equipment_list = Equipment.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('equipment/add_inspection_modal.html', equipment_list=equipment_list, today=today)
    
    try:
        data = request.form
        
        # 점검 기록 생성
        inspection = EquipmentInspection()
        inspection.equipment_id = int(data.get('equipment_id'))
        inspection.inspection_date = datetime.strptime(data.get('inspection_date'), '%Y-%m-%d').date()
        inspection.inspector = data.get('inspector')
        inspection.inspection_type = data.get('inspection_type', '정기점검')
        inspection.result = data.get('result', '정상')
        inspection.condition_before = data.get('condition_before', '')
        inspection.condition_after = data.get('condition_after', '')
        inspection.findings = data.get('findings', '')
        inspection.actions_taken = data.get('actions_taken', '')
        inspection.notes = data.get('notes', '')
        
        # 다음 점검일 계산
        if data.get('next_inspection_date'):
            inspection.next_inspection_date = datetime.strptime(data.get('next_inspection_date'), '%Y-%m-%d').date()
        else:
            # 기본적으로 1년 후
            inspection.next_inspection_date = inspection.inspection_date + timedelta(days=365)
        
        db.session.add(inspection)
        
        # 장비 정보 업데이트
        equipment = Equipment.query.get(inspection.equipment_id)
        if equipment:
            equipment.last_inspection_date = inspection.inspection_date
            equipment.next_inspection_date = inspection.next_inspection_date
            
            # 점검 상태 업데이트
            today = datetime.now().date()
            if inspection.next_inspection_date < today:
                equipment.inspection_status = '점검지연'
            elif inspection.next_inspection_date - today <= timedelta(days=30):
                equipment.inspection_status = '점검필요'
            else:
                equipment.inspection_status = '정상'
        
        db.session.commit()
        flash('점검 기록이 성공적으로 추가되었습니다.', 'success')
        return redirect(url_for('equipment_inspection.inspection_list'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'점검 기록 추가 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('equipment_inspection.add_inspection'))

@equipment_inspection_bp.route('/equipment/inspections/<int:inspection_id>')
def view_inspection(inspection_id):
    """점검 기록 상세 보기 (모달용)"""
    try:
        inspection = EquipmentInspection.query.get_or_404(inspection_id)
        return render_template('equipment/view_inspection_modal.html', inspection=inspection)
    except Exception as e:
        return f'<div class="alert alert-danger">점검 기록을 불러오는 중 오류가 발생했습니다: {str(e)}</div>'

@equipment_inspection_bp.route('/equipment/inspections/<int:inspection_id>/edit', methods=['GET', 'POST'])
def edit_inspection(inspection_id):
    """점검 기록 수정 (모달용)"""
    inspection = EquipmentInspection.query.get_or_404(inspection_id)
    
    if request.method == 'GET':
        equipment_list = Equipment.query.all()
        return render_template('equipment/edit_inspection_modal.html', inspection=inspection, equipment_list=equipment_list)
    
    try:
        data = request.form
        
        inspection.equipment_id = int(data.get('equipment_id'))
        inspection.inspection_date = datetime.strptime(data.get('inspection_date'), '%Y-%m-%d').date()
        inspection.inspector = data.get('inspector')
        inspection.inspection_type = data.get('inspection_type')
        inspection.result = data.get('result')
        inspection.condition_before = data.get('condition_before', '')
        inspection.condition_after = data.get('condition_after', '')
        inspection.findings = data.get('findings', '')
        inspection.actions_taken = data.get('actions_taken', '')
        inspection.notes = data.get('notes', '')
        
        if data.get('next_inspection_date'):
            inspection.next_inspection_date = datetime.strptime(data.get('next_inspection_date'), '%Y-%m-%d').date()
        
        db.session.commit()
        flash('점검 기록이 성공적으로 수정되었습니다.', 'success')
        return redirect(url_for('equipment_inspection.view_inspection', inspection_id=inspection.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'점검 기록 수정 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('equipment_inspection.edit_inspection', inspection_id=inspection_id))

@equipment_inspection_bp.route('/equipment/inspections/<int:inspection_id>/update', methods=['POST'])
def update_inspection(inspection_id):
    """점검 기록 수정 (모달용)"""
    try:
        inspection = EquipmentInspection.query.get_or_404(inspection_id)
        data = request.form
        
        inspection.equipment_id = int(data.get('equipment_id'))
        inspection.inspection_date = datetime.strptime(data.get('inspection_date'), '%Y-%m-%d').date()
        inspection.inspector = data.get('inspector')
        inspection.inspection_type = data.get('inspection_type')
        inspection.result = data.get('result')
        inspection.condition_before = data.get('condition_before', '')
        inspection.condition_after = data.get('condition_after', '')
        inspection.findings = data.get('findings', '')
        inspection.actions_taken = data.get('actions_taken', '')
        inspection.notes = data.get('notes', '')
        
        if data.get('next_inspection_date'):
            inspection.next_inspection_date = datetime.strptime(data.get('next_inspection_date'), '%Y-%m-%d').date()
        
        db.session.commit()
        return json_success_response({'message': '점검 기록이 성공적으로 수정되었습니다.'})
        
    except Exception as e:
        db.session.rollback()
        return json_error_response(str(e))

@equipment_inspection_bp.route('/equipment/inspections/<int:inspection_id>/delete', methods=['POST'])
def delete_inspection(inspection_id):
    """점검 기록 삭제"""
    try:
        inspection = EquipmentInspection.query.get_or_404(inspection_id)
        db.session.delete(inspection)
        db.session.commit()
        flash('점검 기록이 성공적으로 삭제되었습니다.', 'success')
        return redirect(url_for('equipment_inspection.inspection_list'))
    except Exception as e:
        db.session.rollback()
        flash(f'점검 기록 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('equipment_inspection.inspection_list'))

# API 라우트들
@equipment_inspection_bp.route('/api/inspections')
def api_inspections():
    """점검 기록 목록 API"""
    try:
        inspections = EquipmentInspection.query.join(Equipment).order_by(EquipmentInspection.inspection_date.desc()).all()
        result = []
        for inspection in inspections:
            result.append({
                'id': inspection.id,
                'equipment_id': inspection.equipment_id,
                'equipment_name': inspection.equipment.name,
                'inspection_date': format_date(inspection.inspection_date),
                'inspector': inspection.inspector,
                'inspection_type': inspection.inspection_type,
                'result': inspection.result,
                'condition_before': inspection.condition_before,
                'condition_after': inspection.condition_after,
                'findings': inspection.findings,
                'actions_taken': inspection.actions_taken,
                'next_inspection_date': format_date(inspection.next_inspection_date) if inspection.next_inspection_date else None,
                'notes': inspection.notes,
                'created_date': format_date(inspection.created_date)
            })
        return json_success_response(result)
    except Exception as e:
        return json_error_response(str(e))

@equipment_inspection_bp.route('/api/inspections/add', methods=['POST'])
def api_add_inspection():
    """점검 기록 추가 API"""
    try:
        data = request.get_json()
        
        inspection = EquipmentInspection()
        inspection.equipment_id = int(data.get('equipment_id'))
        inspection.inspection_date = datetime.strptime(data.get('inspection_date'), '%Y-%m-%d').date()
        inspection.inspector = data.get('inspector')
        inspection.inspection_type = data.get('inspection_type', '정기점검')
        inspection.result = data.get('result', '정상')
        inspection.condition_before = data.get('condition_before', '')
        inspection.condition_after = data.get('condition_after', '')
        inspection.findings = data.get('findings', '')
        inspection.actions_taken = data.get('actions_taken', '')
        inspection.notes = data.get('notes', '')
        
        if data.get('next_inspection_date'):
            inspection.next_inspection_date = datetime.strptime(data.get('next_inspection_date'), '%Y-%m-%d').date()
        else:
            inspection.next_inspection_date = inspection.inspection_date + timedelta(days=365)
        
        db.session.add(inspection)
        
        # 장비 정보 업데이트
        equipment = Equipment.query.get(inspection.equipment_id)
        if equipment:
            equipment.last_inspection_date = inspection.inspection_date
            equipment.next_inspection_date = inspection.next_inspection_date
            
            # 점검 상태 업데이트
            today = datetime.now().date()
            if inspection.next_inspection_date < today:
                equipment.inspection_status = '점검지연'
            elif inspection.next_inspection_date - today <= timedelta(days=30):
                equipment.inspection_status = '점검필요'
            else:
                equipment.inspection_status = '정상'
        
        db.session.commit()
        return json_success_response({'message': '점검 기록이 성공적으로 추가되었습니다.'})
        
    except Exception as e:
        db.session.rollback()
        return json_error_response(str(e))

@equipment_inspection_bp.route('/api/inspections/<int:inspection_id>', methods=['GET'])
def api_get_inspection(inspection_id):
    """점검 기록 조회 API"""
    try:
        inspection = EquipmentInspection.query.get_or_404(inspection_id)
        result = {
            'id': inspection.id,
            'equipment_id': inspection.equipment_id,
            'equipment_name': inspection.equipment.name,
            'inspection_date': format_date(inspection.inspection_date),
            'inspector': inspection.inspector,
            'inspection_type': inspection.inspection_type,
            'result': inspection.result,
            'condition_before': inspection.condition_before,
            'condition_after': inspection.condition_after,
            'findings': inspection.findings,
            'actions_taken': inspection.actions_taken,
            'next_inspection_date': format_date(inspection.next_inspection_date) if inspection.next_inspection_date else None,
            'notes': inspection.notes,
            'created_date': format_date(inspection.created_date)
        }
        return json_success_response(result)
    except Exception as e:
        return json_error_response(str(e))

@equipment_inspection_bp.route('/api/inspections/<int:inspection_id>/update', methods=['POST'])
def api_update_inspection(inspection_id):
    """점검 기록 수정 API"""
    try:
        inspection = EquipmentInspection.query.get_or_404(inspection_id)
        data = request.get_json()
        
        inspection.equipment_id = int(data.get('equipment_id'))
        inspection.inspection_date = datetime.strptime(data.get('inspection_date'), '%Y-%m-%d').date()
        inspection.inspector = data.get('inspector')
        inspection.inspection_type = data.get('inspection_type')
        inspection.result = data.get('result')
        inspection.condition_before = data.get('condition_before', '')
        inspection.condition_after = data.get('condition_after', '')
        inspection.findings = data.get('findings', '')
        inspection.actions_taken = data.get('actions_taken', '')
        inspection.notes = data.get('notes', '')
        
        if data.get('next_inspection_date'):
            inspection.next_inspection_date = datetime.strptime(data.get('next_inspection_date'), '%Y-%m-%d').date()
        
        db.session.commit()
        return json_success_response({'message': '점검 기록이 성공적으로 수정되었습니다.'})
        
    except Exception as e:
        db.session.rollback()
        return json_error_response(str(e))

@equipment_inspection_bp.route('/api/inspections/<int:inspection_id>/delete', methods=['POST'])
def api_delete_inspection(inspection_id):
    """점검 기록 삭제 API"""
    try:
        inspection = EquipmentInspection.query.get_or_404(inspection_id)
        db.session.delete(inspection)
        db.session.commit()
        return json_success_response({'message': '점검 기록이 성공적으로 삭제되었습니다.'})
    except Exception as e:
        db.session.rollback()
        return json_error_response(str(e)) 