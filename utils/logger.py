"""
로깅 설정 유틸리티
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask import request

def setup_logger(app):
    """애플리케이션 로거 설정"""
    
    # 로그 레벨 설정
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    log_file = os.environ.get('LOG_FILE', 'app.log')
    
    # 로그 디렉토리 생성
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 로그 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 파일 핸들러 설정 (일별 로테이션, 최대 30일 보관)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(formatter)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(formatter)
    
    # 애플리케이션 로거 설정
    app.logger.setLevel(getattr(logging, log_level))
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    # Werkzeug 로거 설정 (Flask 내부 로그)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(getattr(logging, log_level))
    werkzeug_logger.addHandler(file_handler)
    werkzeug_logger.addHandler(console_handler)
    
    # SQLAlchemy 로거 설정
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.setLevel(logging.WARNING)  # SQL 쿼리는 WARNING 레벨로만 로그
    sqlalchemy_logger.addHandler(file_handler)
    
    app.logger.info(f'로거가 설정되었습니다. 로그 레벨: {log_level}, 로그 파일: {log_file}')

def log_request_info(app):
    """요청 정보 로깅 미들웨어"""
    @app.before_request
    def log_request():
        app.logger.info(f'요청: {request.method} {request.url} - IP: {request.remote_addr}')
    
    @app.after_request
    def log_response(response):
        app.logger.info(f'응답: {response.status_code} - {request.method} {request.url}')
        return response

def log_error_info(app):
    """에러 로깅 미들웨어"""
    @app.errorhandler(Exception)
    def log_exception(error):
        app.logger.error(f'예외 발생: {str(error)}', exc_info=True)
        return "서버 내부 오류가 발생했습니다.", 500 