from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from csv_manager import csv_manager
from database import db, WeeklySchedule
import pandas as pd
from datetime import datetime

research_bp = Blueprint('research', __name__)

@research_bp.route('/projects')
def projects():
    projects_data = csv_manager.read_csv('projects.csv')
    projects_list = projects_data.to_dict('records') if not projects_data.empty else []
    return render_template('research/projects.html', projects=projects_list)

@research_bp.route('/projects/add', methods=['POST'])
def add_project():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'start_date': request.form.get('start_date'),
        'end_date': request.form.get('end_date'),
        'status': request.form.get('status', '진행중'),
        'participants': request.form.get('participants'),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('projects.csv', data):
        flash('프로젝트가 성공적으로 추가되었습니다.', 'success')
    else:
        flash('프로젝트 추가 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('research.projects'))

@research_bp.route('/projects/update/<int:index>', methods=['POST'])
def update_project(index):
    data = {
        'name': request.form.get('name'),
        'description': request.form.get('description'),
        'start_date': request.form.get('start_date'),
        'end_date': request.form.get('end_date'),
        'status': request.form.get('status'),
        'participants': request.form.get('participants'),
        'updated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.update_row('projects.csv', index, data):
        flash('프로젝트가 성공적으로 수정되었습니다.', 'success')
    else:
        flash('프로젝트 수정 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('research.projects'))

@research_bp.route('/projects/delete/<int:index>')
def delete_project(index):
    if csv_manager.delete_row('projects.csv', index):
        flash('프로젝트가 성공적으로 삭제되었습니다.', 'success')
    else:
        flash('프로젝트 삭제 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('research.projects'))

@research_bp.route('/researchers')
def researchers():
    researchers_data = csv_manager.read_csv('researchers.csv')
    researchers_list = researchers_data.to_dict('records') if not researchers_data.empty else []
    return render_template('research/researchers.html', researchers=researchers_list)

@research_bp.route('/researchers/add', methods=['POST'])
def add_researcher():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'role': request.form.get('role'),
        'department': request.form.get('department'),
        'join_date': request.form.get('join_date'),
        'projects': request.form.get('projects', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('researchers.csv', data):
        flash('연구원이 성공적으로 추가되었습니다.', 'success')
    else:
        flash('연구원 추가 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('research.researchers'))

@research_bp.route('/schedule')
def schedule():
    schedule_data = csv_manager.read_csv('schedule.csv')
    researchers_data = csv_manager.read_csv('researchers.csv')
    projects_data = csv_manager.read_csv('projects.csv')
    
    schedule_list = schedule_data.to_dict('records') if not schedule_data.empty else []
    researchers_list = researchers_data.to_dict('records') if not researchers_data.empty else []
    projects_list = projects_data.to_dict('records') if not projects_data.empty else []
    
    return render_template('research/schedule.html', 
                         schedule=schedule_list,
                         researchers=researchers_list,
                         projects=projects_list)

@research_bp.route('/schedule/add', methods=['POST'])
def add_schedule():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'researcher_name': request.form.get('researcher_name'),
        'project_name': request.form.get('project_name'),
        'task': request.form.get('task'),
        'start_date': request.form.get('start_date'),
        'end_date': request.form.get('end_date'),
        'start_time': request.form.get('start_time'),
        'end_time': request.form.get('end_time'),
        'status': request.form.get('status', '예정'),
        'notes': request.form.get('notes', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('schedule.csv', data):
        return jsonify({'success': True, 'message': '일정이 성공적으로 추가되었습니다.'})
    else:
        return jsonify({'success': False, 'message': '일정 추가 중 오류가 발생했습니다.'})

@research_bp.route('/api/schedule')
def api_schedule():
    """API endpoint for calendar data"""
    schedule_data = csv_manager.read_csv('schedule.csv')
    events = []
    
    if not schedule_data.empty:
        for _, row in schedule_data.iterrows():
            event = {
                'id': row.get('id', ''),
                'title': f"{row.get('researcher_name', '')} - {row.get('task', '')}",
                'start': f"{row.get('start_date', '')}T{row.get('start_time', '09:00')}",
                'end': f"{row.get('end_date', '')}T{row.get('end_time', '18:00')}",
                'resourceId': row.get('researcher_name', ''),
                'extendedProps': {
                    'project': row.get('project_name', ''),
                    'status': row.get('status', ''),
                    'notes': row.get('notes', '')
                }
            }
            events.append(event)
    
    return jsonify(events)

# Weekly Schedule API endpoints
@research_bp.route('/api/weekly-schedule/<int:year>/<int:month>')
def get_weekly_schedule(year, month):
    """Get weekly schedules for a specific month"""
    schedules = WeeklySchedule.query.filter_by(year=year, month=month).all()
    
    schedule_data = {}
    for schedule in schedules:
        week_key = str(schedule.week)
        if week_key not in schedule_data:
            schedule_data[week_key] = []
        
        schedule_data[week_key].append({
            'id': schedule.schedule_id,
            'task': schedule.task,
            'researcher': schedule.researcher,
            'project': schedule.project,
            'priority': schedule.priority,
            'notes': schedule.notes,
            'createdAt': schedule.created_date.isoformat() if schedule.created_date else None
        })
    
    return jsonify(schedule_data)

@research_bp.route('/api/weekly-schedule/add', methods=['POST'])
def add_weekly_schedule():
    """Add a new weekly schedule item"""
    data = request.get_json()
    
    try:
        schedule = WeeklySchedule(
            schedule_id=f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(data.get('task', ''))%10000}",
            week=int(data.get('week')),
            month=int(data.get('month')),
            year=int(data.get('year')),
            task=data.get('task'),
            researcher=data.get('researcher', ''),
            project=data.get('project', ''),
            priority=data.get('priority', '보통'),
            notes=data.get('notes', '')
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'schedule': {
                'id': schedule.schedule_id,
                'task': schedule.task,
                'researcher': schedule.researcher,
                'project': schedule.project,
                'priority': schedule.priority,
                'notes': schedule.notes,
                'createdAt': schedule.created_date.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@research_bp.route('/api/weekly-schedule/update/<schedule_id>', methods=['PUT'])
def update_weekly_schedule(schedule_id):
    """Update an existing weekly schedule item"""
    data = request.get_json()
    
    try:
        schedule = WeeklySchedule.query.filter_by(schedule_id=schedule_id).first()
        if not schedule:
            return jsonify({'success': False, 'error': 'Schedule not found'}), 404
        
        schedule.task = data.get('task', schedule.task)
        schedule.researcher = data.get('researcher', schedule.researcher)
        schedule.project = data.get('project', schedule.project)
        schedule.priority = data.get('priority', schedule.priority)
        schedule.notes = data.get('notes', schedule.notes)
        schedule.updated_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'schedule': {
                'id': schedule.schedule_id,
                'task': schedule.task,
                'researcher': schedule.researcher,
                'project': schedule.project,
                'priority': schedule.priority,
                'notes': schedule.notes,
                'updatedAt': schedule.updated_date.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@research_bp.route('/api/weekly-schedule/move/<schedule_id>', methods=['PUT'])
def move_weekly_schedule(schedule_id):
    """Move a schedule item to a different week"""
    data = request.get_json()
    
    try:
        schedule = WeeklySchedule.query.filter_by(schedule_id=schedule_id).first()
        if not schedule:
            return jsonify({'success': False, 'error': 'Schedule not found'}), 404
        
        schedule.week = int(data.get('week'))
        schedule.updated_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@research_bp.route('/api/weekly-schedule/delete/<schedule_id>', methods=['DELETE'])
def delete_weekly_schedule(schedule_id):
    """Delete a weekly schedule item"""
    try:
        schedule = WeeklySchedule.query.filter_by(schedule_id=schedule_id).first()
        if not schedule:
            return jsonify({'success': False, 'error': 'Schedule not found'}), 404
        
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
