from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from database import db, Project, Researcher, WeeklyScheduleNew, Week
import uuid
from datetime import datetime

research_bp = Blueprint('research', __name__)

@research_bp.route('/projects')
def projects():
    projects = Project.query.order_by(Project.created_date.desc()).all()
    return render_template('research/projects.html', projects=projects)

@research_bp.route('/researchers')
def researchers():
    researchers = Researcher.query.order_by(Researcher.created_date.desc()).all()
    return render_template('research/researchers.html', researchers=researchers)

@research_bp.route('/schedule')
def schedule():
    return render_template('research/schedule.html', schedule=[])

@research_bp.route('/researchers/add', methods=['POST'])
def add_researcher():
    name = request.form.get('name')
    employee_id = request.form.get('employee_id')
    position = request.form.get('position')
    department = request.form.get('department')
    specialization = request.form.get('specialization')
    email = request.form.get('email')
    phone = request.form.get('phone')
    hire_date = request.form.get('hire_date')
    status = request.form.get('status', '재직')

    researcher = Researcher(
        employee_id=employee_id,
        name=name,
        position=position,
        department=department,
        specialization=specialization,
        email=email,
        phone=phone,
        hire_date=datetime.strptime(hire_date, '%Y-%m-%d') if hire_date else None,
        status=status,
        created_date=datetime.now()
    )
    db.session.add(researcher)
    db.session.commit()
    return redirect(url_for('research.researchers'))

@research_bp.route('/projects/add', methods=['POST'])
def add_project():
    name = request.form.get('name')
    description = request.form.get('description')
    status = request.form.get('status')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    participants = request.form.get('participants')

    project = Project(
        project_id=str(uuid.uuid4()),
        name=name,
        description=description,
        status=status,
        start_date=datetime.strptime(start_date, '%Y-%m-%d') if start_date else None,
        end_date=datetime.strptime(end_date, '%Y-%m-%d') if end_date else None,
        participants=participants,
        created_date=datetime.now()
    )
    db.session.add(project)
    db.session.commit()
    return redirect(url_for('research.projects'))

# ---- 임시 API 엔드포인트 ----
@research_bp.route('/api/researchers')
def api_researchers():
    # 임시 데이터 반환
    return jsonify([])

@research_bp.route('/schedule/add', methods=['POST'])
def api_schedule_add():
    data = request.get_json()
    project_name = data.get('project')
    researcher_name = data.get('researcher')
    year = int(data.get('year'))
    month = int(data.get('month'))
    week = int(data.get('week'))
    title = data.get('task')
    description = data.get('notes')
    # week_id 찾기
    week_obj = Week.query.filter_by(year=year, month=month, week_number=week).first()
    if not week_obj:
        week_obj = Week(year=year, month=month, week_number=week)
        db.session.add(week_obj)
        db.session.commit()
    schedule = WeeklyScheduleNew(
        project_name=project_name,
        researcher_name=researcher_name,
        week_id=week_obj.id,
        title=title,
        description=description,
        start_week_id=week_obj.id,
        end_week_id=week_obj.id
    )
    db.session.add(schedule)
    db.session.commit()
    return jsonify({'success': True})

@research_bp.route('/schedule/update/<int:id>', methods=['PUT'])
def api_schedule_update(id):
    data = request.get_json()
    schedule = WeeklyScheduleNew.query.get(id)
    if not schedule:
        return jsonify({'success': False, 'message': '일정이 존재하지 않습니다.'})
    schedule.title = data.get('task')
    schedule.description = data.get('notes')
    schedule.project_name = data.get('project')
    schedule.researcher_name = data.get('researcher')
    # 주차 정보 변경
    year = int(data.get('year'))
    month = int(data.get('month'))
    week = int(data.get('week'))
    week_obj = Week.query.filter_by(year=year, month=month, week_number=week).first()
    if not week_obj:
        week_obj = Week(year=year, month=month, week_number=week)
        db.session.add(week_obj)
        db.session.commit()
    schedule.week_id = week_obj.id
    schedule.start_week_id = week_obj.id
    schedule.end_week_id = week_obj.id
    db.session.commit()
    return jsonify({'success': True})

@research_bp.route('/api/schedule')
def api_schedule():
    schedules = WeeklyScheduleNew.query.all()
    result = []
    for s in schedules:
        week = Week.query.get(s.week_id)
        result.append({
            'id': s.id,
            'title': s.title,
            'extendedProps': {
                'project': s.project_name,
                'researcher': s.researcher_name,
                'year': week.year if week else None,
                'month': week.month if week else None,
                'week': week.week_number if week else None,
                'notes': s.description
            }
        })
    return jsonify(result)

@research_bp.route('/schedule/delete/<int:id>', methods=['DELETE'])
def api_schedule_delete(id):
    schedule = WeeklyScheduleNew.query.get(id)
    if not schedule:
        return jsonify({'success': False, 'message': '일정이 존재하지 않습니다.'})
    db.session.delete(schedule)
    db.session.commit()
    return jsonify({'success': True})

@research_bp.route('/projects/api')
def api_projects():
    projects = Project.query.order_by(Project.created_date.desc()).all()
    return jsonify([
        {'id': p.id, 'name': p.name, 'color': '#1976d2'}  # color는 임시값
        for p in projects
    ])

@research_bp.route('/projects/delete/<int:project_id>')
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('research.projects'))

@research_bp.route('/projects/manage', methods=['GET', 'POST'])
def projects_manage():
    if request.method == 'POST':
        data = request.get_json()
        new_name = data.get('new_name')
        color = data.get('color', '#1976d2')
        if not new_name:
            return jsonify({'success': False, 'message': '프로젝트명이 필요합니다.'})
        # 이미 존재하는지 확인
        exists = Project.query.filter_by(name=new_name).first()
        if exists:
            return jsonify({'success': False, 'message': '이미 존재하는 프로젝트명입니다.'})
        project = Project(
            project_id=str(uuid.uuid4()),
            name=new_name,
            description='',
            status='진행중',
            participants='',
            created_date=datetime.now()
        )
        db.session.add(project)
        db.session.commit()
        return jsonify({'success': True})
    # GET 요청 시 전체 프로젝트 목록 반환 (필요시)
    projects = Project.query.order_by(Project.created_date.desc()).all()
    return jsonify([{'id': p.id, 'name': p.name} for p in projects])

@research_bp.route('/projects/update/<int:project_id>', methods=['POST'])
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.name = request.form.get('name', project.name)
    project.description = request.form.get('description', project.description)
    project.status = request.form.get('status', project.status)
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    if start_date:
        project.start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        project.end_date = datetime.strptime(end_date, '%Y-%m-%d')
    project.participants = request.form.get('participants', project.participants)
    db.session.commit()
    return redirect(url_for('research.projects'))

@research_bp.route('/projects/update_status/<int:project_id>', methods=['POST'])
def update_project_status(project_id):
    project = Project.query.get_or_404(project_id)
    new_status = request.form.get('status')  # 예: '완료', '진행중' 등
    if new_status:
        project.status = new_status
        db.session.commit()
        return redirect(url_for('research.projects'))
    return 'Invalid status', 400

@research_bp.route('/researchers/update/<int:researcher_id>', methods=['POST'])
def update_researcher(researcher_id):
    researcher = Researcher.query.get_or_404(researcher_id)
    researcher.name = request.form.get('name', researcher.name)
    researcher.employee_id = request.form.get('employee_id', researcher.employee_id)
    researcher.position = request.form.get('position', researcher.position)
    researcher.department = request.form.get('department', researcher.department)
    researcher.specialization = request.form.get('specialization', researcher.specialization)
    researcher.email = request.form.get('email', researcher.email)
    researcher.phone = request.form.get('phone', researcher.phone)
    hire_date = request.form.get('hire_date')
    if hire_date:
        researcher.hire_date = datetime.strptime(hire_date, '%Y-%m-%d')
    researcher.status = request.form.get('status', researcher.status)
    db.session.commit()
    return redirect(url_for('research.researchers'))

@research_bp.route('/researchers/delete/<int:researcher_id>', methods=['POST'])
def delete_researcher(researcher_id):
    researcher = Researcher.query.get_or_404(researcher_id)
    db.session.delete(researcher)
    db.session.commit()
    return redirect(url_for('research.researchers'))



