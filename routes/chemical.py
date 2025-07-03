from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from csv_manager import csv_manager
from datetime import datetime
import math

chemical_bp = Blueprint('chemical', __name__)

def safe_value(val):
    if val is None:
        return ''
    if isinstance(val, float) and math.isnan(val):
        return ''
    return str(val)

@chemical_bp.route('/msds')
def msds_list():
    msds_data = csv_manager.read_csv('msds.csv')
    msds_list = msds_data.to_dict('records') if not msds_data.empty else []
    # NaN/None을 모두 ''로 변환
    for msds in msds_list:
        for k, v in msds.items():
            msds[k] = safe_value(v)
    return render_template('chemical/msds.html', msds_list=msds_list)

@chemical_bp.route('/msds/add', methods=['POST'])
def add_msds():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'chemical_name': request.form.get('chemical_name'),
        'cas_number': request.form.get('cas_number', ''),
        'manufacturer': request.form.get('manufacturer'),
        'hazard_class': request.form.get('hazard_class'),
        'storage_condition': request.form.get('storage_condition'),
        'flash_point': request.form.get('flash_point', ''),
        'exposure_limit': request.form.get('exposure_limit', ''),
        'first_aid': request.form.get('first_aid', ''),
        'disposal_method': request.form.get('disposal_method', ''),
        'msds_file_link': request.form.get('msds_file_link', ''),
        'location': request.form.get('location', ''),
        'quantity': request.form.get('quantity', ''),
        'expiry_date': request.form.get('expiry_date', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('msds.csv', data):
        flash('화학물질 정보가 성공적으로 추가되었습니다.', 'success')
    else:
        flash('화학물질 정보 추가 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('chemical.msds_list'))

@chemical_bp.route('/msds/update/<id>', methods=['POST'])
def update_msds(id):
    msds_data = csv_manager.read_csv('msds.csv')
    if msds_data.empty:
        flash('수정할 데이터를 찾을 수 없습니다.', 'error')
        return redirect(url_for('chemical.msds_list'))
    row_index = msds_data.index[msds_data['id'].astype(str) == str(id)].tolist()
    if not row_index:
        flash('해당 ID의 데이터를 찾을 수 없습니다.', 'error')
        return redirect(url_for('chemical.msds_list'))
    index = row_index[0]
    data = {
        'id': id,
        'chemical_name': request.form.get('chemical_name'),
        'cas_number': request.form.get('cas_number'),
        'manufacturer': request.form.get('manufacturer'),
        'hazard_class': request.form.get('hazard_class'),
        'storage_condition': request.form.get('storage_condition'),
        'flash_point': request.form.get('flash_point'),
        'exposure_limit': request.form.get('exposure_limit'),
        'first_aid': request.form.get('first_aid'),
        'disposal_method': request.form.get('disposal_method'),
        'msds_file_link': request.form.get('msds_file_link'),
        'location': request.form.get('location'),
        'quantity': request.form.get('quantity'),
        'expiry_date': request.form.get('expiry_date'),
        'created_date': msds_data.at[index, 'created_date'] if 'created_date' in msds_data.columns else '',
        'updated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    if csv_manager.update_row('msds.csv', index, data):
        flash('화학물질 정보가 성공적으로 수정되었습니다.', 'success')
    else:
        flash('화학물질 정보 수정 중 오류가 발생했습니다.', 'error')
    return redirect(url_for('chemical.msds_list'))

@chemical_bp.route('/msds/delete/<id>', methods=['POST'])
def delete_msds(id):
    msds_data = csv_manager.read_csv('msds.csv')
    if msds_data.empty:
        return {'success': False, 'message': '삭제할 데이터를 찾을 수 없습니다.'}
    row_index = msds_data.index[msds_data['id'].astype(str) == str(id)].tolist()
    if not row_index:
        return {'success': False, 'message': '해당 ID의 데이터를 찾을 수 없습니다.'}
    index = row_index[0]
    if csv_manager.delete_row('msds.csv', index):
        return {'success': True}
    else:
        return {'success': False, 'message': '삭제 중 오류가 발생했습니다.'}
