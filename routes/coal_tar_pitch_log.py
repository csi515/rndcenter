from flask import Blueprint, render_template, request, jsonify
from app import db, CoalTarPitchLog
from datetime import datetime

coal_log_bp = Blueprint('coal_log', __name__)

@coal_log_bp.route('/coal-tar-pitch-log')
def coal_log_page():
    # 검색/필터
    search = request.args.get('search', '')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    query = CoalTarPitchLog.query
    if search:
        query = query.filter(CoalTarPitchLog.user.contains(search))
    if date_from:
        query = query.filter(CoalTarPitchLog.used_at >= date_from)
    if date_to:
        query = query.filter(CoalTarPitchLog.used_at <= date_to)
    logs = query.order_by(CoalTarPitchLog.used_at.desc()).all()
    return render_template('coal_tar_pitch_log/list.html', logs=logs)

@coal_log_bp.route('/coal-tar-pitch-log/add', methods=['POST'])
def add_coal_log():
    data = request.form
    log = CoalTarPitchLog(
        user=data.get('user'),
        material=data.get('material', '콜타르피치 휘발물'),
        used_at=datetime.strptime(data.get('used_at'), '%Y-%m-%dT%H:%M'),
        location=data.get('location'),
        work_content=data.get('work_content'),
        amount=data.get('amount'),
        ppe=(data.get('ppe') == 'on'),
        process_condition=data.get('process_condition'),
        exposure_reaction=data.get('exposure_reaction'),
        action_note=data.get('action_note'),
        writer=data.get('writer'),
        manager_sign=data.get('manager_sign')
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'success': True})

@coal_log_bp.route('/coal-tar-pitch-log/update/<int:log_id>', methods=['POST'])
def update_coal_log(log_id):
    log = CoalTarPitchLog.query.get_or_404(log_id)
    data = request.form
    log.user = data.get('user')
    log.material = data.get('material', '콜타르피치 휘발물')
    log.used_at = datetime.strptime(data.get('used_at'), '%Y-%m-%dT%H:%M')
    log.location = data.get('location')
    log.work_content = data.get('work_content')
    log.amount = data.get('amount')
    log.ppe = (data.get('ppe') == 'on')
    log.process_condition = data.get('process_condition')
    log.exposure_reaction = data.get('exposure_reaction')
    log.action_note = data.get('action_note')
    log.writer = data.get('writer')
    log.manager_sign = data.get('manager_sign')
    db.session.commit()
    return jsonify({'success': True})

@coal_log_bp.route('/coal-tar-pitch-log/delete/<int:log_id>', methods=['POST'])
def delete_coal_log(log_id):
    log = CoalTarPitchLog.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    return jsonify({'success': True}) 