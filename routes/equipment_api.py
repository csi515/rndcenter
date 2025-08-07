"""
장비 관련 API 라우트
"""
from flask import Blueprint, request, jsonify
from services.equipment_service import EquipmentService
from utils.response_utils import json_success_response, json_error_response, validate_required_fields

equipment_api_bp = Blueprint('equipment_api', __name__)


@equipment_api_bp.route('/api/equipment')
def api_equipment():
    """장비 목록 API"""
    try:
        equipment_data = EquipmentService.get_all_equipment()
        return json_success_response({'equipment': equipment_data})
    except Exception as e:
        return json_error_response(str(e))


@equipment_api_bp.route('/api/equipment/add', methods=['POST'])
def api_add_equipment():
    """장비 추가 API"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        error = validate_required_fields(data, ['name'])
        if error:
            return json_error_response(error)
        
        result = EquipmentService.create_equipment(data)
        
        if result.get('success'):
            return json_success_response(message=result.get('message', '장비가 추가되었습니다.'))
        else:
            return json_error_response(result.get('error', '장비 추가에 실패했습니다.'))
            
    except Exception as e:
        return json_error_response(f"장비 추가 중 오류가 발생했습니다: {str(e)}")


@equipment_api_bp.route('/api/equipment/<int:equipment_id>/update', methods=['POST'])
def api_update_equipment(equipment_id):
    """장비 수정 API"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        error = validate_required_fields(data, ['name'])
        if error:
            return json_error_response(error)
        
        result = EquipmentService.update_equipment(equipment_id, data)
        
        if result.get('success'):
            return json_success_response(message=result.get('message', '장비가 수정되었습니다.'))
        else:
            return json_error_response(result.get('error', '장비 수정에 실패했습니다.'))
            
    except Exception as e:
        return json_error_response(f"장비 수정 중 오류가 발생했습니다: {str(e)}")


@equipment_api_bp.route('/api/equipment/<int:equipment_id>/delete', methods=['POST'])
def api_delete_equipment(equipment_id):
    """장비 삭제 API"""
    try:
        result = EquipmentService.delete_equipment(equipment_id)
        
        if result.get('success'):
            return json_success_response(message=result.get('message', '장비가 삭제되었습니다.'))
        else:
            return json_error_response(result.get('error', '장비 삭제에 실패했습니다.'))
            
    except Exception as e:
        return json_error_response(f"장비 삭제 중 오류가 발생했습니다: {str(e)}") 