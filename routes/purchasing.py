from flask import Blueprint, render_template, request, redirect, url_for, flash
from csv_manager import csv_manager
from datetime import datetime

purchasing_bp = Blueprint('purchasing', __name__)

@purchasing_bp.route('/requests')
def purchase_requests():
    requests_data = csv_manager.read_csv('purchase_requests.csv')
    requests_list = requests_data.to_dict('records') if not requests_data.empty else []
    return render_template('purchasing/requests.html', requests=requests_list)

@purchasing_bp.route('/requests/add', methods=['POST'])
def add_purchase_request():
    data = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'requester': request.form.get('requester'),
        'item_name': request.form.get('item_name'),
        'quantity': int(request.form.get('quantity', 1)),
        'unit_price': float(request.form.get('unit_price', 0)),
        'total_price': float(request.form.get('quantity', 1)) * float(request.form.get('unit_price', 0)),
        'supplier': request.form.get('supplier', ''),
        'category': request.form.get('category'),
        'urgency': request.form.get('urgency', '보통'),
        'reason': request.form.get('reason'),
        'budget_code': request.form.get('budget_code', ''),
        'status': '요청',
        'request_date': datetime.now().strftime('%Y-%m-%d'),
        'notes': request.form.get('notes', ''),
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.append_to_csv('purchase_requests.csv', data):
        flash('구매 요청이 성공적으로 등록되었습니다.', 'success')
    else:
        flash('구매 요청 등록 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('purchasing.purchase_requests'))

@purchasing_bp.route('/requests/update_status/<int:index>', methods=['POST'])
def update_request_status(index):
    data = {
        'status': request.form.get('status'),
        'approved_by': request.form.get('approved_by', ''),
        'approval_date': datetime.now().strftime('%Y-%m-%d') if request.form.get('status') == '승인' else '',
        'notes': request.form.get('notes', ''),
        'updated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if csv_manager.update_row('purchase_requests.csv', index, data):
        flash('구매 요청 상태가 성공적으로 업데이트되었습니다.', 'success')
    else:
        flash('구매 요청 상태 업데이트 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('purchasing.purchase_requests'))
