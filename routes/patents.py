from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from csv_manager import csv_manager
from datetime import datetime

patents_bp = Blueprint('patents', __name__)

@patents_bp.route('/list')
def patent_list():
    patents_data = csv_manager.read_csv('patents.csv')
    patents_list = patents_data.to_dict('records') if not patents_data.empty else []
    return render_template('patents/list.html', patents=patents_list)

@patents_bp.route('/add', methods=['POST'])
def add_patent():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'title': request.form.get('title'),
        'application_number': request.form.get('application_number'),
        'application_date': request.form.get('application_date'),
        'status': request.form.get('status', '출원'),
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


# 개선된 특허 관리 페이지
@patents_bp.route("/enhanced")
def enhanced_patent_list():
    """출원인별 지분율 관리가 포함된 개선된 특허 관리 페이지"""
    return render_template("patents/enhanced_list.html")

@patents_bp.route("/enhanced/api")
def enhanced_patents_api():
    """개선된 특허 관리용 API"""
    try:
        # 임시 데이터 - 실제로는 데이터베이스에서 로드
        patents_list = [
            {
                "id": 1,
                "title": "나노 입자를 이용한 암 치료 시스템",
                "status": "등록",
                "application_number": "10-2024-0001234",
                "registration_number": "10-2566789",
                "application_date": "2024-03-15",
                "registration_date": "2024-12-10",
                "field": "바이오메디컬",
                "abstract": "나노 입자를 이용하여 암세포를 선택적으로 타겟팅하는 혁신적인 치료 시스템",
                "applicants": [
                    {"name": "김연구", "affiliation": "연구소", "share_percentage": 60, "filing_reward": 300000, "registration_reward": 500000},
                    {"name": "이박사", "affiliation": "대학교", "share_percentage": 40, "filing_reward": 200000, "registration_reward": 300000}
                ]
            }
        ]
        return jsonify(patents_list)
    except Exception as e:
        return jsonify([])
