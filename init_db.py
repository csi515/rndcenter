from app import app, db
from database import *

def init_database():
    with app.app_context():
        # 데이터베이스 테이블 생성
        db.create_all()
        print("데이터베이스 테이블이 성공적으로 생성되었습니다.")

if __name__ == '__main__':
    init_database() 