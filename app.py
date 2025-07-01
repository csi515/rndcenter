import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from database import db, init_db

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-for-rd-center")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///rd_center.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
init_db(app)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
