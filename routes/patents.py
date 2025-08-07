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
            'registration_number': p.registration_number,
            'application_date': p.application_date.strftime('%Y-%m-%d') if p.application_date else '',
            'status': p.status,
            'inventors': p.inventors,
            'description': p.description,
            'patent_office': p.patent_office,

            'main_inventor': p.main_inventor,
            'co_inventors': p.co_inventors,
            'application_draft_link': p.application_draft_link,
            'prior_art_report_link': p.prior_art_report_link,
            'application_form_link': p.application_form_link,
            'application_review_link': p.application_review_link,
            'office_action_link': p.office_action_link,
            'response_link': p.response_link,
            'amendment_link': p.amendment_link,
            'publication_link': p.publication_link,
            'registration_review_link': p.registration_review_link,
            'notes': p.notes,
            'created_date': p.created_date.strftime('%Y-%m-%d') if p.created_date else ''
        })
    return render_template('patents/list.html', patents=patents_list)

@patents_bp.route('/add', methods=['POST'])
def add_patent():
    try:
        # 필수 필드 검증
        if not request.form.get('title'):
            flash('특허명은 필수 입력 항목입니다.', 'error')
            return redirect(url_for('patents.patent_list'))

        # 발명자 정보 처리
        main_inventor = request.form.get('main_inventor', '')
        co_inventors_list = request.form.getlist('co_inventors')
        co_inventors_list = [co for co in co_inventors_list if co.strip()]
        
        # 발명자들을 하나의 문자열로 결합
        all_inventors = [main_inventor] + co_inventors_list
        inventors_str = ', '.join([inv for inv in all_inventors if inv.strip()])

        patent = Patent(
            patent_id=datetime.now().strftime('%Y%m%d%H%M%S'),
            title=request.form.get('title'),
            application_number=request.form.get('application_number'),
            registration_number=request.form.get('registration_number', ''),
            application_date=parse_date(request.form.get('application_date')),
            publication_date=parse_date(request.form.get('publication_date')),
            status=request.form.get('status', '출원 준비 중'),
            patent_office=request.form.get('patent_office', '특허청'),
            main_inventor=main_inventor,
            main_inventor_share=request.form.get('main_inventor_share'),
            co_inventors=', '.join(co_inventors_list),
            inventors=inventors_str,
            description=request.form.get('description'),
            application_draft_link=request.form.get('application_draft_link'),
            prior_art_report_link=request.form.get('prior_art_report_link'),
            application_form_link=request.form.get('application_form_link'),
            application_review_link=request.form.get('application_review_link'),
            office_action_link=request.form.get('office_action_link'),
            response_link=request.form.get('response_link'),
            amendment_link=request.form.get('amendment_link'),
            publication_link=request.form.get('publication_link'),
            registration_review_link=request.form.get('registration_review_link'),
            notes=request.form.get('notes'),
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
        
        # 필수 필드 검증
        if not request.form.get('title'):
            flash('특허명은 필수 입력 항목입니다.', 'error')
            return redirect(url_for('patents.patent_list'))

        # 발명자 정보 처리
        main_inventor = request.form.get('main_inventor', '')
        co_inventors_list = request.form.getlist('co_inventors')
        co_inventors_list = [co for co in co_inventors_list if co.strip()]
        
        # 발명자들을 하나의 문자열로 결합
        all_inventors = [main_inventor] + co_inventors_list
        inventors_str = ', '.join([inv for inv in all_inventors if inv.strip()])

        patent.title = request.form.get('title')
        patent.application_number = request.form.get('application_number')
        patent.registration_number = request.form.get('registration_number', '')
        patent.application_date = parse_date(request.form.get('application_date'))
        patent.status = request.form.get('status')
        patent.patent_office = request.form.get('patent_office')
        patent.main_inventor = main_inventor
        patent.main_inventor_share = request.form.get('main_inventor_share')
        patent.co_inventors = ', '.join(co_inventors_list)
        patent.inventors = inventors_str
        patent.description = request.form.get('description')
        patent.application_draft_link = request.form.get('application_draft_link')
        patent.prior_art_report_link = request.form.get('prior_art_report_link')
        patent.application_form_link = request.form.get('application_form_link')
        patent.application_review_link = request.form.get('application_review_link')
        patent.office_action_link = request.form.get('office_action_link')
        patent.response_link = request.form.get('response_link')
        patent.amendment_link = request.form.get('amendment_link')
        patent.publication_link = request.form.get('publication_link')
        patent.registration_review_link = request.form.get('registration_review_link')
        patent.notes = request.form.get('notes')
        
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



