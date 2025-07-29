from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from database import db, Patent
from datetime import datetime

patents_bp = Blueprint('patents', __name__)

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return None

@patents_bp.route('/list')
def patent_list():
    patents = Patent.query.order_by(Patent.created_date.desc()).all()
    patents_list = []
    for p in patents:
        patents_list.append({
            'id': p.id,
            'title': p.title,
            'application_number': p.application_number,
            'registration_number': getattr(p, 'registration_number', ''),
            'application_date': p.application_date.strftime('%Y-%m-%d') if p.application_date else '',
            'status': p.status,
            'inventors': p.inventors,
            'description': p.abstract,
            'patent_office': getattr(p, 'applicant', ''),
            'link': '',
            'created_date': p.created_date.strftime('%Y-%m-%d') if p.created_date else ''
        })
    return render_template('patents/list.html', patents=patents_list)

@patents_bp.route('/add', methods=['POST'])
def add_patent():
    try:
        patent = Patent(
            patent_id=datetime.now().strftime('%Y%m%d%H%M%S'),
            title=request.form.get('title'),
            application_number=request.form.get('application_number'),
            registration_number=request.form.get('registration_number', ''),
            application_date=parse_date(request.form.get('application_date')),
            publication_date=parse_date(request.form.get('publication_date')),
            grant_date=parse_date(request.form.get('grant_date')),
            registration_date=parse_date(request.form.get('registration_date')),
            priority_date=parse_date(request.form.get('priority_date')),
            status=request.form.get('status', '출원 준비 중'),
            inventors=request.form.get('inventors'),
            abstract=request.form.get('description'),
            applicant=request.form.get('patent_office', '특허청'),
            created_date=datetime.now()
        )
        db.session.add(patent)
        db.session.commit()
        flash('특허가 성공적으로 추가되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'특허 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('patents.patent_list'))

@patents_bp.route('/update/<int:patent_id>', methods=['POST'])
def update_patent(patent_id):
    try:
        patent = Patent.query.get(patent_id)
        if not patent:
            flash('특허를 찾을 수 없습니다.', 'error')
            return redirect(url_for('patents.patent_list'))
        patent.title = request.form.get('title')
        patent.application_number = request.form.get('application_number')
        patent.registration_number = request.form.get('registration_number', '')
        patent.application_date = parse_date(request.form.get('application_date'))
        patent.status = request.form.get('status')
        patent.inventors = request.form.get('inventors')
        patent.abstract = request.form.get('description')
        patent.applicant = request.form.get('patent_office')
        db.session.commit()
        flash('특허 정보가 성공적으로 수정되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'특허 정보 수정 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('patents.patent_list'))

@patents_bp.route('/delete/<int:patent_id>')
def delete_patent(patent_id):
    try:
        patent = Patent.query.get(patent_id)
        if not patent:
            flash('특허를 찾을 수 없습니다.', 'error')
            return redirect(url_for('patents.patent_list'))
        db.session.delete(patent)
        db.session.commit()
        flash('특허가 성공적으로 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'특허 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('patents.patent_list'))



