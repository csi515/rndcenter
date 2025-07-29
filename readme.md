# 연구개발(R&D) 센터 관리 시스템

## 개요
이 시스템은 연구개발(R&D) 센터 관리를 위해 설계된 Flask 기반 웹 애플리케이션입니다. 연구 과제, 특허, 장비, 재고, 안전관리, 구매, 커뮤니케이션 등 R&D 환경에서 필요한 다양한 기능을 제공합니다. PostgreSQL 데이터베이스를 사용하여 안정적이고 확장 가능한 데이터 저장을 제공합니다.

## 주요 변경 사항

- 2024년 6월 기준, 모든 데이터 저장은 PostgreSQL 데이터베이스를 사용합니다.
- 기존 CSV/JSON 파일(`data/` 폴더 내)은 더 이상 서비스에서 사용하지 않으며, 백업/이전 데이터 용도로만 보관합니다.
- 데이터 마이그레이션이 필요한 경우 `tools/migrate_csv_to_postgres.py` 스크립트를 사용하세요.
- CSV/JSON 파일을 직접 읽고 쓰는 코드는 모두 삭제 또는 비활성화되었습니다.

## 🚀 Render 배포 가이드

### 1. Render 설정
- **서비스 타입**: Web Service (Flask 애플리케이션)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

### 2. 환경 변수 설정
Render Dashboard에서 다음 환경 변수를 설정하세요:

```bash
# 필수 설정
SESSION_SECRET=your-super-secret-session-key-here

# 선택 설정
FLASK_ENV=production
FLASK_DEBUG=false
LOG_LEVEL=INFO

# 데이터베이스 (선택사항)
# DATABASE_URL=postgresql://username:password@your-db-host:port/dbname
# 설정하지 않으면 SQLite를 사용합니다 (app.db 파일)
```

### 3. 데이터베이스 연결
- **기본**: SQLite 데이터베이스 (app.db 파일) 자동 생성
- **PostgreSQL 사용 시**: `DATABASE_URL` 환경변수 설정
- 데이터베이스 테이블은 자동으로 생성됩니다

### 4. 보안 기능
- **HTTPS 자동 리다이렉트**: HTTP 요청을 HTTPS로 자동 변환
- **보안 헤더**: XSS, CSRF, 클릭재킹 등 공격 방지
- **세션 보안**: 환경변수로 설정 가능한 세션 키
- **정적 파일 캐싱**: 성능 최적화를 위한 캐시 설정

## 시스템 아키텍처

### 프론트엔드 아키텍처
- **템플릿 엔진**: Jinja2 템플릿 + Bootstrap 5 다크 테마
- **UI 프레임워크**: Bootstrap 5, Font Awesome 아이콘
- **자바스크립트 라이브러리**: FullCalendar(일정 관리), 커스텀 JS
- **반응형 디자인**: 모바일 우선, Bootstrap 그리드 시스템

### 백엔드 아키텍처
- **프레임워크**: Flask (파이썬 웹 프레임워크)
- **구조 패턴**: Blueprint 기반 모듈 구조
- **데이터베이스**: SQLite (기본) / PostgreSQL (선택)
- **ORM**: SQLAlchemy를 통한 객체 관계 매핑
- **세션 관리**: 환경변수로 설정 가능한 Flask 세션
- **에러 처리**: Flash 메시지로 사용자 피드백
- **로깅**: Python logging 모듈 활용

### 데이터 저장
- **기본 저장소**: SQLite 데이터베이스 (app.db)
- **PostgreSQL**: 환경변수 설정 시 사용
- **ORM**: SQLAlchemy를 통한 객체 관계 매핑
- **마이그레이션**: CSV에서 데이터베이스로 데이터 이전 지원
- **백업**: 기존 CSV 파일은 백업용으로 보관

## 주요 구성 요소

### 1. 애플리케이션 코어(`app.py`)
- Flask 앱 초기화 및 모델 정의
- Blueprint 등록을 통한 모듈별 라우팅
- 보안 헤더 및 HTTPS 리다이렉트 설정
- 데이터베이스 연결 및 테이블 생성

### 2. 데이터베이스 모델
- **Project**: 연구 과제 관리
- **Researcher**: 연구원 정보 관리
- **Equipment**: 장비 관리 및 예약
- **PurchaseRequest**: 구매 요청 관리
- **CoalTarPitchLog**: 콜타르피치 휘발물 사용일지
- 기타 필요한 모델들

### 3. 라우트 모듈
- **대시보드**(`routes/dashboard.py`): 통계 및 최근 활동
- **연구과제**(`routes/research.py`): 과제 및 연구원 관리
- **특허**(`routes/patents.py`): 지적재산권 관리
- **장비**(`routes/equipment.py`): 장비 관리 및 예약
- **재고**(`routes/inventory.py`): 재고 관리
- **안전**(`routes/safety.py`): 사고 보고 및 안전관리
- **구매**(`routes/purchasing.py`): 구매 요청 관리
- **커뮤니케이션**(`routes/communication.py`): 내부 소통 및 Q&A
- **외부**(`routes/external.py`): 연락처 관리
- **화학물질**(`routes/chemical.py`): MSDS 및 화학물질 관리
- **콜타르피치**(`routes/coal_tar_pitch_log.py`): 휘발물 사용일지

### 4. 프론트엔드 구성
- **기본 템플릿**: 사이드바 네비게이션 포함 일관된 레이아웃
- **반응형 테이블**: 검색/필터 기능이 있는 데이터 테이블
- **모달 폼**: Bootstrap 모달을 활용한 데이터 입력
- **캘린더 연동**: FullCalendar로 일정 관리
- **인터랙티브 요소**: 자바스크립트로 사용자 경험 강화

## 보안 기능

### 1. HTTP 보안 헤더
- **X-Content-Type-Options**: MIME 타입 스니핑 방지
- **X-Frame-Options**: 클릭재킹 공격 방지
- **X-XSS-Protection**: XSS 공격 방지
- **Strict-Transport-Security**: HTTPS 강제 사용
- **Content-Security-Policy**: 리소스 로딩 제한
- **Referrer-Policy**: 리퍼러 정보 제어

### 2. 캐시 제어
- **정적 파일**: 1년간 캐시 (성능 최적화)
- **동적 페이지**: 캐시 비활성화 (보안)

### 3. HTTPS 리다이렉트
- HTTP 요청을 HTTPS로 자동 변환
- 보안 연결 강제 적용

## 외부 의존성

### 파이썬 패키지
- **Flask**: 웹 프레임워크
- **Flask-SQLAlchemy**: ORM
- **gunicorn**: WSGI 서버
- **python-dotenv**: 환경변수 관리
- **openpyxl**: Excel 파일 처리

### 프론트엔드 라이브러리
- **Bootstrap 5**: 다크 테마 UI 프레임워크
- **Font Awesome 6**: 아이콘 라이브러리
- **FullCalendar 6**: 캘린더/일정 관리
- **jQuery**: Bootstrap에서 암시적으로 사용

## 로컬 개발 환경 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
cp env.example .env
# .env 파일을 편집하여 실제 값으로 설정
```

### 3. 데이터베이스 설정
```bash
# PostgreSQL 데이터베이스 생성 및 연결 설정
# DATABASE_URL 환경변수 설정
```

### 4. 애플리케이션 실행
```bash
python app.py
```

## 문제 해결

### 일반적인 문제들
1. **데이터베이스 연결 오류**: `DATABASE_URL` 환경변수 확인
2. **모듈 import 오류**: `pip install -r requirements.txt` 재실행
3. **권한 오류**: 파일 권한 및 데이터베이스 사용자 권한 확인

### 로그 확인
- 애플리케이션 로그: `app.log` 파일
- Render 로그: Render Dashboard에서 확인 