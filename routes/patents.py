from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from csv_manager import csv_manager
from datetime import datetime

patents_bp = Blueprint('patents', __name__)

@patents_bp.route('/list')
def patent_list():
    patents_data = csv_manager.read_csv('patents.csv')
    patents_list = patents_data.to_dict('records') if not patents_data.empty else []
    # NaN, None, nan, undefined, Infinity 등 비정상 값 보정
    for row in patents_list:
        for k, v in row.items():
            if v in [None, 'NaN', 'nan', 'undefined', 'Infinity'] or (isinstance(v, float) and (v != v)):
                row[k] = ''
    return render_template('patents/list.html', patents=patents_list)

@patents_bp.route('/add', methods=['POST'])
def add_patent():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'title': request.form.get('title'),
        'application_number': request.form.get('application_number'),
        'registration_number': request.form.get('registration_number', ''),
        'application_date': request.form.get('application_date'),
        'status': request.form.get('status', '출원 준비 중'),
        'inventors': request.form.get('inventors'),
        'description': request.form.get('description'),
        'patent_office': request.form.get('patent_office', '특허청'),
        'link': request.form.get('link', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('patents.csv', data):
        flash('특허가 성공적으로 추가되었습니다.', 'success')
    else:
        flash('특허 추가 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('patents.patent_list'))

@patents_bp.route('/update/<int:index>', methods=['POST'])
def update_patent(index):
    data = {
        'title': request.form.get('title'),
        'application_number': request.form.get('application_number'),
        'registration_number': request.form.get('registration_number', ''),
        'application_date': request.form.get('application_date'),
        'status': request.form.get('status'),
        'inventors': request.form.get('inventors'),
        'description': request.form.get('description'),
        'patent_office': request.form.get('patent_office'),
        'link': request.form.get('link'),
        'updated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.update_row('patents.csv', index, data):
        flash('특허 정보가 성공적으로 수정되었습니다.', 'success')
    else:
        flash('특허 정보 수정 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('patents.patent_list'))

@patents_bp.route('/delete/<int:index>')
def delete_patent(index):
    if csv_manager.delete_row('patents.csv', index):
        flash('특허가 성공적으로 삭제되었습니다.', 'success')
    else:
        flash('특허 삭제 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('patents.patent_list'))



