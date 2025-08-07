# 연구관리시스템 가동계 배포 가이드

## 사전 요구사항

### 1. 시스템 요구사항
- Ubuntu 20.04 LTS 이상
- Python 3.8 이상
- PostgreSQL 12 이상
- Nginx (선택사항, 리버스 프록시용)

### 2. PostgreSQL 설치 및 설정

```bash
# PostgreSQL 설치
sudo apt update
sudo apt install postgresql postgresql-contrib

# PostgreSQL 서비스 시작
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 데이터베이스 및 사용자 생성
sudo -u postgres psql

CREATE DATABASE research_management;
CREATE USER research_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE research_management TO research_user;
\q
```

## 배포 단계

### 1. 프로젝트 클론 및 설정

```bash
# 프로젝트 디렉토리로 이동
cd /opt/research-management

# 환경 변수 파일 설정
cp env.production .env
nano .env  # 데이터베이스 정보 수정
```

### 2. 환경 변수 설정

`.env` 파일에서 다음 항목들을 수정하세요:

```env
# 데이터베이스 설정
DATABASE_URL=postgresql://research_user:your_secure_password@localhost:5432/research_management

# Flask 설정
SECRET_KEY=your-production-secret-key-here
FLASK_ENV=production
DEBUG=False

# 로깅 설정
LOG_LEVEL=INFO
LOG_FILE=/var/log/research_management/app.log

# 서버 설정
HOST=0.0.0.0
PORT=8002
```

### 3. 배포 스크립트 실행

```bash
# 배포 스크립트 실행 권한 부여
chmod +x deploy.sh

# 배포 실행
./deploy.sh
```

### 4. 수동 배포 (스크립트 사용 불가 시)

```bash
# 1. Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 로그 디렉토리 생성
sudo mkdir -p /var/log/research_management
sudo chown $USER:$USER /var/log/research_management

# 4. 데이터베이스 마이그레이션
python migrate_to_postgresql.py

# 5. Gunicorn으로 서비스 시작
gunicorn -c gunicorn.conf.py app:app
```

## 서비스 관리

### 서비스 상태 확인
```bash
sudo systemctl status research-management
```

### 서비스 시작/중지/재시작
```bash
sudo systemctl start research-management
sudo systemctl stop research-management
sudo systemctl restart research-management
```

### 로그 확인
```bash
# 시스템 서비스 로그
sudo journalctl -u research-management -f

# 애플리케이션 로그
tail -f /var/log/research_management/app.log

# 접근 로그
tail -f /var/log/research_management/app_access.log

# 에러 로그
tail -f /var/log/research_management/app_error.log
```

## Nginx 설정 (선택사항)

### Nginx 설치
```bash
sudo apt install nginx
```

### Nginx 설정 파일 생성
```bash
sudo nano /etc/nginx/sites-available/research-management
```

설정 내용:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/research-management/static;
        expires 30d;
    }
}
```

### Nginx 활성화
```bash
sudo ln -s /etc/nginx/sites-available/research-management /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 보안 설정

### 1. 방화벽 설정
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. SSL 인증서 설정 (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 모니터링

### 1. 시스템 리소스 모니터링
```bash
# CPU 및 메모리 사용량
htop

# 디스크 사용량
df -h

# 네트워크 연결
netstat -tulpn
```

### 2. 애플리케이션 모니터링
```bash
# 프로세스 확인
ps aux | grep gunicorn

# 포트 사용량 확인
sudo lsof -i :8002
```

## 백업 및 복구

### 1. 데이터베이스 백업
```bash
# PostgreSQL 백업
pg_dump -U research_user -h localhost research_management > backup_$(date +%Y%m%d_%H%M%S).sql

# 자동 백업 스크립트 생성
sudo crontab -e
# 매일 새벽 2시에 백업
0 2 * * * pg_dump -U research_user -h localhost research_management > /backup/db_backup_$(date +\%Y\%m\%d).sql
```

### 2. 로그 파일 관리
```bash
# 로그 로테이션 설정
sudo nano /etc/logrotate.d/research-management

/var/log/research_management/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
```

## 문제 해결

### 1. 서비스 시작 실패
```bash
# 서비스 상태 확인
sudo systemctl status research-management

# 로그 확인
sudo journalctl -u research-management -n 50
```

### 2. 데이터베이스 연결 오류
```bash
# PostgreSQL 서비스 상태 확인
sudo systemctl status postgresql

# 데이터베이스 연결 테스트
psql -U research_user -h localhost -d research_management
```

### 3. 포트 충돌
```bash
# 포트 사용 확인
sudo lsof -i :8002

# 프로세스 종료
sudo kill -9 <PID>
```

## 업데이트

### 1. 코드 업데이트
```bash
# 코드 업데이트
git pull origin main

# 의존성 업데이트
source venv/bin/activate
pip install -r requirements.txt

# 서비스 재시작
sudo systemctl restart research-management
```

### 2. 데이터베이스 마이그레이션
```bash
python migrate_to_postgresql.py
```

## 연락처

문제가 발생하면 다음 정보와 함께 문의하세요:
- 오류 메시지
- 로그 파일 내용
- 시스템 정보 (OS 버전, Python 버전 등) 