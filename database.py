import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create database instance
db = SQLAlchemy()

# Define all models
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
    budget = db.Column(db.Float)
    status = db.Column(db.String(50), default='진행중')
    progress = db.Column(db.Integer, default=0)
    participants = db.Column(db.Text)
    # 분기별 보고서 링크
    q1_report_link = db.Column(db.String(500))
    q2_report_link = db.Column(db.String(500))
    q3_report_link = db.Column(db.String(500))
    q4_report_link = db.Column(db.String(500))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Researcher(db.Model):
    __tablename__ = 'researchers'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    specialization = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    hire_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='재직')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

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
    purchase_price = db.Column(db.Float)
    status = db.Column(db.String(50), default='사용가능')
    manager = db.Column(db.String(100))
    maintenance_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    # 점검 주기 관련 필드 추가
    inspection_cycle_days = db.Column(db.Integer, default=365)  # 점검 주기 (일)
    last_inspection_date = db.Column(db.Date)  # 마지막 점검일
    next_inspection_date = db.Column(db.Date)  # 다음 점검 예정일
    inspection_status = db.Column(db.String(50), default='정상')  # 점검 상태 (정상, 점검필요, 점검지연)
    specifications = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class EquipmentInspection(db.Model):
    __tablename__ = 'equipment_inspections'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    inspection_date = db.Column(db.Date, nullable=False)
    inspector = db.Column(db.String(100), nullable=False)
    inspection_type = db.Column(db.String(50), default='정기점검')  # 정기점검, 수리후점검, 특별점검
    result = db.Column(db.String(50), default='정상')  # 정상, 이상발견, 수리필요
    condition_before = db.Column(db.String(200))  # 점검 전 상태
    condition_after = db.Column(db.String(200))   # 점검 후 상태
    findings = db.Column(db.Text)  # 발견사항
    actions_taken = db.Column(db.Text)  # 조치사항
    next_inspection_date = db.Column(db.Date)  # 다음 점검 예정일
    notes = db.Column(db.Text)  # 기타 메모
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    equipment = db.relationship('Equipment', backref='inspections')

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

class ProjectType(db.Model):
    __tablename__ = 'project_types'
    id = db.Column(db.String(50), primary_key=True)
    project_type = db.Column(db.String(200), nullable=False)



# Additional models from routes
class Week(db.Model):
    __tablename__ = 'weeks'
    
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    
    week = db.relationship('Week', foreign_keys=[week_id], backref='schedules')
    start_week = db.relationship('Week', foreign_keys=[start_week_id])
    end_week = db.relationship('Week', foreign_keys=[end_week_id])

class Patent(db.Model):
    __tablename__ = 'patents'
    
    id = db.Column(db.Integer, primary_key=True)
    patent_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    inventors = db.Column(db.String(200))
    application_number = db.Column(db.String(100))
    registration_number = db.Column(db.String(100))
    application_date = db.Column(db.Date)
    publication_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='출원')
    patent_office = db.Column(db.String(100))
    main_inventor = db.Column(db.String(100))
    main_inventor_share = db.Column(db.Integer)
    co_inventors = db.Column(db.Text)
    description = db.Column(db.Text)
    link = db.Column(db.String(500))
    # 특허 관련 문서 링크들
    application_draft_link = db.Column(db.String(500))  # 출원서 초안
    prior_art_report_link = db.Column(db.String(500))   # 선행기술조사 보고서
    application_form_link = db.Column(db.String(500))   # 출원서
    application_review_link = db.Column(db.String(500)) # 출원 심의 자료
    office_action_link = db.Column(db.String(500))      # 의견제출통지서
    response_link = db.Column(db.String(500))           # 의견서
    amendment_link = db.Column(db.String(500))          # 보정서
    publication_link = db.Column(db.String(500))        # 특허등록 공보
    registration_review_link = db.Column(db.String(500)) # 등록 심의 자료
    notes = db.Column(db.Text)  # 비고
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class SafetyMaterial(db.Model):
    __tablename__ = 'safety_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Accident(db.Model):
    __tablename__ = 'accidents'
    
    id = db.Column(db.Integer, primary_key=True)
    accident_id = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time)
    location = db.Column(db.String(200))
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(50))
    injured_person = db.Column(db.String(100))
    cause = db.Column(db.Text)
    action_taken = db.Column(db.Text)
    status = db.Column(db.String(50), default='보고')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AccidentDocument(db.Model):
    __tablename__ = 'accident_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    accident_id = db.Column(db.Integer, db.ForeignKey('accidents.id'), nullable=False)
    document_type = db.Column(db.String(100))
    file_name = db.Column(db.String(200))
    file_path = db.Column(db.String(500))
    uploaded_date = db.Column(db.DateTime, default=datetime.utcnow)

class SafetyProcedure(db.Model):
    __tablename__ = 'safety_procedures'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    version = db.Column(db.String(20))
    responsible_person = db.Column(db.String(100))
    review_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='유효')
    procedure_link = db.Column(db.String(500))
    risk_assessment_link = db.Column(db.String(500))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    category = db.Column(db.String(100), default='협력업체')
    relationship = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Communication(db.Model):
    __tablename__ = 'communications'
    
    id = db.Column(db.Integer, primary_key=True)
    comm_id = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), default='익명')
    question_type = db.Column(db.String(50), default='일반')
    urgency = db.Column(db.String(50), default='보통')
    views = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='공개')
    answer = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Chemical(db.Model):
    __tablename__ = 'chemicals'
    
    id = db.Column(db.Integer, primary_key=True)
    chem_id = db.Column(db.String(50), unique=True, nullable=False)
    chemical_name = db.Column(db.String(200), nullable=False)
    cas_number = db.Column(db.String(50))
    manufacturer = db.Column(db.String(200))
    hazard_class = db.Column(db.String(100))
    storage_condition = db.Column(db.String(200))
    flash_point = db.Column(db.String(100))
    exposure_limit = db.Column(db.String(200))
    first_aid = db.Column(db.Text)
    disposal_method = db.Column(db.Text)
    msds_file_link = db.Column(db.String(500))
    location = db.Column(db.String(200))
    quantity = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 