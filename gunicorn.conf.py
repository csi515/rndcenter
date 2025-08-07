"""
Gunicorn 설정 파일
"""
import os
import multiprocessing

# 서버 소켓 설정
bind = f"{os.environ.get('HOST', '0.0.0.0')}:{os.environ.get('PORT', '8002')}"
backlog = 2048

# 워커 프로세스 설정
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# 로깅 설정
accesslog = os.environ.get('LOG_FILE', 'app.log').replace('.log', '_access.log')
errorlog = os.environ.get('LOG_FILE', 'app.log').replace('.log', '_error.log')
loglevel = os.environ.get('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 프로세스 설정
preload_app = True
max_requests = 1000
max_requests_jitter = 50

# 보안 설정
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 환경 변수
raw_env = [
    f"FLASK_ENV={os.environ.get('FLASK_ENV', 'production')}",
    f"DATABASE_URL={os.environ.get('DATABASE_URL', 'sqlite:///app.db')}",
    f"SECRET_KEY={os.environ.get('SECRET_KEY', 'dev-secret-key')}",
    f"LOG_LEVEL={os.environ.get('LOG_LEVEL', 'INFO')}",
    f"LOG_FILE={os.environ.get('LOG_FILE', 'app.log')}",
]

# 기타 설정
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None 