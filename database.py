from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def ensure_project_participants_column():
    """participants 컬럼이 없으면 자동으로 추가 (PostgreSQL, SQLite 지원)"""
    from sqlalchemy import inspect, text
    engine = db.get_engine()
    insp = inspect(engine)
    columns = [col['name'] for col in insp.get_columns('projects')]
    if 'participants' not in columns:
        with engine.connect() as conn:
            # DB 종류에 따라 쿼리 분기
            if engine.dialect.name == 'postgresql':
                conn.execute(text('ALTER TABLE projects ADD COLUMN participants TEXT'))
            elif engine.dialect.name == 'sqlite':
                conn.execute(text('ALTER TABLE projects ADD COLUMN participants TEXT'))
            # 필요시 다른 DBMS도 추가

def init_db(app):
    """Initialize database with app context"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        try:
            ensure_project_participants_column()
        except Exception as e:
            print(f"Warning: Could not ensure project_participants column: {e}")

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    leader = db.Column(db.String(100))
    department = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Numeric(15, 2))
    status = db.Column(db.String(50), default='진행중')
    progress = db.Column(db.Integer, default=0)
    participants = db.Column(db.Text)  # 추가: 참여자 정보
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Researcher(db.Model):
    __tablename__ = 'researchers'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    specialization = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    hire_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='재직')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    researcher_name = db.Column(db.String(100))
    project_name = db.Column(db.String(200))
    task = db.Column(db.String(500), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    status = db.Column(db.String(50), default='예정')
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class WeeklySchedule(db.Model):
    __tablename__ = 'weekly_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.String(100), unique=True, nullable=False)
    week = db.Column(db.Integer, nullable=False)  # 1-5 for week number
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    task = db.Column(db.String(500), nullable=False)
    researcher = db.Column(db.String(100))
    project = db.Column(db.String(200))
    priority = db.Column(db.String(50), default='보통')
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Patent(db.Model):
    __tablename__ = 'patents'
    
    id = db.Column(db.Integer, primary_key=True)
    patent_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    inventors = db.Column(db.Text)
    applicant = db.Column(db.String(200))
    application_date = db.Column(db.Date)
    application_number = db.Column(db.String(100))
    publication_date = db.Column(db.Date)
    publication_number = db.Column(db.String(100))
    grant_date = db.Column(db.Date)
    patent_number = db.Column(db.String(100))
    registration_number = db.Column(db.String(100))  # 등록번호 추가
    registration_date = db.Column(db.Date)  # 등록일 추가
    status = db.Column(db.String(50))
    field = db.Column(db.String(200))
    abstract = db.Column(db.Text)
    claims = db.Column(db.Text)
    priority_date = db.Column(db.Date)
    priority_number = db.Column(db.String(100))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

# 특허 출원인 테이블
class PatentApplicant(db.Model):
    __tablename__ = 'patent_applicants'
    
    id = db.Column(db.Integer, primary_key=True)
    patent_id = db.Column(db.Integer, db.ForeignKey('patents.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    affiliation = db.Column(db.String(200))  # 소속 (선택)
    share_percentage = db.Column(db.Numeric(5, 2), nullable=False)  # 지분율 (%)
    filing_reward = db.Column(db.Numeric(15, 2), default=0)  # 출원 보상금
    registration_reward = db.Column(db.Numeric(15, 2), default=0)  # 등록 보상금
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    patent = db.relationship('Patent', backref='applicants')

class Equipment(db.Model):
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    manufacturer = db.Column(db.String(200))
    model = db.Column(db.String(200))
    serial_number = db.Column(db.String(200))
    location = db.Column(db.String(200))
    purchase_date = db.Column(db.Date)
    purchase_price = db.Column(db.Numeric(15, 2))
    status = db.Column(db.String(50), default='사용가능')
    manager = db.Column(db.String(100))
    maintenance_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    specifications = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_name = db.Column(db.String(200), nullable=False)
    reserver = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(500))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    status = db.Column(db.String(50), default='예약')
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class UsageLog(db.Model):
    __tablename__ = 'usage_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_name = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(100), nullable=False)
    usage_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    purpose = db.Column(db.String(500))
    notes = db.Column(db.Text)
    condition_before = db.Column(db.String(200))
    condition_after = db.Column(db.String(200))
    issues = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class InventoryItem(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    location = db.Column(db.String(200))
    quantity = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(50))
    min_quantity = db.Column(db.Integer, default=0)
    supplier = db.Column(db.String(200))
    unit_price = db.Column(db.Numeric(10, 2))
    purchase_date = db.Column(db.Date)  # 추가
    expiry_date = db.Column(db.Date)
    lot_number = db.Column(db.String(100))
    storage_condition = db.Column(db.String(200))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class PurchaseRequest(db.Model):
    __tablename__ = 'purchase_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(50), unique=True, nullable=False)
    requester = db.Column(db.String(100), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2))
    total_price = db.Column(db.Numeric(15, 2))
    supplier = db.Column(db.String(200))
    category = db.Column(db.String(100))
    urgency = db.Column(db.String(50))
    reason = db.Column(db.Text)
    budget_code = db.Column(db.String(100))
    status = db.Column(db.String(50), default='요청')
    request_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class Communication(db.Model):
    __tablename__ = 'communications'
    
    id = db.Column(db.Integer, primary_key=True)
    comm_id = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text)
    author = db.Column(db.String(100))
    views = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='공개')
    question_type = db.Column(db.String(100))
    urgency = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    answer = db.Column(db.Text)

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(200))
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(200))
    address = db.Column(db.Text)
    category = db.Column(db.String(100))
    relationship = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class Chemical(db.Model):
    __tablename__ = 'chemicals'
    
    id = db.Column(db.Integer, primary_key=True)
    chem_id = db.Column(db.String(50), unique=True, nullable=False)
    chemical_name = db.Column(db.String(200), nullable=False)
    cas_number = db.Column(db.String(50))
    manufacturer = db.Column(db.String(200))
    hazard_class = db.Column(db.String(50))
    storage_condition = db.Column(db.String(200))
    flash_point = db.Column(db.String(50))
    exposure_limit = db.Column(db.String(100))
    first_aid = db.Column(db.Text)
    disposal_method = db.Column(db.Text)
    msds_file_link = db.Column(db.String(500))
    location = db.Column(db.String(200))
    quantity = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class Accident(db.Model):
    __tablename__ = 'accidents'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200))
    involved_person = db.Column(db.String(100))
    incident_type = db.Column(db.String(100))
    severity = db.Column(db.String(50))
    description = db.Column(db.Text)
    immediate_action = db.Column(db.Text)
    follow_up = db.Column(db.Text)
    prevention = db.Column(db.Text)
    reporter = db.Column(db.String(100))
    status = db.Column(db.String(50), default='조사중')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)


class AccidentDocument(db.Model):
    __tablename__ = 'accident_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    accident_id = db.Column(db.Integer, db.ForeignKey('accidents.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(1000), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    accident = db.relationship('Accident', backref='documents')

class SafetyEducation(db.Model):
    __tablename__ = 'safety_education'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    trainer = db.Column(db.String(100))
    participants = db.Column(db.Text)
    education_date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.String(50))
    location = db.Column(db.String(200))
    materials = db.Column(db.Text)
    status = db.Column(db.String(50), default='계획')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class SafetyProcedure(db.Model):
    __tablename__ = 'safety_procedures'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    steps = db.Column(db.Text)
    responsible_person = db.Column(db.String(100))
    review_date = db.Column(db.Date)
    version = db.Column(db.String(20), default='1.0')
    status = db.Column(db.String(50), default='유효')
    procedure_link = db.Column(db.String(1000))  # 절차서 링크
    risk_assessment_link = db.Column(db.String(1000))  # 위험성평가 링크
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class ProjectSchedule(db.Model):
    __tablename__ = 'project_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(50), db.ForeignKey('projects.project_id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    start_week = db.Column(db.Integer, nullable=False)
    end_week = db.Column(db.Integer, nullable=False)
    start_month = db.Column(db.Integer, nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    researcher_ids = db.Column(db.Text)  # JSON string of researcher IDs
    memo = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with Project
    project = db.relationship('Project', backref='schedules')

# 주차 테이블
class Week(db.Model):
    __tablename__ = 'weeks'
    
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)
    week_number = db.Column(db.Integer, nullable=False)  # 1-5
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 새로운 주간 일정 테이블
class WeeklyScheduleNew(db.Model):
    __tablename__ = 'weekly_schedule_new'
    
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200), nullable=False)
    researcher_name = db.Column(db.String(100))
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    start_week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)
    end_week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)
    status = db.Column(db.String(50), default='계획')
    priority = db.Column(db.String(50), default='보통')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    week = db.relationship('Week', foreign_keys=[week_id], backref='schedules')
    start_week = db.relationship('Week', foreign_keys=[start_week_id])
    end_week = db.relationship('Week', foreign_keys=[end_week_id])


class SafetyMaterial(db.Model):
    __tablename__ = 'safety_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(1000))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProjectType(db.Model):
    __tablename__ = 'project_types'
    id = db.Column(db.String(50), primary_key=True)
    project_type = db.Column(db.String(200), unique=True, nullable=False)

class InventoryTransaction(db.Model):
    __tablename__ = 'inventory_transactions'
    id = db.Column(db.String(50), primary_key=True)
    item_id = db.Column(db.String(50), db.ForeignKey('inventory.item_id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    transaction_type = db.Column(db.String(50))  # 입고/출고
    quantity = db.Column(db.Integer)
    before_quantity = db.Column(db.Integer)
    after_quantity = db.Column(db.Integer)
    user = db.Column(db.String(100))
    notes = db.Column(db.Text)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

class CoalTarPitchLog(db.Model):
    __tablename__ = 'coal_tar_pitch_logs'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)  # 사용자(작업자 이름)
    material = db.Column(db.String(100), default='콜타르피치 휘발물', nullable=False)  # 사용 물질
    used_at = db.Column(db.DateTime, nullable=False)  # 사용 일시
    location = db.Column(db.String(200))  # 작업 장소
    work_content = db.Column(db.String(200))  # 작업 내용
    amount = db.Column(db.String(100))  # 사용량(단위 포함)
    ppe = db.Column(db.Boolean, default=False)  # 보호구 착용 여부
    process_condition = db.Column(db.String(200))  # 공정 조건
    exposure_reaction = db.Column(db.String(200))  # 유해 노출 반응
    action_note = db.Column(db.String(200))  # 조치 및 비고
    writer = db.Column(db.String(100))  # 작성자
    manager_sign = db.Column(db.String(100))  # 관리자 서명
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)