"""
날짜 관련 공통 유틸리티 함수들
"""
from datetime import datetime, date, timedelta
from typing import Optional, Union


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """문자열을 date 객체로 변환하는 헬퍼 함수"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_datetime(datetime_str: Optional[str]) -> Optional[datetime]:
    """문자열을 datetime 객체로 변환하는 헬퍼 함수"""
    if not datetime_str:
        return None
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(datetime_str, "%Y-%m-%d")
        except ValueError:
            return None


def format_date(date_obj: Optional[Union[date, datetime]]) -> str:
    """date/datetime 객체를 문자열로 변환"""
    if not date_obj:
        return ''
    if isinstance(date_obj, datetime):
        return date_obj.date().strftime('%Y-%m-%d')
    return date_obj.strftime('%Y-%m-%d')


def format_datetime(datetime_obj: Optional[datetime]) -> str:
    """datetime 객체를 문자열로 변환"""
    if not datetime_obj:
        return ''
    return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')


def calculate_next_inspection_date(last_inspection_date: date, cycle_days: int) -> date:
    """마지막 점검일과 점검 주기로 다음 점검일 계산"""
    return last_inspection_date + timedelta(days=cycle_days)


def get_inspection_status(next_inspection_date: date) -> str:
    """다음 점검일을 기준으로 점검 상태 반환"""
    today = date.today()
    
    if next_inspection_date < today:
        return '점검지연'
    elif next_inspection_date - today <= timedelta(days=30):
        return '점검필요'
    else:
        return '정상'


def generate_equipment_id() -> str:
    """장비 ID 자동 생성"""
    return 'EQ' + datetime.now().strftime('%Y%m%d%H%M%S') 