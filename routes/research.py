from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from csv_manager import csv_manager
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
