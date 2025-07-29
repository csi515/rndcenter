from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from database import db, Chemical
from datetime import datetime
import uuid
import math

chemical_bp = Blueprint('chemical', __name__)

def safe_value(val):
    if val is None:
        return ''
    if isinstance(val, float) and math.isnan(val):
        return ''
    return str(val)

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        return None

@chemical_bp.route('/msds')
def msds_list():
    msds = Chemical.query.order_by(Chemical.created_date.desc()).all()
    msds_list = []
    for m in msds:
        msds_list.append({
            'id': m.chem_id,
            'chemical_name': m.chemical_name,
            'cas_number': m.cas_number,
            'manufacturer': m.manufacturer,
            'hazard_class': m.hazard_class,
            'storage_condition': m.storage_condition,
            'flash_point': m.flash_point,
            'exposure_limit': m.exposure_limit,
            'first_aid': m.first_aid,
            'disposal_method': m.disposal_method,
            'msds_file_link': m.msds_file_link,
            'location': m.location,
            'quantity': m.quantity,
            'expiry_date': m.expiry_date.strftime('%Y-%m-%d') if m.expiry_date else '',
            'created_date': m.created_date.strftime('%Y-%m-%d') if m.created_date else ''
        })
    return render_template('chemical/msds.html', msds_list=msds_list)

@chemical_bp.route('/msds/add', methods=['POST'])
def add_msds():
    try:
        chem = Chemical(
            chem_id=str(uuid.uuid4()),
            chemical_name=request.form.get('chemical_name'),
            cas_number=request.form.get('cas_number', ''),
            manufacturer=request.form.get('manufacturer'),
            hazard_class=request.form.get('hazard_class'),
            storage_condition=request.form.get('storage_condition'),
            flash_point=request.form.get('flash_point', ''),
            exposure_limit=request.form.get('exposure_limit', ''),
            first_aid=request.form.get('first_aid', ''),
            disposal_method=request.form.get('disposal_method', ''),
            msds_file_link=request.form.get('msds_file_link', ''),
            location=request.form.get('location', ''),
            quantity=request.form.get('quantity', ''),
            expiry_date=parse_date(request.form.get('expiry_date')),
            created_date=datetime.now()
        )
        db.session.add(chem)
        db.session.commit()
        flash('화학물질 정보가 성공적으로 추가되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'화학물질 정보 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('chemical.msds_list'))

@chemical_bp.route('/msds/update/<id>', methods=['POST'])
def update_msds(id):
    try:
        chem = Chemical.query.filter_by(chem_id=id).first()
        if not chem:
        flash('수정할 데이터를 찾을 수 없습니다.', 'error')
        return redirect(url_for('chemical.msds_list'))
        chem.chemical_name = request.form.get('chemical_name')
        chem.cas_number = request.form.get('cas_number')
        chem.manufacturer = request.form.get('manufacturer')
        chem.hazard_class = request.form.get('hazard_class')
        chem.storage_condition = request.form.get('storage_condition')
        chem.flash_point = request.form.get('flash_point')
        chem.exposure_limit = request.form.get('exposure_limit')
        chem.first_aid = request.form.get('first_aid')
        chem.disposal_method = request.form.get('disposal_method')
        chem.msds_file_link = request.form.get('msds_file_link')
        chem.location = request.form.get('location')
        chem.quantity = request.form.get('quantity')
        chem.expiry_date = parse_date(request.form.get('expiry_date'))
        db.session.commit()
        flash('화학물질 정보가 성공적으로 수정되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'화학물질 정보 수정 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('chemical.msds_list'))

@chemical_bp.route('/msds/delete/<id>', methods=['POST'])
def delete_msds(id):
    try:
        chem = Chemical.query.filter_by(chem_id=id).first()
        if not chem:
        return {'success': False, 'message': '삭제할 데이터를 찾을 수 없습니다.'}
        db.session.delete(chem)
        db.session.commit()
        return {'success': True}
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'message': f'삭제 중 오류가 발생했습니다: {str(e)}'}
