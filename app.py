import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-for-rd-center")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql://username:password@172.28.12.47:5987/dbname"
)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create database instance
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

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
    budget = db.Column(db.Numeric(15, 2))
    status = db.Column(db.String(50), default='진행중')
    progress = db.Column(db.Integer, default=0)
    participants = db.Column(db.Text)
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

class ProjectType(db.Model):
    __tablename__ = 'project_types'
    id = db.Column(db.String(50), primary_key=True)
    project_type = db.Column(db.String(200), unique=True, nullable=False)

class CoalTarPitchLog(db.Model):
    __tablename__ = 'coal_tar_pitch_logs'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    material = db.Column(db.String(100), default='콜타르피치 휘발물', nullable=False)
    used_at = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    work_content = db.Column(db.String(200))
    amount = db.Column(db.String(100))
    ppe = db.Column(db.Boolean, default=False)
    process_condition = db.Column(db.String(200))
    exposure_reaction = db.Column(db.String(200))
    action_note = db.Column(db.String(200))
    writer = db.Column(db.String(100))
    manager_sign = db.Column(db.String(100))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

# Import and register blueprints
from routes.dashboard import dashboard_bp
from routes.research import research_bp
from routes.patents import patents_bp
from routes.equipment import equipment_bp
from routes.inventory import inventory_bp
from routes.safety import safety_bp
from routes.purchasing import purchasing_bp
from routes.communication import communication_bp
from routes.external import external_bp
from routes.chemical import chemical_bp
from routes.coal_tar_pitch_log import coal_log_bp

app.register_blueprint(dashboard_bp, url_prefix='/')
app.register_blueprint(research_bp, url_prefix='/research')
app.register_blueprint(patents_bp, url_prefix='/patents')
app.register_blueprint(equipment_bp, url_prefix='/equipment')
app.register_blueprint(inventory_bp, url_prefix='/inventory')
app.register_blueprint(safety_bp, url_prefix='/safety')
app.register_blueprint(purchasing_bp, url_prefix='/purchasing')
app.register_blueprint(communication_bp, url_prefix='/communication')
app.register_blueprint(external_bp, url_prefix='/external')
app.register_blueprint(chemical_bp, url_prefix='/chemical')
app.register_blueprint(coal_log_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(host='172.28.12.68', port=8002, debug=False)
