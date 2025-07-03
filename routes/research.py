from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from csv_manager import csv_manager
from database import db, WeeklySchedule, Project, Researcher, ProjectSchedule, Week, WeeklyScheduleNew
import pandas as pd
from datetime import datetime, date
import json
import calendar
import os
import csv

research_bp = Blueprint('research', __name__)

SCHEDULE_JSON = os.path.join('data', 'schedule.json')
PROJECTS_CSV = os.path.join('data', 'projects.csv')

def read_schedules():
    if not os.path.exists(SCHEDULE_JSON):
        return []
    with open(SCHEDULE_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_schedules(schedules):
    with open(SCHEDULE_JSON, 'w', encoding='utf-8') as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)

def get_year_month_week(date_str):
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        year = d.year
        month = d.month
        week = (d.day - 1) // 7 + 1
        return str(year), str(month), str(week)
    except Exception:
        return "", "", ""

@research_bp.route('/projects')
def projects():
    projects_data = csv_manager.read_csv('projects.csv')
    projects_list = projects_data.to_dict('records') if not projects_data.empty else []
    return render_template('research/projects.html', projects=projects_list)

@research_bp.route('/projects/api')
def projects_api():
    projects = []
    with open('data/projects.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # participants 등 NaN, None, Infinity 등 비정상 값 보정
            for k, v in row.items():
                if v in [None, 'NaN', 'nan', 'undefined', 'Infinity']:
                    row[k] = ""
            projects.append(row)
    return jsonify(projects)

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

@research_bp.route('/projects/delete', methods=['POST'])
def delete_project_api():
    data = request.get_json()
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'success': False, 'message': '프로젝트명 누락'})
    # projects.csv에서 삭제 (있을 때만)
    projects_df = csv_manager.read_csv('projects.csv')
    existed = (projects_df['name'] == name).any() if not projects_df.empty else False
    projects_df = projects_df[projects_df['name'] != name] if not projects_df.empty else projects_df
    csv_manager.write_csv('projects.csv', projects_df)
    # schedule.json에서도 해당 프로젝트 일정 삭제 (항상 시도)
    schedules = read_schedules()
    before = len(schedules)
    schedules = [s for s in schedules if (s.get('project_name') or s.get('project')) != name]
    write_schedules(schedules)
    after = len(schedules)
    if existed or before != after:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': '해당 프로젝트를 찾을 수 없음'})

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
    projects_data = csv_manager.read_csv('projects.csv')
    projects_list = projects_data.to_dict('records') if not projects_data.empty else []
    return render_template('research/schedule.html', projects=projects_list)

@research_bp.route('/schedule/add', methods=['POST'])
def add_schedule():
    schedules = read_schedules()
    if request.is_json:
        data = request.get_json()
        get = lambda k, default='': data.get(k, default)
    else:
        get = lambda k, default='': request.form.get(k, default)
    new_schedule = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'researcher_name': get('researcher_name'),
        'project_name': get('project_name') or get('project'),
        'task': get('task'),
        'start_date': get('start_date'),
        'end_date': get('end_date'),
        'start_time': get('start_time'),
        'end_time': get('end_time'),
        'year': get('year', ''),
        'month': get('month', ''),
        'week': get('week', ''),
        'priority': get('priority', '보통'),
        'status': get('status', '예정'),
        'notes': get('notes', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    schedules.append(new_schedule)
    write_schedules(schedules)
    return jsonify({'success': True, 'message': '일정이 성공적으로 추가되었습니다.'})

@research_bp.route('/schedule/update/<schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    schedules = read_schedules()
    updated = False
    for schedule in schedules:
        if str(schedule.get('id', '')) == str(schedule_id):
            schedule['researcher_name'] = request.form.get('researcher_name', schedule.get('researcher_name', ''))
            schedule['project_name'] = request.form.get('project_name', schedule.get('project_name', ''))
            schedule['task'] = request.form.get('task', schedule.get('task', ''))
            schedule['start_date'] = request.form.get('start_date', schedule.get('start_date', ''))
            schedule['end_date'] = request.form.get('end_date', schedule.get('end_date', ''))
            schedule['start_time'] = request.form.get('start_time', schedule.get('start_time', ''))
            schedule['end_time'] = request.form.get('end_time', schedule.get('end_time', ''))
            schedule['year'] = request.form.get('year', schedule.get('year', ''))
            schedule['month'] = request.form.get('month', schedule.get('month', ''))
            schedule['week'] = request.form.get('week', schedule.get('week', ''))
            schedule['priority'] = request.form.get('priority', schedule.get('priority', '보통'))
            schedule['status'] = request.form.get('status', schedule.get('status', '예정'))
            schedule['notes'] = request.form.get('notes', schedule.get('notes', ''))
            schedule['updated_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated = True
            break
    if updated:
        write_schedules(schedules)
        return jsonify({'success': True, 'message': '일정이 성공적으로 수정되었습니다.'})
    else:
        return jsonify({'success': False, 'message': '일정을 찾을 수 없습니다.'})

@research_bp.route('/schedule/delete/<schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    schedules = read_schedules()
    new_schedules = [s for s in schedules if str(s.get('id', '')) != str(schedule_id)]
    if len(new_schedules) == len(schedules):
        return jsonify({'success': False, 'message': '일정을 찾을 수 없습니다.'})
    write_schedules(new_schedules)
    return jsonify({'success': True, 'message': '일정이 성공적으로 삭제되었습니다.'})

@research_bp.route('/api/schedule')
def api_schedule():
    schedules = read_schedules()
    events = []
    for row in schedules:
        # year, month, week가 없으면 start_date에서 계산
        year = row.get('year') or ""
        month = row.get('month') or ""
        week = row.get('week') or ""
        if not (year and month and week):
            year, month, week = get_year_month_week(row.get('start_date', ''))
        event = {
            'id': row.get('id', ''),
            'title': f"{row.get('researcher_name', '')} - {row.get('task', '')}",
            'start': f"{row.get('start_date', '')}T{row.get('start_time', '09:00')}",
            'end': f"{row.get('end_date', '')}T{row.get('end_time', '18:00')}",
            'resourceId': row.get('researcher_name', ''),
            'extendedProps': {
                'project': row.get('project_name', ''),
                'status': row.get('status', ''),
                'notes': row.get('notes', ''),
                'year': year,
                'month': month,
                'week': week,
                'priority': row.get('priority', '보통')
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


# 새로운 주간 일정 관리 페이지
@research_bp.route("/weekly-schedule")
def weekly_schedule():
    """2단 테이블 헤더 구조의 주간 일정 관리 페이지"""
    return render_template("research/weekly_schedule.html")

@research_bp.route("/weekly-schedule/projects/api")
def weekly_schedule_projects_api():
    """프로젝트 목록 API (주간 일정용)"""
    try:
        # 기본 프로젝트들 (임시)
        projects_list = [
            {"id": 1, "name": "신약 개발 프로젝트", "researcher": "김연구"},
            {"id": 2, "name": "바이오 센서 연구", "researcher": "이박사"},
            {"id": 3, "name": "나노 소재 분석", "researcher": "박교수"}
        ]
        return jsonify(projects_list)
    except Exception as e:
        return jsonify([])

@research_bp.route("/weekly-schedule/schedules/api")
def weekly_schedule_schedules_api():
    """주간 일정 데이터 API"""
    try:
        # 임시 일정 데이터
        schedules_list = []
        return jsonify(schedules_list)
    except Exception as e:
        return jsonify([])

@research_bp.route('/project-schedule')
def project_schedule_page():
    # 연구원, 프로젝트 목록 불러오기
    researchers_data = csv_manager.read_csv('researchers.csv')
    projects_data = csv_manager.read_csv('projects.csv')
    researchers = researchers_data.to_dict('records') if not researchers_data.empty else []
    projects = projects_data.to_dict('records') if not projects_data.empty else []
    return render_template('research/project_schedule.html', researchers=researchers, projects=projects)

@research_bp.route('/api/project-schedule', methods=['GET'])
def get_project_schedule():
    import pandas as pd
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    project_id = request.args.get('project_id')
    csv_path = os.path.join('data', 'project_schedule.csv')
    if not os.path.exists(csv_path):
        # 템플릿 생성
        df = pd.DataFrame(columns=['id','researcher_id','researcher_name','project_id','project_name','year','month','week','summary','detail','merged_weeks','created_at','updated_at'])
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    df = pd.read_csv(csv_path, dtype=str)
    if year:
        df = df[df['year'] == str(year)]
    if month:
        df = df[df['month'] == str(month)]
    if project_id:
        df = df[df['project_id'] == str(project_id)]
    return jsonify(df.to_dict('records'))

@research_bp.route('/api/project-schedule/save', methods=['POST'])
def save_project_schedule():
    import pandas as pd
    import uuid
    csv_path = os.path.join('data', 'project_schedule.csv')
    if not os.path.exists(csv_path):
        df = pd.DataFrame(columns=['id','researcher_id','researcher_name','project_id','project_name','year','month','week','summary','detail','merged_weeks','created_at','updated_at'])
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    df = pd.read_csv(csv_path, dtype=str)
    data = request.get_json()
    # id가 있으면 수정, 없으면 추가
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if data.get('id') and data['id'] in df['id'].values:
        idx = df.index[df['id'] == data['id']][0]
        for k in ['researcher_id','researcher_name','project_id','project_name','year','month','week','summary','detail','merged_weeks']:
            df.at[idx, k] = data.get(k, '')
        df.at[idx, 'updated_at'] = now
    else:
        data['id'] = str(uuid.uuid4())
        data['created_at'] = now
        data['updated_at'] = now
        for k in ['researcher_id','researcher_name','project_id','project_name','year','month','week','summary','detail','merged_weeks']:
            if k not in data:
                data[k] = ''
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    return jsonify({'success': True, 'id': data['id']})

@research_bp.route('/api/project-schedule/delete', methods=['POST'])
def delete_project_schedule_api():
    import pandas as pd
    csv_path = os.path.join('data', 'project_schedule.csv')
    if not os.path.exists(csv_path):
        return jsonify({'success': False, 'error': '파일 없음'})
    df = pd.read_csv(csv_path, dtype=str)
    data = request.get_json()
    if 'id' not in data:
        return jsonify({'success': False, 'error': 'id 없음'})
    df = df[df['id'] != data['id']]
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    return jsonify({'success': True})

# 프로젝트 관리 API (프론트엔드 연동용)
@research_bp.route('/projects/manage', methods=['POST'])
def manage_project_api():
    data = request.get_json()
    old_name = (data.get('old_name') or '').strip()
    new_name = (data.get('new_name') or '').strip()
    color = data.get('color', '#1976d2')
    if not new_name:
        return jsonify({'success': False, 'message': '프로젝트명 누락'})
    # projects.csv 읽기
    projects_df = csv_manager.read_csv('projects.csv')
    # 수정
    if old_name and old_name != new_name:
        if not (projects_df['name'] == old_name).any():
            return jsonify({'success': False, 'message': '기존 프로젝트를 찾을 수 없음'})
        projects_df.loc[projects_df['name'] == old_name, 'name'] = new_name
        projects_df.loc[projects_df['name'] == new_name, 'color'] = color
    # 추가
    elif not old_name:
        if (not projects_df.empty) and (projects_df['name'] == new_name).any():
            return jsonify({'success': False, 'message': '이미 존재하는 프로젝트명'})
        from datetime import datetime
        new_row = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'name': new_name,
            'description': '',
            'start_date': '',
            'end_date': '',
            'status': '진행중',
            'participants': '',
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'color': color
        }
        # DataFrame이 비어 있으면 컬럼 지정
        if projects_df.empty:
            columns = ['id','name','description','start_date','end_date','status','participants','created_date','color']
            projects_df = pd.DataFrame([new_row], columns=columns)
        else:
            projects_df = pd.concat([projects_df, pd.DataFrame([new_row])], ignore_index=True)
    # 저장
    csv_manager.write_csv('projects.csv', projects_df)
    return jsonify({'success': True})
