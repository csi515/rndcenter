from flask import Blueprint, render_template, jsonify
from database import db
from database import Project, Patent, Equipment, Reservation, InventoryItem
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    # Get overview statistics from DB
    total_projects = Project.query.count()
    active_projects = Project.query.filter_by(status='진행중').count()
    total_patents = Patent.query.count()
    total_equipment = Equipment.query.count()
    available_equipment = Equipment.query.filter_by(status='사용 가능').count()
    total_reservations = Reservation.query.count()
    
    # 재고 중 수량이 10 이하인 항목 수
    low_inventory_items = InventoryItem.query.filter(InventoryItem.quantity < 10).count()
    
    stats = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_patents': total_patents,
        'total_equipment': total_equipment,
        'available_equipment': available_equipment,
        'total_reservations': total_reservations,
        'low_inventory_items': low_inventory_items
    }
    
    # Get recent activities
    recent_projects = Project.query.order_by(Project.created_date.desc()).limit(5).all()
    recent_reservations = Reservation.query.order_by(Reservation.created_date.desc()).limit(5).all()
    
    # Convert to dict for template
    recent_projects_list = []
    for project in recent_projects:
        recent_projects_list.append({
            'name': project.name,
            'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else 'nan',
            'end_date': project.end_date.strftime('%Y-%m-%d') if project.end_date else 'nan',
            'status': project.status
        })
    
    recent_reservations_list = []
    for reservation in recent_reservations:
        recent_reservations_list.append({
            'equipment_name': reservation.equipment_name or '알 수 없음',
            'user_name': reservation.reserver or '',
            'start_time': reservation.start_time.strftime('%H:%M') if reservation.start_time else '00:00',
            'end_time': reservation.end_time.strftime('%H:%M') if reservation.end_time else '14:00'
        })
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_projects=recent_projects_list,
                         recent_reservations=recent_reservations_list)

@dashboard_bp.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    # Project status distribution
    project_status_query = db.session.query(
        Project.status, 
        func.count(Project.id)
    ).group_by(Project.status).all()
    
    project_status = {status: count for status, count in project_status_query}
    
    # Equipment status distribution
    equipment_status_query = db.session.query(
        Equipment.status, 
        func.count(Equipment.id)
    ).group_by(Equipment.status).all()
    
    equipment_status = {status: count for status, count in equipment_status_query}
    
    return jsonify({
        'project_status': project_status,
        'equipment_status': equipment_status
    })
