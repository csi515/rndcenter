from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from csv_manager import csv_manager
from database import db, WeeklySchedule, Project, Researcher, ProjectSchedule
import pandas as pd
from datetime import datetime, date
import json
import calendar

research_bp = Blueprint('research', __name__)

@research_bp.route('/projects')
def projects():
    projects_data = csv_manager.read_csv('projects.csv')
    projects_list = projects_data.to_dict('records') if not projects_data.empty else []
    return render_template('research/projects.html', projects=projects_list)

@research_bp.route('/projects/api')
def projects_api():
    """API endpoint for projects data"""
    try:
        projects = Project.query.all()
        projects_list = []
        for project in projects:
            projects_list.append({
                'id': project.id,
                'project_id': project.project_id,
                'name': project.name,
                'description': project.description,
                'leader': project.leader,
                'department': project.department,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'status': project.status,
                'progress': project.progress
            })
        return jsonify(projects_list)
    except Exception as e:
        return jsonify([])

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
        'position': request.form.get('position', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('researchers.csv', data):
        flash('연구원이 성공적으로 추가되었습니다.', 'success')
    else:
        flash('연구원 추가 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('research.researchers'))

@research_bp.route('/researchers/update/<int:index>', methods=['POST'])
def update_researcher(index):
    try:
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'position': request.form.get('position', '')
        }
        
        if csv_manager.update_row('researchers.csv', index, data):
            flash('연구원 정보가 성공적으로 수정되었습니다.', 'success')
        else:
            flash('연구원 정보 수정 중 오류가 발생했습니다.', 'error')
    except Exception as e:
        flash(f'연구원 정보 수정 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('research.researchers'))

@research_bp.route('/researchers/delete/<int:index>', methods=['POST'])
def delete_researcher(index):
    try:
        if csv_manager.delete_row('researchers.csv', index):
            flash('연구원이 성공적으로 삭제되었습니다.', 'success')
        else:
            flash('연구원 삭제 중 오류가 발생했습니다.', 'error')
    except Exception as e:
        flash(f'연구원 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('research.researchers'))

@research_bp.route('/researchers/api')
def researchers_api():
    """API endpoint for researchers data"""
    try:
        researchers = Researcher.query.all()
        researchers_list = []
        for researcher in researchers:
            researchers_list.append({
                'id': researcher.id,
                'employee_id': researcher.employee_id,
                'name': researcher.name,
                'position': researcher.position,
                'department': researcher.department,
                'specialization': researcher.specialization,
                'email': researcher.email,
                'phone': researcher.phone,
                'status': researcher.status
            })
        return jsonify(researchers_list)
    except Exception as e:
        return jsonify([])

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
        schedule = WeeklySchedule(**{
            'schedule_id': f"schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(data.get('task', ''))%10000}",
            'week': int(data.get('week')),
            'month': int(data.get('month')),
            'year': int(data.get('year')),
            'task': data.get('task'),
            'researcher': data.get('researcher', ''),
            'project': data.get('project', ''),
            'priority': data.get('priority', '보통'),
            'notes': data.get('notes', '')
        })
        
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

# 프로젝트 일정 관리 (새로운 페이지)
@research_bp.route('/schedule/projects')
def project_schedule():
    """프로젝트별 주간 일정 관리 페이지"""
    # 프로젝트 목록 가져오기
    projects = Project.query.all()
    researchers = Researcher.query.all()
    
    return render_template('research/project_schedule.html', 
                         projects=projects, 
                         researchers=researchers)

@research_bp.route('/schedule/projects/api/data')
def get_project_schedule_data():
    """프로젝트 일정 데이터 API"""
    year = request.args.get('year', type=int, default=datetime.now().year)
    month = request.args.get('month', type=int, default=datetime.now().month)
    project_id = request.args.get('project_id')
    
    # 3개월 범위 계산
    months = []
    for i in range(-1, 2):  # 이전달, 현재달, 다음달
        target_month = month + i
        target_year = year
        
        if target_month < 1:
            target_month += 12
            target_year -= 1
        elif target_month > 12:
            target_month -= 12
            target_year += 1
            
        months.append({'year': target_year, 'month': target_month})
    
    # 주차 정보 생성
    calendar_data = []
    for month_info in months:
        cal = calendar.monthcalendar(month_info['year'], month_info['month'])
        weeks = []
        
        for week_num, week in enumerate(cal, 1):
            if any(day > 0 for day in week):  # 유효한 주차만
                week_start = next(day for day in week if day > 0)
                week_end = max(day for day in week if day > 0)
                weeks.append({
                    'week_num': week_num,
                    'week_start': week_start,
                    'week_end': week_end,
                    'month': month_info['month'],
                    'year': month_info['year']
                })
        
        calendar_data.append({
            'month': month_info['month'],
            'year': month_info['year'],
            'weeks': weeks
        })
    
    # 일정 데이터 가져오기
    query = ProjectSchedule.query.join(Project)
    if project_id:
        query = query.filter(ProjectSchedule.project_id == project_id)
    
    schedules = query.all()
    
    # 일정 데이터를 주차별로 그룹화
    schedule_data = []
    for schedule in schedules:
        researchers = []
        if schedule.researcher_ids:
            try:
                researcher_ids = json.loads(schedule.researcher_ids)
                researchers = [r.name for r in Researcher.query.filter(Researcher.employee_id.in_(researcher_ids)).all()]
            except:
                pass
        
        schedule_data.append({
            'id': schedule.id,
            'project_id': schedule.project_id,
            'project_name': schedule.project.name if schedule.project else '',
            'title': schedule.title,
            'start_week': schedule.start_week,
            'end_week': schedule.end_week,
            'start_month': schedule.start_month,
            'start_year': schedule.start_year,
            'researchers': researchers,
            'memo': schedule.memo
        })
    
    return jsonify({
        'calendar': calendar_data,
        'schedules': schedule_data
    })

@research_bp.route('/schedule/projects/add', methods=['POST'])
def add_project_schedule():
    """프로젝트 일정 추가"""
    try:
        data = request.get_json()
        
        new_schedule = ProjectSchedule(**{
            'project_id': data['project_id'],
            'title': data['title'],
            'start_week': data['start_week'],
            'end_week': data['end_week'],
            'start_month': data['start_month'],
            'start_year': data['start_year'],
            'researcher_ids': json.dumps(data.get('researcher_ids', [])),
            'memo': data.get('memo', '')
        })
        
        db.session.add(new_schedule)
        db.session.commit()
        
        return jsonify({'success': True, 'id': new_schedule.id})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@research_bp.route('/schedule/projects/update/<int:schedule_id>', methods=['PUT'])
def update_project_schedule(schedule_id):
    """프로젝트 일정 수정"""
    try:
        schedule = ProjectSchedule.query.get_or_404(schedule_id)
        data = request.get_json()
        
        schedule.title = data.get('title', schedule.title)
        schedule.start_week = data.get('start_week', schedule.start_week)
        schedule.end_week = data.get('end_week', schedule.end_week)
        schedule.start_month = data.get('start_month', schedule.start_month)
        schedule.start_year = data.get('start_year', schedule.start_year)
        schedule.researcher_ids = json.dumps(data.get('researcher_ids', []))
        schedule.memo = data.get('memo', schedule.memo)
        schedule.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@research_bp.route('/schedule/projects/delete/<int:schedule_id>', methods=['DELETE'])
def delete_project_schedule(schedule_id):
    """프로젝트 일정 삭제"""
    try:
        schedule = ProjectSchedule.query.get_or_404(schedule_id)
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@research_bp.route('/schedule/projects/move/<int:schedule_id>', methods=['POST'])
def move_project_schedule(schedule_id):
    """프로젝트 일정 이동"""
    try:
        schedule = ProjectSchedule.query.get_or_404(schedule_id)
        data = request.get_json()
        
        # 새로운 주차/월 정보로 업데이트
        schedule.start_week = data['start_week']
        schedule.end_week = data['end_week']
        schedule.start_month = data['start_month']
        schedule.start_year = data['start_year']
        schedule.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
