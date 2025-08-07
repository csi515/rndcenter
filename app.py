import os
import logging
from flask import Flask, redirect, request
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Create the app
app = Flask(__name__)

# 환경 설정
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-for-rd-center")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# 로깅 설정
from utils.logger import setup_logger, log_request_info, log_error_info
setup_logger(app)
log_request_info(app)
log_error_info(app)

# Security and performance headers
@app.after_request
def add_security_headers(response):
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' data: https://cdnjs.cloudflare.com;"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Cache control for static assets
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year for static assets
    else:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    return response

# HTTPS redirect (for production)
@app.before_request
def https_redirect():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///app.db"  # Use SQLite as fallback
)

# PostgreSQL인 경우에만 연결 풀 설정 적용
if app.config["SQLALCHEMY_DATABASE_URI"].startswith('postgresql'):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }
else:
    # SQLite인 경우 기본 설정만 적용
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Import database and models
from database import db, Project, Researcher, Equipment, Reservation, UsageLog, Week, WeeklyScheduleNew, Patent, SafetyMaterial, Accident, AccidentDocument, SafetyProcedure, Contact, Communication, Chemical

db.init_app(app)

# Create tables
with app.app_context():
    try:
        db.create_all()
        app.logger.info("데이터베이스 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        app.logger.error(f"데이터베이스 테이블 생성 중 오류: {str(e)}")

# Import and register blueprints
from routes.dashboard import dashboard_bp
from routes.research import research_bp
from routes.patents import patents_bp
from routes.equipment_pages import equipment_pages_bp
from routes.equipment_api import equipment_api_bp
from routes.equipment import equipment_bp
from routes.equipment_inspection import equipment_inspection_bp
from routes.safety import safety_bp
from routes.communication import communication_bp
from routes.external import external_bp
from routes.chemical import chemical_bp

app.register_blueprint(dashboard_bp, url_prefix='/')
app.register_blueprint(research_bp, url_prefix='/research')
app.register_blueprint(patents_bp, url_prefix='/patents')
app.register_blueprint(equipment_pages_bp, url_prefix='/equipment')
app.register_blueprint(equipment_api_bp, url_prefix='/equipment')
app.register_blueprint(equipment_bp, url_prefix='/equipment')
app.register_blueprint(equipment_inspection_bp, url_prefix='/equipment')
app.register_blueprint(safety_bp, url_prefix='/safety')
app.register_blueprint(communication_bp, url_prefix='/communication')
app.register_blueprint(external_bp, url_prefix='/external')
app.register_blueprint(chemical_bp, url_prefix='/chemical')

if __name__ == '__main__':
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 8002))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    app.logger.info(f"애플리케이션이 시작됩니다. 호스트: {host}, 포트: {port}, 디버그: {debug}")
    app.run(host=host, port=port, debug=debug)
