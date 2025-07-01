from flask import Blueprint, render_template, jsonify
from csv_manager import csv_manager
import pandas as pd
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    # Get overview statistics
    projects = csv_manager.read_csv('projects.csv')
    patents = csv_manager.read_csv('patents.csv')
    equipment = csv_manager.read_csv('equipment.csv')
    reservations = csv_manager.read_csv('reservations.csv')
    inventory = csv_manager.read_csv('inventory.csv')
    
    stats = {
        'total_projects': len(projects),
        'active_projects': len(projects[projects.get('status', '') == '진행중']) if not projects.empty else 0,
        'total_patents': len(patents),
        'total_equipment': len(equipment),
        'available_equipment': len(equipment[equipment.get('status', '') == '사용 가능']) if not equipment.empty else 0,
        'total_reservations': len(reservations),
        'low_inventory_items': len(inventory[inventory.get('quantity', 0) < 10]) if not inventory.empty else 0
    }
    
    # Get recent activities
    recent_projects = projects.tail(5).to_dict('records') if not projects.empty else []
    recent_reservations = reservations.tail(5).to_dict('records') if not reservations.empty else []
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_projects=recent_projects,
                         recent_reservations=recent_reservations)

@dashboard_bp.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    projects = csv_manager.read_csv('projects.csv')
    
    # Project status distribution
    project_status = {}
    if not projects.empty:
        status_counts = projects['status'].value_counts() if 'status' in projects.columns else {}
        project_status = status_counts.to_dict()
    
    # Equipment status distribution
    equipment = csv_manager.read_csv('equipment.csv')
    equipment_status = {}
    if not equipment.empty:
        status_counts = equipment['status'].value_counts() if 'status' in equipment.columns else {}
        equipment_status = status_counts.to_dict()
    
    return jsonify({
        'project_status': project_status,
        'equipment_status': equipment_status
    })
