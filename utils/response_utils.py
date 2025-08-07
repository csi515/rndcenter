"""
API 응답 관련 공통 유틸리티 함수들
"""
from flask import jsonify
from typing import Any, Dict, Optional


def success_response(data: Any = None, message: str = "성공") -> Dict:
    """성공 응답 생성"""
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return response


def error_response(error: str, status_code: int = 400) -> Dict:
    """에러 응답 생성"""
    return {
        'success': False,
        'error': error
    }, status_code


def json_success_response(data: Any = None, message: str = "성공"):
    """JSON 성공 응답"""
    return jsonify(success_response(data, message))


def json_error_response(error: str, status_code: int = 400):
    """JSON 에러 응답"""
    return jsonify(error_response(error, status_code)[0]), status_code


def validate_required_fields(data: Dict, required_fields: list) -> Optional[str]:
    """필수 필드 검증"""
    for field in required_fields:
        if not data.get(field):
            return f"{field}는 필수 입력 항목입니다."
    return None 