import csv
import os
from sqlalchemy import create_engine
from database import db, ProjectType, PurchaseRequest
from datetime import datetime

# 데이터베이스 연결 설정 (실제 값으로 변경 필요)
DB_URL = 'postgresql+psycopg2://username:password@localhost:5432/your_dbname'
engine = create_engine(DB_URL)

def migrate_project_types():
    csv_path = os.path.join('data', 'project_types.csv')
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                project_type = ProjectType(
                    id=int(row['id']),
                    project_type=row['project_type']
                )
                db.session.add(project_type)
        db.session.commit()
        print('project_types.csv -> project_type 테이블 마이그레이션 완료')
    else:
        print('project_types.csv 파일이 없습니다.')

def migrate_purchase_requests():
    csv_path = os.path.join('data', 'purchase_requests.csv')
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                purchase_request = PurchaseRequest(
                    request_id=row['id'],
                    item_name=row.get('item', ''),
                    quantity=float(row.get('required_qty', 0)),
                    unit_price=float(row.get('unit_price', 0)),
                    total_price=float(row.get('total_price', 0)),
                    status=row.get('purchase_status', '대기'),
                    requester=row.get('requester', ''),
                    request_date=datetime.strptime(row.get('request_date', '2024-01-01'), '%Y-%m-%d') if row.get('request_date') else datetime.now(),
                    notes=row.get('note', ''),
                    reason=row.get('reason', ''),
                    spec=row.get('spec', ''),
                    item_number=row.get('item_number', ''),
                    unit=row.get('unit', ''),
                    project_type=row.get('project_type', ''),
                    safety_stock=float(row.get('safety_stock', 0))
                )
                db.session.add(purchase_request)
        db.session.commit()
        print('purchase_requests.csv -> purchase_request 테이블 마이그레이션 완료')
    else:
        print('purchase_requests.csv 파일이 없습니다.')

if __name__ == '__main__':
    migrate_project_types()
    migrate_purchase_requests() 