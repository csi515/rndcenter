#!/bin/bash

# 연구관리시스템 가동계 배포 스크립트

set -e  # 오류 발생 시 스크립트 중단

echo "=== 연구관리시스템 가동계 배포 시작 ==="

# 1. 환경 변수 파일 확인
if [ ! -f ".env" ]; then
    echo "오류: .env 파일이 없습니다. env.production을 .env로 복사하세요."
    exit 1
fi

# 2. Python 가상환경 확인 및 활성화
if [ ! -d "venv" ]; then
    echo "Python 가상환경을 생성합니다..."
    python3 -m venv venv
fi

echo "가상환경을 활성화합니다..."
source venv/bin/activate

# 3. 의존성 설치
echo "의존성을 설치합니다..."
pip install -r requirements.txt

# 4. 로그 디렉토리 생성
echo "로그 디렉토리를 생성합니다..."
sudo mkdir -p /var/log/research_management
sudo chown $USER:$USER /var/log/research_management

# 5. PostgreSQL 데이터베이스 설정 확인
echo "PostgreSQL 데이터베이스 연결을 확인합니다..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine
try:
    engine = create_engine(os.environ.get('DATABASE_URL'))
    engine.connect()
    print('PostgreSQL 연결 성공')
except Exception as e:
    print(f'PostgreSQL 연결 실패: {e}')
    exit(1)
"

# 6. 데이터베이스 마이그레이션
echo "데이터베이스 마이그레이션을 실행합니다..."
python migrate_to_postgresql.py

# 7. 애플리케이션 테스트
echo "애플리케이션을 테스트합니다..."
python -c "
from app import app
with app.app_context():
    print('애플리케이션 테스트 성공')
"

# 8. Gunicorn 서비스 파일 생성
echo "Gunicorn 서비스 파일을 생성합니다..."
sudo tee /etc/systemd/system/research-management.service > /dev/null <<EOF
[Unit]
Description=Research Management System
After=network.target

[Service]
Type=notify
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# 9. 서비스 등록 및 시작
echo "서비스를 등록하고 시작합니다..."
sudo systemctl daemon-reload
sudo systemctl enable research-management
sudo systemctl start research-management

# 10. 서비스 상태 확인
echo "서비스 상태를 확인합니다..."
sudo systemctl status research-management

echo "=== 배포 완료 ==="
echo "서비스 URL: http://$(hostname -I | awk '{print $1}'):8002"
echo "로그 파일: /var/log/research_management/"
echo ""
echo "서비스 관리 명령어:"
echo "  상태 확인: sudo systemctl status research-management"
echo "  서비스 시작: sudo systemctl start research-management"
echo "  서비스 중지: sudo systemctl stop research-management"
echo "  서비스 재시작: sudo systemctl restart research-management"
echo "  로그 확인: sudo journalctl -u research-management -f" 