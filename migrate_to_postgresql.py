#!/usr/bin/env python3
"""
SQLite에서 PostgreSQL로 데이터 마이그레이션 스크립트
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def migrate_data():
    """SQLite에서 PostgreSQL로 데이터 마이그레이션"""
    
    # SQLite 데이터베이스 연결 (기존 데이터)
    sqlite_url = "sqlite:///app.db"
    
    # PostgreSQL 데이터베이스 연결 (새 데이터)
    postgres_url = os.environ.get('DATABASE_URL')
    
    if not postgres_url:
        print("DATABASE_URL 환경 변수가 설정되지 않았습니다.")
        return
    
    print(f"마이그레이션 시작: {sqlite_url} -> {postgres_url}")
    
    try:
        # SQLite에서 데이터 읽기
        from sqlalchemy import create_engine, text
        from database import db, Project, Researcher, Equipment, Reservation, UsageLog, Week, WeeklyScheduleNew, Patent, SafetyMaterial, Accident, AccidentDocument, SafetyProcedure, Contact, Communication, Chemical
        
        # SQLite 엔진 생성
        sqlite_engine = create_engine(sqlite_url)
        
        # PostgreSQL 엔진 생성
        postgres_engine = create_engine(postgres_url)
        
        # 테이블 목록
        tables = [
            ('projects', Project),
            ('researchers', Researcher),
            ('equipment', Equipment),
            ('reservations', Reservation),
            ('usage_logs', UsageLog),
            ('weeks', Week),
            ('weekly_schedule_new', WeeklyScheduleNew),
            ('patents', Patent),
            ('safety_materials', SafetyMaterial),
            ('accidents', Accident),
            ('accident_documents', AccidentDocument),
            ('safety_procedures', SafetyProcedure),
            ('contacts', Contact),
            ('communications', Communication),
            ('chemicals', Chemical)
        ]
        
        total_migrated = 0
        
        for table_name, model in tables:
            try:
                # SQLite에서 데이터 읽기
                with sqlite_engine.connect() as conn:
                    result = conn.execute(text(f"SELECT * FROM {table_name}"))
                    rows = result.fetchall()
                
                if rows:
                    print(f"{table_name}: {len(rows)}개 레코드 발견")
                    
                    # PostgreSQL에 데이터 삽입
                    with postgres_engine.connect() as conn:
                        for row in rows:
                            # 딕셔너리로 변환
                            row_dict = dict(row._mapping)
                            
                            # 모델 인스턴스 생성 및 저장
                            try:
                                # 기존 ID가 있으면 제거 (자동 생성)
                                if 'id' in row_dict:
                                    del row_dict['id']
                                
                                # 모델에 맞는 데이터만 필터링
                                valid_fields = {k: v for k, v in row_dict.items() 
                                              if hasattr(model, k) and v is not None}
                                
                                if valid_fields:
                                    # 모델 인스턴스 생성
                                    instance = model(**valid_fields)
                                    db.session.add(instance)
                                
                            except Exception as e:
                                print(f"  레코드 삽입 오류: {e}")
                                continue
                        
                        db.session.commit()
                        print(f"  {len(rows)}개 레코드 마이그레이션 완료")
                        total_migrated += len(rows)
                else:
                    print(f"{table_name}: 데이터 없음")
                    
            except Exception as e:
                print(f"{table_name} 마이그레이션 오류: {e}")
                continue
        
        print(f"\n마이그레이션 완료! 총 {total_migrated}개 레코드가 마이그레이션되었습니다.")
        
    except Exception as e:
        print(f"마이그레이션 중 오류 발생: {e}")

def create_postgresql_tables():
    """PostgreSQL에 테이블 생성"""
    try:
        from app import app
        from database import db
        
        with app.app_context():
            db.create_all()
            print("PostgreSQL 테이블이 성공적으로 생성되었습니다.")
            
    except Exception as e:
        print(f"테이블 생성 중 오류: {e}")

if __name__ == '__main__':
    print("=== PostgreSQL 마이그레이션 도구 ===")
    print("1. PostgreSQL 테이블 생성")
    print("2. SQLite에서 PostgreSQL로 데이터 마이그레이션")
    
    choice = input("선택하세요 (1 또는 2): ").strip()
    
    if choice == '1':
        create_postgresql_tables()
    elif choice == '2':
        migrate_data()
    else:
        print("잘못된 선택입니다.") 