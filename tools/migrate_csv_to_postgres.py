import pandas as pd
from sqlalchemy import create_engine
import os

# 환경에 맞게 DB URL을 수정하세요
DB_URL = 'postgresql+psycopg2://username:password@localhost:5432/your_dbname'
engine = create_engine(DB_URL)

def migrate_project_types():
    csv_path = os.path.join('data', 'project_types.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.rename(columns={'id': 'id', 'project_type': 'project_type'}, inplace=True)
        df.to_sql('project_type', engine, if_exists='append', index=False)
        print('project_types.csv -> project_type 테이블 마이그레이션 완료')
    else:
        print('project_types.csv 파일이 없습니다.')

def migrate_purchase_requests():
    csv_path = os.path.join('data', 'purchase_requests.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # 컬럼명 매핑 필요시 여기에 추가
        df.to_sql('purchase_request', engine, if_exists='append', index=False)
        print('purchase_requests.csv -> purchase_request 테이블 마이그레이션 완료')
    else:
        print('purchase_requests.csv 파일이 없습니다.')

if __name__ == '__main__':
    migrate_project_types()
    migrate_purchase_requests() 