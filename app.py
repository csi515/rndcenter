import os
import logging
from flask import Flask, redirect, request
from werkzeug.middleware.proxy_fix import ProxyFix
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

# Security and performance headers
@app.after_request
def add_security_headers(response):
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' data: https://cdnjs.cloudflare.com;"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Cache control for static assets
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year for static assets
    else:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    return response

# HTTPS redirect (for production)
@app.before_request
def https_redirect():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# Import database and models
from database import db, Project, Researcher, Equipment, Reservation, UsageLog, CoalTarPitchLog, Week, WeeklyScheduleNew, Patent, InventoryItem, InventoryTransaction, SafetyMaterial, Accident, AccidentDocument, SafetyProcedure, Contact, Communication, Chemical

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///app.db"  # Use SQLite as fallback
)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)



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
app.register_blueprint(communication_bp, url_prefix='/communication')
app.register_blueprint(external_bp, url_prefix='/external')
app.register_blueprint(chemical_bp, url_prefix='/chemical')
app.register_blueprint(coal_log_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8002, debug=True)
