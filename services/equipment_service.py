"""
장비 관련 비즈니스 로직 서비스
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from database import db, Equipment, Reservation
from utils.date_utils import (
    parse_date, format_date, calculate_next_inspection_date, 
    get_inspection_status, generate_equipment_id
)
from utils.response_utils import success_response, error_response


class EquipmentService:
    """장비 관리 서비스 클래스"""
    
    @staticmethod
    def get_all_equipment() -> List[Dict]:
        """모든 장비 조회"""
        equipment_list = Equipment.query.order_by(Equipment.created_date.desc()).all()
        equipment_data = []
        
        for equipment in equipment_list:
            # 점검 상태 업데이트
            EquipmentService._update_inspection_status(equipment)
            
            equipment_data.append({
                'id': equipment.id,
                'name': equipment.name,
                'model': equipment.model,
                'manufacturer': equipment.manufacturer,
                'location': equipment.location,
                'status': equipment.status,
                'asset_number': getattr(equipment, 'asset_number', ''),
                'purchase_date': format_date(equipment.purchase_date),
                'maintenance_date': format_date(equipment.maintenance_date),
                'inspection_cycle_days': equipment.inspection_cycle_days,
                'last_inspection_date': format_date(equipment.last_inspection_date),
                'next_inspection_date': format_date(equipment.next_inspection_date),
                'inspection_status': equipment.inspection_status,
                'notes': equipment.notes,
                'created_date': format_date(equipment.created_date)
            })
        
        return equipment_data
    
    @staticmethod
    def create_equipment(data: Dict[str, Any]) -> Dict:
        """장비 생성"""
        try:
            # 점검 주기 계산
            next_inspection_date = None
            if data.get('last_inspection_date') and data.get('inspection_cycle_days'):
                last_date = parse_date(data.get('last_inspection_date'))
                cycle_days = int(data.get('inspection_cycle_days', 365))
                if last_date:
                    next_inspection_date = calculate_next_inspection_date(last_date, cycle_days)
            
            equipment = Equipment(
                equipment_id=data.get('equipment_id', generate_equipment_id()),
                name=data['name'],
                model=data.get('model', ''),
                manufacturer=data.get('manufacturer', ''),
                serial_number=data.get('serial_number', ''),
                location=data.get('location', ''),
                manager=data.get('manager', ''),
                status=data.get('status', '사용가능'),
                purchase_date=parse_date(data.get('purchase_date')),
                purchase_price=float(data['purchase_price']) if data.get('purchase_price') else None,
                maintenance_date=parse_date(data.get('maintenance_date')),
                warranty_expiry=parse_date(data.get('warranty_expiry')),
                inspection_cycle_days=int(data.get('inspection_cycle_days', 365)),
                last_inspection_date=parse_date(data.get('last_inspection_date')),
                next_inspection_date=next_inspection_date,
                specifications=data.get('specifications', ''),
                notes=data.get('notes', ''),
                created_date=datetime.now()
            )
            
            # 점검 상태 설정
            if equipment.last_inspection_date and equipment.inspection_cycle_days:
                EquipmentService._update_inspection_status(equipment)
            
            db.session.add(equipment)
            db.session.commit()
            
            return success_response(message="장비가 성공적으로 추가되었습니다.")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"장비 추가 중 오류가 발생했습니다: {str(e)}")
    
    @staticmethod
    def update_equipment(equipment_id: int, data: Dict[str, Any]) -> Dict:
        """장비 수정"""
        try:
            equipment = Equipment.query.get_or_404(equipment_id)
            
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
            equipment.inspection_cycle_days = int(data.get('inspection_cycle_days', 365))
            equipment.last_inspection_date = parse_date(data.get('last_inspection_date'))
            equipment.next_inspection_date = parse_date(data.get('next_inspection_date'))
            equipment.specifications = data.get('specifications')
            equipment.notes = data.get('notes')
            
            # 점검 상태 업데이트
            EquipmentService._update_inspection_status(equipment)
            
            db.session.commit()
            
            return success_response(message="장비가 성공적으로 수정되었습니다.")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"장비 수정 중 오류가 발생했습니다: {str(e)}")
    
    @staticmethod
    def delete_equipment(equipment_id: int) -> Dict:
        """장비 삭제"""
        try:
            equipment = Equipment.query.get_or_404(equipment_id)
            
            # 관련 예약이 있는지 확인
            active_reservations = Reservation.query.filter_by(
                equipment_name=equipment.name, status='예약'
            ).count()
            
            if active_reservations > 0:
                return error_response('활성 예약이 있는 장비는 삭제할 수 없습니다.')
            
            db.session.delete(equipment)
            db.session.commit()
            
            return success_response(message="장비가 성공적으로 삭제되었습니다.")
            
        except Exception as e:
            db.session.rollback()
            return error_response(f"장비 삭제 중 오류가 발생했습니다: {str(e)}")
    
    @staticmethod
    def _update_inspection_status(equipment: Equipment) -> None:
        """장비의 점검 상태를 업데이트하는 내부 메서드"""
        try:
            if equipment.last_inspection_date and equipment.inspection_cycle_days:
                next_date = calculate_next_inspection_date(
                    equipment.last_inspection_date, 
                    equipment.inspection_cycle_days
                )
                equipment.next_inspection_date = next_date
                equipment.inspection_status = get_inspection_status(next_date)
            
            db.session.commit()
        except Exception as e:
            print(f"점검 상태 업데이트 중 오류: {e}")
            db.session.rollback() 